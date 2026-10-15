# GIT WORKFLOW — 3 branches, merge at the end

## Why this is safe
Every person owns different files (see `ARCHITECTURE.md`). The skeleton on `main` already runs with stubs. Branches never touch the same file, so merges produce no conflicts.

| Branch | Person | Files they change |
|---|---|---|
| `feat/a-ai-pipeline` | A | `llm.py`, `pipeline.py`, `prompts/ranker.md`, `data/sample_items.json`, `data/llm_output.json` |
| `feat/b-review-station` | B | `storage.py`, `ui_review.py` |
| `feat/c-newsletter` | C | `newsletter.py`, `ui_newsletter.py`, `app.py`, `tests/`, `DEMO.md` |

**Do not edit:** `CONTRACT.md`, `config.py`, `requirements.txt`, `AGENTS.md` (agree out loud first, then ONE person changes it on `main`).

## Minute 0 (once)
Whoever owns the repo:
```bash
git init && git add . && git commit -m "chore: skeleton"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
git branch feat/a-ai-pipeline && git branch feat/b-review-station && git branch feat/c-newsletter
git push origin --all
```
(If you received the zip with `.git` inside, the branches already exist locally: just add the remote and `git push origin --all`.)

## Each person, once
```bash
git clone <your-repo-url> && cd ai-pulse
git checkout feat/a-ai-pipeline        # or feat/b-review-station / feat/c-newsletter
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt && cp .env.example .env
streamlit run app.py                    # should already run with stubs
```

## While building
```bash
git add -A && git commit -m "A: <what>" && git push origin HEAD
```
Every 15-20 minutes, push. Nobody else needs your branch until a checkpoint.

## Checkpoint 1 (about 2:15): integration test
Merge captain (pick one in advance, default Person A) runs:
```bash
git checkout main && git pull
git merge --no-ff origin/feat/a-ai-pipeline -m "merge: A"
git merge --no-ff origin/feat/b-review-station -m "merge: B"
git merge --no-ff origin/feat/c-newsletter -m "merge: C"
streamlit run app.py
git push origin main
```
Then everyone syncs their branch to catch the other two people's work:
```bash
git checkout feat/<yours> && git merge origin/main && git push origin HEAD
```
Fix integration bugs on your own branch (in your own files), push, repeat.

## Final merge (about 2:40): freeze
1. Everyone pushes their last commit and says "pushed" out loud.
2. Merge captain repeats the three `git merge --no-ff` commands above on `main`.
3. Run the app with Wi-Fi off. Run `tests/TEST_CASES.md`.
4. Tag it: `git tag demo-ready && git push --tags`.
5. **From here, only bug fixes that break the demo, one person at a time.**

## If a conflict happens anyway
```bash
git status                # see conflicted files
# open the file, keep the OWNER's version for owner-only files
git checkout --theirs <file>   # or --ours, depending on direction
git add <file> && git commit
```
The owner of that file decides. Don't resolve other people's files by guessing.

## Golden rules
- Never force-push. Never rebase shared branches.
- Never commit `.env` or `data/state.json` (already in `.gitignore`).
- If `main` breaks on demo day, `git checkout demo-ready` is your safety net.
