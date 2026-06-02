# Eval Summary — 20260601_231838

## Overall
| Metric | Value |
|--------|-------|
| Total Samples | 20 |
| Passed | 19 |
| Failed | 1 |
| Pass Rate | 95.0% |
| Avg Confidence | 0.942 |

## Per-Class Breakdown
| Class | Total | Passed | Pass Rate |
|-------|-------|--------|-----------|
| BASIC | 7 | 7 | 100.0% |
| NON_BUSINESS | 6 | 5 | 83.3% |
| PRIORITY | 7 | 7 | 100.0% |

## Confusion Matrix
| Actual \ Predicted | BASIC | NON_BUSINESS | PRIORITY |
|---|---|---|---|
| BASIC | 7 | 0 | 0 |
| NON_BUSINESS | 1 | 5 | 0 |
| PRIORITY | 0 | 0 | 7 |

## Failed Cases
### `msg_203` — Your newsletter - loved the AI ethics piece!
- **Expected:** NON_BUSINESS
- **Predicted:** BASIC
- **Confidence:** 0.850
- **Reasoning:** The email primarily compliments a newsletter (personal) but also mentions a potential future consulting budget of $10k, which is an inquiry about a possible business opportunity. It lacks a concrete meeting request, deadline, or confirmed high‑value project, so it does not meet PRIORITY criteria. The business interest makes it a BASIC inquiry rather than purely NON_BUSINESS.
- **Body Preview:** Hey! Just wanted to say I really enjoyed your latest newsletter on AI ethics. That said, I'm also part of a nonprofit that might have a $10k budget for some consulting next quarter. But no pressure at all - mostly just wanted to say keep up the great writing!


## Confident Failures (confidence ≥ 0.8)
**1 high-confidence failures**

| Gmail ID | Expected | Predicted | Confidence |
|----------|----------|------------|------------|
| `msg_203` | NON_BUSINESS | BASIC | 0.850 |