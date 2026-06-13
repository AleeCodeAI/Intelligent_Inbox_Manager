# BasicFlow Evaluation Documentation

## Overview

This document describes the evaluation strategy for the BasicFlow pipeline in the Intelligent Inbox Manager. The evaluation process was carried out in two stages: judge validation and live pipeline evaluation. The goal was to ensure that the LLM judge used for automated evaluation produces judgments aligned with human assessment before it was trusted to evaluate live pipeline output.

---

## Stage 1: Judge Validation

### Motivation

Before using an LLM as an automated judge, it must be verified that its verdicts are reliable. An unvalidated judge can produce systematically biased results — for example, being too lenient — which would make the evaluation meaningless.

### Step 1: Initial Pipeline Run

The BasicFlow pipeline was run against a set of 15 real test cases from the test dataset. Each case produced a generated email reply. These 15 examples, along with their original messages, RAG answers and generated reply, were collected as the base dataset for judge validation.

### Step 2: First Judge Run

The judge was run against all 15 pipeline-generated examples. The judge evaluated each case and produced a verdict of `GOOD` or `BAD` along with its reasoning. All 15 cases were judged as `GOOD`, meaning no failures were detected in this initial run.

### Step 3: Introducing Bad Examples

Since all 15 cases were judged as `GOOD`, there were no negative examples available to test whether the judge could correctly identify bad outputs. To address this, a separate JSONL file was constructed that included the original 15 cases along with 5 deliberately crafted bad examples. These bad examples were designed to represent realistic pipeline failures such as factual mismatch with the RAG answer, vague or unhelpful responses, and responses that ignored the original message.

### Step 4: Human Evaluation and Alignment Check

The judge was run against this extended dataset of 20 cases. An Excel report was then produced with the following columns for each case:

- Original message
- RAG answer
- Pipeline-generated reply
- LLM judge verdict and reasoning
- Human reviewer verdict and reasoning

The human reviewer independently assessed each case without referencing the judge's verdict. The judge's verdicts were then compared against the human verdicts. The alignment rate was **100%**, meaning the judge agreed with the human reviewer on every case.

This result provided sufficient confidence to proceed with using the judge in the main evaluation pipeline.

---

## Stage 2: Live Pipeline Evaluation

### Overview

With the judge validated, the main evaluator was built to assess the BasicFlow pipeline against live test data on an ongoing basis. The evaluation runs end-to-end: it loads test data, passes each case through the pipeline to generate a reply, then passes that reply to the judge for assessment.

### Data

Test cases are loaded from:

```
backend/evals/data/basic_test_data.jsonl
```

Each entry is a `BasicLLMInput` containing the sender information, the inbound message, the RAG answer, and citations.

### Evaluation Flow

For each test case, the evaluator runs the following steps:

1. Load the `BasicLLMInput` from the test dataset.
2. Pass it to `BasicFlow._call_llm()` to generate a `BasicEmailResponse`.
3. Construct a `BasicFlowEvalJudgeInput` with the original message, RAG answer, and generated reply.
4. Pass it to `BasicFlowEvaluator._judge()` which calls the LLM judge with Groq as primary and OpenRouter as fallback.
5. Append the result to the results file.

### Output Files

Each evaluation run produces two timestamped output files under:

```
backend/evals/basic_flow/results/
```

| File | Description |
|---|---|
| `basic_flow_results_<run_id>.jsonl` | Per-case raw results including original message, RAG answer, generated reply, judge verdict, and reasoning |
| `basic_flow_summary_<run_id>.md` | Aggregated summary with pass rate and per-case breakdown |

The `run_id` is formatted as `YYYYMMDD_HHMMSS`, allowing runs to be traced and compared over time.

### Why Live Pipeline Data Matters

Synthetic or manually crafted test data does not fully represent the distribution of inputs the pipeline encounters in production. Real emails vary in phrasing, intent, length, and complexity in ways that are difficult to anticipate when writing test cases by hand. Evaluating against live data ensures the results reflect actual pipeline behavior rather than performance on a curated subset.

