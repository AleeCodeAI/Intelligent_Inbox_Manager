# Eval Summary — 20260602_214033

## Overall
| Metric | Value |
|--------|-------|
| Total Samples | 20 |
| Passed | 19 |
| Failed | 1 |
| Pass Rate | 95.0% |
| Avg Confidence | 0.936 |

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
### `msg_205` — Free meditation event this weekend (also maybe AI work?)
- **Expected:** NON_BUSINESS
- **Predicted:** BASIC
- **Confidence:** 0.930
- **Reasoning:** The email contains a clear business question asking if the recipient provides AI consulting, which is a request for information about services, fitting the BASIC category. The invitation to a free meditation event is non‑business, but the presence of the business inquiry makes BASIC the appropriate classification.
- **Body Preview:** Hi! I'm hosting a free community meditation on Saturday at 10am - you should come! Also random question: do you do any AI consulting? My friend mentioned you might. No big project or anything, just idle curiosity. Hope to see you at the event!


## Confident Failures (confidence ≥ 0.8)
**1 high-confidence failures**

| Gmail ID | Expected | Predicted | Confidence |
|----------|----------|------------|------------|
| `msg_205` | NON_BUSINESS | BASIC | 0.930 |