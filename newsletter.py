"""Person C owns this file. Window, cap, publish gate, exports. See CONTRACT.md sections 6, 7."""
import html
from datetime import date

from config import (AS_OF, MIN_ITEMS_TO_PUBLISH, MONTHLY_MAX_ITEMS, MONTHLY_WINDOW_DAYS,
                    WEEKLY_MAX_ITEMS, WEEKLY_WINDOW_DAYS)


def _in_window(published, days: int) -> bool:
    if not published:
        return False
    try:
        delta = (date.fromisoformat(AS_OF) - date.fromisoformat(published)).days
        return 0 <= delta <= days
    except (ValueError, TypeError):
        return False


def build_newsletter(state: dict, period: str) -> dict:
    days, cap = ((WEEKLY_WINDOW_DAYS, WEEKLY_MAX_ITEMS) if period == "weekly"
                 else (MONTHLY_WINDOW_DAYS, MONTHLY_MAX_ITEMS))
    pool = [i for i in state.get("items", [])
            if i.get("status") == "approved" and not i.get("duplicate_of")
            and _in_window(i.get("published"), days)]
    pool.sort(key=lambda i: i.get("total", 0), reverse=True)
    chosen = pool[:cap]
    ok = len(chosen) >= MIN_ITEMS_TO_PUBLISH
    
    msg = ""
    if not ok:
        count = len(chosen)
        needed = MIN_ITEMS_TO_PUBLISH - count
        msg = f"Publish gate locked: Approve at least {needed} more item{'s' if needed > 1 else ''} published within the last {days} days ({period}). Currently have {count}/{MIN_ITEMS_TO_PUBLISH} approved."

    return {
        "headline": state.get("headline", "") or "AI Pulse for Engineers",
        "challenge": state.get("challenge", ""),
        "period": period,
        "as_of": AS_OF,
        "items": chosen,
        "publishable": ok,
        "message": msg,
    }


def export_markdown(nl: dict) -> str:
    headline = nl.get("headline") or "AI Pulse"
    lines = [
        f"# {headline}",
        f"*{nl.get('period', 'weekly').title()} edition · As of {nl.get('as_of', AS_OF)}*",
        "",
        "---",
        "",
    ]
    for n, i in enumerate(nl.get("items", []), 1):
        lines += [
            f"## {n}. [{i['title']}]({i['url']})",
            f"**Category:** `{i['topic']}` | **Reading time:** ~{i.get('reading_time_min', 1)} min (est.) | **Source:** {i['source']}",
            "",
            i.get("summary", ""),
            "",
            f"**Why it matters:** {i.get('why_it_matters', '')}",
        ]
        if i.get("target_audience"):
            lines.append(f"\n**Target audience:** {i['target_audience']}")
        if i.get("what_to_do_next"):
            lines.append(f"\n**What to do next:** {i['what_to_do_next']}")
        lines += [
            "",
            f"🔗 [Read the original story on {i['source']}]({i['url']})",
            "",
            "---",
            "",
        ]
    if nl.get("challenge"):
        lines += [
            "### ⚡ 5-Minute Student Challenge",
            f"> {nl['challenge']}",
            "",
        ]
    return "\n".join(lines)


def export_html(nl: dict) -> str:
    e = html.escape
    headline = e(nl.get("headline") or "AI Pulse")
    period = e(nl.get("period", "weekly").title())
    as_of = e(nl.get("as_of", AS_OF))

    items_html = []
    for n, i in enumerate(nl.get("items", []), 1):
        title = e(i.get("title", ""))
        url = e(i.get("url", "#"))
        topic = e(i.get("topic", "AI"))
        mins = i.get("reading_time_min", 1)
        source = e(i.get("source", ""))
        summary = e(i.get("summary", ""))
        why = e(i.get("why_it_matters", ""))
        aud = e(i.get("target_audience", ""))
        nxt = e(i.get("what_to_do_next", ""))

        extra_parts = []
        if aud:
            extra_parts.append(f"<p style=\"margin: 4px 0; color: #475569;\"><strong>Target Audience:</strong> {aud}</p>")
        if nxt:
            extra_parts.append(f"<p style=\"margin: 4px 0; color: #0284c7;\"><strong>What to do next:</strong> {nxt}</p>")

        extras = "".join(extra_parts)

        items_html.append(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
          <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; color: #6366f1; letter-spacing: 0.05em; margin-bottom: 6px;">
            {topic} &bull; ~{mins} min read &bull; {source}
          </div>
          <h2 style="margin: 0 0 12px 0; font-size: 19px; line-height: 1.4;">
            <a href="{url}" style="color: #0f172a; text-decoration: none;">{n}. {title}</a>
          </h2>
          <p style="margin: 0 0 12px 0; color: #334155; line-height: 1.6; font-size: 15px;">{summary}</p>
          <div style="background: #f8fafc; border-left: 3px solid #6366f1; padding: 10px 14px; margin-bottom: 12px; border-radius: 0 6px 6px 0;">
            <strong style="color: #1e293b;">Why it matters:</strong>
            <span style="color: #475569;"> {why}</span>
          </div>
          {extras}
          <div style="margin-top: 14px;">
            <a href="{url}" style="display: inline-block; font-size: 13px; font-weight: 600; color: #4f46e5; text-decoration: none;">Read full story &rarr;</a>
          </div>
        </div>
        """)

    challenge_html = ""
    if nl.get("challenge"):
        c_text = e(nl["challenge"])
        challenge_html = f"""
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%); border: 1px solid #c7d2fe; border-radius: 8px; padding: 20px; margin-top: 24px;">
          <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #3730a3; display: flex; align-items: center;">
            ⚡ 5-Minute Student Challenge
          </h3>
          <p style="margin: 0; color: #1e1b4b; line-height: 1.5; font-size: 14px;">{c_text}</p>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{headline}</title>
</head>
<body style="margin: 0; padding: 30px 15px; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <div style="max-width: 640px; margin: 0 auto;">
    <div style="text-align: center; margin-bottom: 28px;">
      <span style="background: #e0e7ff; color: #3730a3; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 12px; text-transform: uppercase;">
        {period} Edition &bull; {as_of}
      </span>
      <h1 style="color: #0f172a; margin: 12px 0 6px 0; font-size: 26px; font-weight: 800; letter-spacing: -0.02em;">{headline}</h1>
      <p style="color: #64748b; font-size: 14px; margin: 0;">Curated AI intelligence for engineering students and future developers</p>
    </div>
    
    {"".join(items_html)}
    
    {challenge_html}

    <div style="text-align: center; margin-top: 30px; color: #94a3b8; font-size: 12px;">
      <p>Curated with AI Pulse &bull; Reviewed & approved by club coordinators</p>
    </div>
  </div>
</body>
</html>"""