There is also the issue of data drift. As the pipeline evolves — prompt changes, model updates, RAG content changes — synthetic benchmarks can become stale while live data naturally tracks what the system is actually processing. Running evals against live data on each significant change gives a reliable signal of whether the pipeline has improved or regressed in practice.

Finally, live data exposes edge cases. Unusual email formats, ambiguous requests, or topics not covered by the knowledge base are the cases most likely to produce bad outputs, and they are also the cases least likely to appear in a hand-written test set.

### Summary Report Structure

The summary report includes an aggregate metrics table at the top followed by a per-case breakdown. Each case in the breakdown includes the truncated original message, the truncated generated reply, and the judge's reasoning for its verdict.

### Judge

The judge is an LLM called via `BasicFlowEvaluator._judge()`. It receives the original message, RAG answer, and generated reply, and returns a structured `BasicFlowEvalJudgeOutput` with a `verdict` field (`GOOD` or `BAD`) and a `reasoning` field. The judge uses `temperature=0.0` for deterministic output and structured output parsing via `response_format`.

Provider fallback follows the same pattern as the pipeline: Groq is tried first, OpenRouter is used if Groq fails.

---

## Notes

- The `run_id` timestamp on output files ensures no previous results are overwritten between runs.

---

## Edge Case: RAG Answer Quality Validation

### Problem Identified

During live pipeline evaluation, an edge case was discovered: the RAG system sometimes returns answers that are technically valid (non-empty, has citations) but are functionally insufficient for responding to the client. Examples include:

- "I don't have enough information to answer that."
- "The notes don't mention what you asked about."
- Partial answers that answer only part of a multi-part question.

In the original pipeline design, the LLM simply paraphrased whatever RAG returned. This meant insufficient RAG answers were being rewritten into polished email responses and sent to clients — a poor user experience.

### Solution: Validation First, Paraphrase Second

The BasicFlow system prompt was redesigned with a two-stage process:

1. **Validate** — The LLM first checks if the RAG reply is a valid response. A reply is **INVALID** if it indicates information is missing, unavailable, unknown, not provided, or otherwise insufficient to answer the email.

2. **Paraphrase** — If the RAG reply is **VALID**, the LLM rewrites it into a polished email. If **INVALID**, the pipeline returns `answered="FALSE"` with an empty body, and no email is sent.

The output schema was updated to reflect this:

```python
class BasicEmailResponse(BaseModel):
    answered: Literal["TRUE", "FALSE"]
    body: str  # empty when answered=FALSE
```

### Impact on Evals

This change required updates to the evaluation pipeline:

1. **Test Data Expansion** — The test dataset was expanded to include cases where the RAG answer is insufficient. These cases expect `answered="FALSE"` and have no generated reply body.

2. **Eval Flow Modification** — The evaluator now checks the `answered` flag:
   - If `answered="TRUE"`: Normal quality evaluation via judge
   - If `answered="FALSE"`: Skip judge, add a note explaining why no evaluation was performed

3. **Summary Metrics** — The summary now distinguishes between:
   - Evaluated cases (answered=TRUE) — contribute to GOOD/BAD and pass rate
   - Unevaluated cases (answered=FALSE) — tracked separately as correctly identified unanswerable queries

4. **Schema Alignment** — The eval schemas remain unchanged; the `note` field is added only in results (in jsonl file) to explain skipped evaluations.

### Why This Matters for Evaluation

Without this change, evals would incorrectly treat `answered=FALSE` cases as having empty generated replies, skewing metrics. By separating validation quality (answered flag correctness) from response quality (GOOD/BAD for generated replies), the evaluation now accurately measures:

- **Validation accuracy** — Did the pipeline correctly identify unanswerable queries?
- **Generation quality** — For answerable queries, how good are the responses?

This dual metric provides a complete picture of pipeline health.