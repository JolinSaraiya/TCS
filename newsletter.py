"""Person C owns this file. Window, cap, publish gate, exports. See CONTRACT.md sections 6, 7."""
import html
from datetime import date

from config import (AS_OF, MIN_ITEMS_TO_PUBLISH, MONTHLY_MAX_ITEMS, MONTHLY_WINDOW_DAYS,
                    WEEKLY_MAX_ITEMS, WEEKLY_WINDOW_DAYS)


def _in_window(published, days: int) -> bool:
    if not published:
        return False
    delta = (date.fromisoformat(AS_OF) - date.fromisoformat(published)).days
    return 0 <= delta <= days


def build_newsletter(state: dict, period: str) -> dict:
    days, cap = ((WEEKLY_WINDOW_DAYS, WEEKLY_MAX_ITEMS) if period == "weekly"
                 else (MONTHLY_WINDOW_DAYS, MONTHLY_MAX_ITEMS))
    pool = [i for i in state.get("items", [])
            if i.get("status") == "approved" and not i.get("duplicate_of")
            and _in_window(i.get("published"), days)]
    pool.sort(key=lambda i: i.get("total", 0), reverse=True)
    chosen = pool[:cap]
    ok = len(chosen) >= MIN_ITEMS_TO_PUBLISH
    return {
        "headline": state.get("headline", ""), "challenge": state.get("challenge", ""),
        "period": period, "as_of": AS_OF, "items": chosen, "publishable": ok,
        "message": "" if ok else f"Approve at least {MIN_ITEMS_TO_PUBLISH} items in this window to publish.",
    }


def export_markdown(nl: dict) -> str:
    lines = [f"# {nl['headline'] or 'AI Pulse'}", f"*{nl['period'].title()} edition · {nl['as_of']}*", ""]
    for n, i in enumerate(nl["items"], 1):
        lines += [f"## {n}. {i['title']}", f"**{i['topic']}** · ~{i['reading_time_min']} min (est.)", "",
                  i["summary"], "", f"**Why it matters:** {i['why_it_matters']}", "",
                  f"Source: {i['source']} — [Read more]({i['url']})", ""]
    if nl.get("challenge"):
        lines += ["---", f"**5-minute challenge:** {nl['challenge']}"]
    return "\n".join(lines)


def export_html(nl: dict) -> str:
    e = html.escape
    parts = [f"<h1>{e(nl['headline'] or 'AI Pulse')}</h1>",
             f"<p><em>{e(nl['period'].title())} edition · {e(nl['as_of'])}</em></p>"]
    for n, i in enumerate(nl["items"], 1):
        parts.append(
            f"<h2>{n}. {e(i['title'])}</h2><p><strong>{e(i['topic'])}</strong> · ~{i['reading_time_min']} min (est.)</p>"
            f"<p>{e(i['summary'])}</p><p><strong>Why it matters:</strong> {e(i['why_it_matters'])}</p>"
            f"<p>Source: {e(i['source'])} — <a href=\"{e(i['url'])}\">Read more</a></p>")
    if nl.get("challenge"):
        parts.append(f"<hr><p><strong>5-minute challenge:</strong> {e(nl['challenge'])}</p>")
    return ("<html><body style=\"font-family:sans-serif;max-width:640px;margin:2rem auto\">"
            + "".join(parts) + "</body></html>")
