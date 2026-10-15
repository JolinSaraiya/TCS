# AI Pulse — Automated Student Newsletter Generator

TCS Tech Day @ VESIT · Problem P7 · 90-minute hackathon · Team of 3

> Approved AI sources → one AI pass (filter, score, summarize) → coordinator reviews → 3-5 item newsletter → export.

## Read these first (in order)
1. `PRD.md` — what we're building and why
2. `CONTRACT.md` — **data contract. Field names are law.**
3. `ARCHITECTURE.md` — files, modules, who owns what
4. `AGENTS.md` — rules for any AI coding tool (paste into Cursor/Claude Code/Copilot)
5. `GIT_WORKFLOW.md` — branches and merge order
6. `TASKS.md` — roles, timeline, checklists
7. `tests/TEST_CASES.md` and `DEMO.md` — proof + 5-minute script

## Setup (5 min, do it together at minute 0)

```bash
# 1. Python 3.10+
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Keys
cp .env.example .env             # then paste your key into .env

# 3. Run
streamlit run app.py
```

## Repo layout

```
ai-pulse/
├── app.py              # Streamlit shell, tab wiring   (Person C)
├── ui_review.py        # Review Station tab            (Person B)
├── ui_newsletter.py    # Newsletter + Export tabs      (Person C)
├── pipeline.py         # LLM pass, validation, cache   (Person A)
├── llm.py              # one function: call_llm()      (Person A)
├── newsletter.py       # windowing, assembly, export   (Person C)
├── storage.py          # load/save state.json          (Person B)
├── config.py           # constants, AS_OF date         (shared, rarely edited)
├── prompts/ranker.md   # the batched prompt            (Person A)
├── data/
│   ├── sample_items.json   # 15 hand-written items     (Person A)
│   ├── llm_output.json     # saved good LLM result = fallback (Person A)
│   └── state.json          # runtime state (gitignored)
└── tests/TEST_CASES.md
```

## Golden rules
- **Demo must work with zero internet.** Cached output is the default path.
- **Never rename a field** from `CONTRACT.md` without all three agreeing out loud.
- **Own your files.** Don't edit someone else's file; ask them.
- **No new features** until every box in `TASKS.md` "MVP" is ticked.
