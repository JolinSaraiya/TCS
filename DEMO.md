# DEMO — 5 minutes (Problem → Approach → Solution → Output → Proof → Learning)

## Before you walk on stage
- [ ] `USE_CACHE_ONLY=true`, app already running, Wi-Fi irrelevant
- [ ] `data/state.json` deleted for a clean start
- [ ] Browser zoom set so cards are readable from the back
- [ ] One person drives, one talks, one watches the clock
- [ ] Hand-labeled top-5 match number written on a sticky note

## Script
| Time | Step | Say | Show |
|---|---|---|---|
| 0:00-0:30 | **Problem** | "A club coordinator spends hours every week finding, vetting, and summarizing AI news." | Title slide |
| 0:30-1:00 | **Approach** | "Approved sources go through one AI pass that scores, filters, and summarizes. A human approves everything." | Flow diagram from `ARCHITECTURE.md` |
| 1:00-2:00 | **Solution** | "Here's the coordinator's workflow." | Load app, point to the **cached** badge. Say it out loud: "this is cached output for reliability." |
| 2:00-3:30 | **Output** | "Every card shows Decision, Reason, Next Action." | Approve 3, edit one summary, reject one, show Publish gate flipping to enabled, toggle weekly/monthly |
| 3:30-4:30 | **Proof** | "Now the edge cases." | Filtered earnings item with its reason, merged duplicate, missing-date flag, near-miss pair NOT merged |
| 4:30-5:00 | **Learning** | "Limitations and result." | "AI matched X of 5 of our hand-labeled top items. LLMs can err, relevance is subjective, reading time is estimated, sources are hand-curated. Next: live RSS and scheduled weekly drafts." |

## Likely judge questions
| Question | Answer |
|---|---|
| Where's the AI? | One batched LLM call does scoring, filtering, dedupe, summaries, and headline. The score breakdown makes it explainable. |
| How do you stop hallucination? | Summaries are restricted to the stored excerpt, max 30 words, and every item is human-reviewed. |
| What if the API is down? | Cached output with an honest badge; shown in test case 7. |
| Is this live data? | Prototype uses cached content as the problem statement allows; live RSS is the next step. |
| How do you know it picks the right items? | We hand-labeled an ideal top 5 and measured the match. |
| How would it scale? | Add feeds, schedule the pipeline (n8n or cron), keep the same review step. |

## Do NOT
- Click anything you haven't clicked in rehearsal
- Call a cached run "live"
- Open code unless asked
