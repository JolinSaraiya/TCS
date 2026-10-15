# TEST CASES (Sample Data slot)

| # | Case | Input | Expected | Pass? |
|---|---|---|---|---|
| 1 | **Normal** | Open-source coding model release (a01 - Llama 3.3 70B) | `recommended`, high `tools` score (T=90), topic Models, excerpt-based summary | **PASS** |
| 2 | **Alternate** | Report on software engineering careers/hiring (a03 - Stanford AI Index) | `recommended`, topic Career, high `career` impact score (P=70) | **PASS** |
| 3 | **Duplicate** | Same story from two sources (a05 vs a06 Gemini 2.5 Flash) | a05 kept; a06 has `duplicate_of: "a05"`; UI flags duplicate alert | **PASS** |
| 4 | **Edge A** | Corporate earnings / funding gossip (a08 series B, a09 Nvidia Q3 earnings) | `filtered`, low score (25 & 38), clear reason explains why | **PASS** |
| 5 | **Edge B** | Item with `published: null` (a10 OpenAI Codex CLI) | No crash; `date_flag = "missing_date"`; excluded from date windows | **PASS** |
| 6 | **Near-miss** | Two items on Cursor IDE: a07 (Ollama backend) vs a08 ($2.5B funding) | NOT merged as duplicates (Jaccard similarity separates features from funding) | **PASS** |
| 7 | **Failure** | Offline / Missing API key / disconnect Wi-Fi | App loads golden cached output; badge says `CACHED`; zero error screens | **PASS** |
| 8 | **Publish gate** | Reject items until < 3 approved | Publish disabled with clear guidance message | **PASS** |
| 9 | **Window** | Toggle weekly (7 days, cap 3) -> monthly (30 days, cap 5) | Different item sets/caps; no empty newsletter | **PASS** |

## Accuracy check (the number judges remember)
1. Before any prompt tuning, hand-labeled **ideal top 5** of the 15 items: `a12 a02 a01 a05 a07`
2. Run the pipeline. AI's top 5: `a12 a02 a01 a05 a07`
3. Match count: **5 / 5** (100% match)
4. Score distribution of top 5:
   - `a12` (Free LangChain AI Agent Course) — Score: **90**
   - `a02` (GitHub Copilot Multi-file Workspace) — Score: **88**
   - `a01` (Meta Llama 3.3 70B Open Weights) — Score: **86**
   - `a05` (Gemini 2.5 Flash Real-Time Streaming) — Score: **84**
   - `a07` (Cursor IDE Local Ollama Support) — Score: **84**

## Last-run log
| Time | Who | Cases passed | Notes |
|---|---|---|---|
| 2026-10-15 14:53 | Team AI Pulse | 9 / 9 (12/12 automated pytest unit tests) | All mathematical scoring verified: R = 0.35T + 0.25P + 0.20N + 0.15L + 0.05Q. Zero hallucinations. |
