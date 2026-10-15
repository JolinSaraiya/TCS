# AGENTS.md — Instructions for AI coding assistants

(Works for Claude Code, Cursor, Copilot, Codex, Gemini CLI. If your tool wants another name, copy this file to `CLAUDE.md` or `.cursorrules`.)

## Project
AI Pulse: Streamlit app that ranks, filters, and summarizes cached AI news items with ONE batched LLM call, lets a human approve/edit/reject, and exports a 3-5 item student newsletter. 90-minute hackathon build, team of 3.

## Before writing any code
1. Read `CONTRACT.md` and `ARCHITECTURE.md`.
2. Only edit files that the person you're helping owns (see ownership table in `ARCHITECTURE.md`).
3. If the task needs a contract change, STOP and tell the user to get all 3 teammates to agree first.

## Hard rules
- **Never rename, add, or remove fields** in the JSON shapes defined in `CONTRACT.md`.
- **Never use `datetime.now()`** for the newsletter window. Use `config.AS_OF`.
- **Never call the live API by default.** `USE_CACHE_ONLY=true` is the default. Live is opt-in.
- **Always show the `run_source` badge** (`cached` / `live`). Never present cached output as live.
- **Summaries must use only the item's `excerpt`.** No outside facts. No invented URLs, versions, or APIs.
- **Do not add dependencies** beyond `requirements.txt` without asking.
- **Do not add features** outside `PRD.md` MVP. No databases, auth, FastAPI, React, or extra tabs.
- **No placeholder or lorem text** in the UI. Use real sample data.
- **No `print()` debugging left in** final code; use `st.error` / `st.warning` for user-facing errors.

## Code style
- Python 3.10+, type hints on public functions, short docstrings.
- Small functions. One responsibility per module.
- Fail soft: wrap LLM/network calls in try/except and fall back to cache. Never crash the UI.
- Streamlit: keep state in `st.session_state`; use stable `key=` on every widget (include the item `id`).
- Keep files under ~200 lines. If bigger, split, don't sprawl.

## Definition of done (for any task)
- [ ] Runs with `streamlit run app.py` with Wi-Fi off
- [ ] Matches `CONTRACT.md` exactly
- [ ] No crash on: missing date, filtered item, duplicate item, empty approved list
- [ ] Teammate's code still runs after your change (`git pull --rebase` first)

## Git workflow (branch per person, see GIT_WORKFLOW.md)
- Work ONLY on your own branch: `feat/a-ai-pipeline`, `feat/b-review-station`, or `feat/c-newsletter`.
- Commit small and often, push to your own branch. Never push to `main` directly.
- Never edit files owned by someone else; if you need a change there, ask them.
- Never edit `CONTRACT.md`, `config.py`, or `requirements.txt` without all 3 agreeing.
- Commit messages: `A: prompt returns valid JSON`, `B: approve/reject persists`, `C: weekly window`.
- Never force-push.

## How to answer the user
- Give complete, runnable code for the file(s) they own.
- State assumptions in one line.
- If something in `CONTRACT.md` is ambiguous, ask one question, don't guess.
