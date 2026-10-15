# TEST CASES (Sample Data slot)

| # | Case | Input | Expected | Pass? |
|---|---|---|---|---|
| 1 | **Normal** | Open-source coding model release (e.g. a new open model usable by students) | `recommended`, high `tools` score, topic Models or Tools, summary uses only excerpt | |
| 2 | **Alternate** | Report on software engineering careers/hiring | `recommended`, topic Career, medium-high `career` score | |
| 3 | **Duplicate** | Same story from two sources | One kept; other has `duplicate_of` set; UI shows primary source with the other noted | |
| 4 | **Edge A** | Corporate earnings / funding gossip item | `filtered`, strong `noise_penalty`, reason explains why | |
| 5 | **Edge B** | Item with `published: null` | No crash; `date_flag = missing_date`; excluded from windowed newsletter | |
| 6 | **Near-miss** | Two items on the same product, different news (e.g. release vs pricing) | NOT merged as duplicates | |
| 7 | **Failure** | Remove API key / disconnect Wi-Fi | App loads cached output; badge says `cached`; no error screen | |
| 8 | **Publish gate** | Reject items until < 3 approved | Publish disabled with message | |
| 9 | **Window** | Toggle weekly -> monthly | Different item sets/caps; no empty newsletter | |

## Accuracy check (the number judges remember)
1. Before any prompt tuning, Person C hand-labels the **ideal top 5** of the 15 items (write ids here): `__ __ __ __ __`
2. Run the pipeline. AI's top 5: `__ __ __ __ __`
3. Match count: **__ / 5**
4. Report this honestly in the demo, even if it's 3/5.

## Last-run log
| Time | Who | Cases passed | Notes |
|---|---|---|---|
| | | | |
