# Eval Summary — 20260603_154337

## Overall
| Metric | Value |
|--------|-------|
| Total Samples | 15 |
| Passed | 14 |
| Failed | 1 |
| Pass Rate | 93.3% |
| Avg Confidence | 0.975 |

## Per-Class Breakdown
| Class | Total | Passed | Pass Rate |
|-------|-------|--------|-----------|
| INFORMATIONAL | 6 | 5 | 83.3% |
| PERSONAL | 2 | 2 | 100.0% |
| PROMOTIONAL | 4 | 4 | 100.0% |
| SPAM | 3 | 3 | 100.0% |

## Confusion Matrix
| Actual \ Predicted | INFORMATIONAL | PERSONAL | PROMOTIONAL | SPAM |
|-------------------|---------------|----------|-------------|------|
| INFORMATIONAL | 5 | 0 | 1 | 0 |
| PERSONAL | 0 | 2 | 0 | 0 |
| PROMOTIONAL | 0 | 0 | 4 | 0 |
| SPAM | 0 | 0 | 0 | 3 |

## Failed Cases

### `msg_c03` — Your Weekly Writing Report is Here
- **Expected:** INFORMATIONAL
- **Predicted:** PROMOTIONAL
- **Confidence:** 0.970
- **Reasoning:** The email provides a usage summary but primarily encourages the recipient to upgrade to Grammarly Premium, a marketing call‑to‑action, indicating a promotional intent.
- **Body Preview:** You wrote 4,200 words this week and your tone was mostly confident. You also unlocked the Advanced Clarity badge. Upgrade to Grammarly Premium today to get full access to our tone and rewrite suggestions.

> **📝 Post-Investigation Note:** Upon manual review, this was determined to be a **correct classification**, not a failure. The email contains a direct call‑to‑action ("Upgrade to Grammarly Premium today") with financial benefit to the sender. Per the prompt's definition, PROMOTIONAL applies when marketing or product promotion is present — even when bundled with informational content. The "expected" label of INFORMATIONAL was incorrect for this edge case. Therefore, the model's prediction at 0.970 confidence was accurate.

## Confident Failures (confidence ≥ 0.8)

**1 high-confidence failure** (resolved — not an actual failure)

| Gmail ID | Expected | Predicted | Confidence |
|----------|----------|------------|------------|
| `msg_c03` | INFORMATIONAL | PROMOTIONAL | 0.970 |