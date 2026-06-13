# BasicFlow Documentation

## Overview

`BasicFlow` is the end-to-end pipeline for handling a single inbound email. It receives a parsed email, retrieves context-aware information via the agentic RAG pipeline, generates a reply using an LLM, renders it into HTML, and delivers it via n8n. Every step is persisted to the database and traced in Langfuse under the email's thread ID as the session.

The pipeline includes a critical validation step: the LLM evaluates whether the RAG reply actually contains sufficient information to answer the email. If not, the system flags the email for manual review without attempting to send a response.

---

## Initialization

On instantiation, `BasicFlow` sets up two LLM clients — Groq and OpenRouter — both using the OpenAI-compatible interface. It also initializes the `AgenticRag` instance which is reused across all calls. Settings are loaded from `MainSettings`.

---

## Entry Point — `run(email, email_db_id)`

The only public method. Takes a parsed `InboundEmail` object and its database ID. Executes the pipeline sequentially across 6 steps and returns a `BasicEmailResponse`.

Two state variables are declared at the top before any step runs:

- **`llm_input`** — initialized as `None`, populated after Step 1 if RAG succeeds. Holds the RAG answer and citations for use in later steps and for DB persistence on failure.
- **`basic_inserted`** — initialized as `False`, flips to `True` only after `insert_basic` succeeds in Step 5. Guards against duplicate DB inserts in the except block.

---

## Pipeline Steps

**Step 1 — Build LLM Input**
Calls `_build_llm_input()` which runs the agentic RAG pipeline against the email body. Returns a `BasicLLMInput` object containing the sender details, original message, RAG answer, and citations. The RAG pipeline runs under the email's `thread_id` as the Langfuse session ID so traces are grouped correctly.

**Step 2 — Call LLM with Structured Output**
Calls `_call_llm()` which constructs the message list from the system prompt, the original email body, and the RAG answer, then calls the LLM using structured output. Providers are tried in order — currently only Groq is active. If a provider returns an empty response it is treated as a failure and the next provider is tried.

**Structured Output & RAG Validation:**
The LLM uses OpenAI's `parse()` method with a strict `BasicEmailResponse` schema:
```python
class BasicEmailResponse(BaseModel):
    answered: Literal["TRUE", "FALSE"]
    body: str
```

The LLM is instructed to:
- Set `answered = "FALSE"` and `body = ""` when the RAG reply is **INVALID** (indicates missing, unavailable, unknown, or insufficient information)
- Set `answered = "TRUE"` and `body = <polished email>` when the RAG reply is **VALID** (directly answers the email, even if brief)

This validation prevents the system from generating emails when the RAG context lacks the necessary information to answer the query. Token usage, cost, and the validation decision are recorded in Langfuse via the observability layer. Returns a `BasicEmailResponse` with the `answered` flag and either an empty body or the generated reply.

**Step 3 — Branch on Validation Result**
- If `response.answered == "FALSE"`: The pipeline short-circuits. No email is rendered or sent. The email is inserted into the database with `rag_status="failed"`, `needs_manual_reply=True`, and a failure reason indicating insufficient RAG context. The trace is closed and scored as a failure.
- If `response.answered == "TRUE"`: Proceeds to Step 4.

**Step 4 — Render HTML**
Passes the sender name and reply body to `render_email()` which wraps the plain text reply in the HTML email template.

**Step 5 — Send via n8n**
Calls `_send()` which attempts delivery via `send_to_n8n()` up to `N8N_MAX_RETRIES` times. Each attempt is logged individually. If `send_to_n8n` returns `{"status": "failed"}` instead of throwing, `_send` raises a `RuntimeError` explicitly so the retry loop actually fires. After all attempts are exhausted, the exception propagates up to `run()`.

**Step 6 — Insert to Database**
Calls `insert_basic()` with the full successful state — RAG answer, citations, send status, and `needs_manual_reply=False`. After this succeeds, `basic_inserted` is flipped to `True`. For the validation-failure branch, this step is skipped and a failure-state insert happens earlier.

**Step 7 — Mark Reviewed**
Calls `mark_basic_reviewed()` to update the parent email record. This step is wrapped in its own try/except — a failure here is logged but does not affect the overall success of the pipeline since the email was already sent and recorded.

---

## Failure Handling

All steps run inside a single try/except in `run()`. On any exception:

1. The Langfuse trace is closed with an empty output and scored as a failure.
2. If `basic_inserted` is `False`, a failure-state row is inserted into the database with:
   - `rag_answer` and `citations` from `llm_input` if RAG had already succeeded, with safety checks for `None` values
   - `rag_status="failed"`
   - `failure_reason` set to the exception message or a specific reason
   - `needs_manual_reply=True`
3. A `BasicEmailResponse` is returned with `answered="FALSE"` and an empty body.

**Failure scenarios and what gets saved:**

- **RAG fails** — `llm_input` is `None`. DB row is inserted with no RAG data, flagged for manual review.
- **RAG succeeds, LLM validation returns `answered="FALSE"`** — `llm_input` is populated, but the LLM determined the RAG reply was insufficient. DB row is inserted with RAG answer and citations, `rag_status="failed"`, and a specific failure reason explaining the validation failure. No email is sent.
- **RAG succeeds, LLM validation returns `answered="TRUE"`, but generation fails** — Same as above. RAG answer and citations are saved to DB even though no reply was generated. Most valuable partial-state case.
- **RAG succeeds, LLM succeeds, send fails** — Full RAG and LLM output is preserved in DB, flagged for manual review.
- **Step 6 insert succeeds, Step 7 fails** — `basic_inserted` is `True`. Except block skips `insert_basic` entirely, preventing a duplicate key violation.
- **Step 6 insert itself fails** — `basic_inserted` never flipped. Except block attempts failure-state insert with whatever partial data is available.

The guarantee is that **every email that enters `run()` produces exactly one database row** — either a successful record or a failure record with the maximum amount of data that was available at the point of failure. The RAG validation edge case is explicitly handled as a failure branch, ensuring no emails are sent when the system lacks confidence in its answer.

---

## Observability

Every run is traced in Langfuse via `BasicFlowObservability`. The trace opens at the start of `run()` and closes in both the success and failure paths. Individual spans are created for the RAG step, the LLM generation, and the send step. The LLM generation span captures the system prompt, user content, model, provider, token counts, cost, and crucially — the `answered` decision. The send span captures the final status, number of attempts, and the n8n email ID. Traces are scored as success or failure at the end of every run, with validation failures being scored as failures.

---

## LLM Provider Fallback

`_call_llm()` iterates through a providers list. Each provider is a tuple of `(name, client, model)`. If a provider throws or returns empty content, the error is logged and the next provider is tried. If all providers fail, the last exception is re-raised and propagates to `run()`. Structured output via `parse()` is used with all providers that support it.

---

## Citations Safety

All database insert operations include safety checks for citations:
```python
citations=[c.model_dump() for c in llm_input.citations] if llm_input.citations else None
```
This ensures that `citations` is either a list of dictionaries or `None`, preventing iteration errors when the RAG pipeline returns no citations. This safety check is applied in both success and failure paths.