# Eval Summary — 20260602_221830

## Overall
| Metric | Value |
|--------|-------|
| Total Samples | 20 |
| Passed | 19 |
| Failed | 1 |
| Pass Rate | 95.0% |
| Avg Confidence | 0.945 |

## Per-Class Breakdown
| Class | Total | Passed | Pass Rate |
|-------|-------|--------|-----------|
| BASIC | 7 | 7 | 100.0% |
| NON_BUSINESS | 6 | 6 | 100.0% |
| PRIORITY | 7 | 6 | 85.7% |

## Confusion Matrix
| Actual \ Predicted | BASIC | NON_BUSINESS | PRIORITY |
|---|---|---|---|
| BASIC | 7 | 0 | 0 |
| NON_BUSINESS | 0 | 6 | 0 |
| PRIORITY | 1 | 0 | 6 |

## Failed Cases
### `msg_077` — Project Revisions: Introducing Document Summarization Layer
- **Expected:** PRIORITY
- **Predicted:** BASIC
- **Confidence:** 0.930
- **Reasoning:** The sender requests a scope expansion and addition of a new summarization layer for their data pipeline, which is a business request that requires a response. No meeting, high‑value, or legal/financial matters are mentioned, so it fits the BASIC category.
- **Body Preview:** Hi, we want to expand the scope of our live data pipeline. We would like to introduce a new information extraction and summarization layer to process data chunks before they undergo embedding retrieval.


## Confident Failures (confidence ≥ 0.8)
**1 high-confidence failures**

| Gmail ID | Expected | Predicted | Confidence |
|----------|----------|------------|------------|
| `msg_077` | PRIORITY | BASIC | 0.930 |