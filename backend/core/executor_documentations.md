# Executor Documentation


## Overview

`Executor` is the master orchestration pipeline for the email automation system. It is the entry point for all inbound email processing. It fetches emails in batches, deduplicates by gmail_id, classifies each email using an LLM, routes it to the appropriate downstream flow, and persists the full processing record. Every run is traced in Langfuse and scored as success or failure.

---

## Initialization

On instantiation, `Executor` sets up two LLM clients — Groq and OpenRouter — both using the OpenAI-compatible interface. It also initializes `EmailReceiver` for fetching inbound emails and a `flow_registry` which maps classification labels to their respective flow instances — `BasicFlow`, `PriorityFlow`, and `NonBusinessFlow`. All three flows are instantiated once at startup and reused across all emails in the batch.

---

## Entry Point — `run()`

The public async method. Fetches the full email batch from `EmailReceiver`, then spawns a `_process_email()` task for every email in the batch. All tasks run concurrently via `asyncio.gather()`. Results are collected, exceptions are caught and logged per-task without crashing the entire batch, and the final list of `EmailProcessed` objects is returned.

---

## Single Email Processing — `_process_email(email)`

The core per-email pipeline. Runs the full lifecycle for a single email and returns an `EmailProcessed` result.

**Deduplication check** happens before anything else. If the email's `gmail_id` already exists in the database, the email is skipped entirely and `None` is returned. This prevents reprocessing emails that were already handled in a previous run.

A `uuid_id` is generated at the start and used as the primary key for all database records created during this email's lifecycle — linking the email record, the processing record, and the flow-specific record together.

**`email_inserted`** is a boolean flag initialized as `False`, flipped to `True` after `insert_email` succeeds. In the except block this guards the `insert_processing` call — a processing record should only be inserted if the parent email row exists. If `insert_email` itself failed, `email_inserted` stays `False` and no orphaned processing record is created.

---

## Pipeline Steps

**Step 1 — Insert Email**
Inserts the raw email into the database using `insert_email()`. This is the first write operation. On success, `email_inserted` flips to `True`.

**Step 2 — Classification**
Calls `_call_llm()` which constructs messages from the system prompt and the first 1000 characters of the email body, then calls the LLM using structured output parsing into `ExecutorResult`. Returns a classification label, confidence score, and reasoning. Body is truncated to 1000 characters to keep classification cost low.

**Step 3 — Flow Routing**
Looks up the classification label in `flow_registry`. If a matching flow exists, it is called via `asyncio.to_thread()` since all downstream flows (`BasicFlow`, `PriorityFlow`, `NonBusinessFlow`) are synchronous. This prevents them from blocking the async event loop. If the classification label is unknown or not in the registry, it is logged and processing continues without routing.

**Step 4 — Insert Processing Record**
Creates an `EmailProcessed` object with the gmail ID, classification result, timestamp, and `success=True`, then persists it via `insert_processing()`.

---

## Failure Handling

All steps after deduplication run inside a single try/except. On any exception:

1. A `fallback_result` is constructed with `classification="UNKNOWN"`, `confidence=0.0`, and the error as the reasoning. This is used only if the LLM classification in Step 2 had not yet completed — otherwise the real `result` from locals is used.
2. An `EmailProcessed` object is built with `success=False`.
3. If `email_inserted` is `True`, a processing record is still inserted so there is always a traceable record of what happened.
4. The trace is scored as failure with the error message.
5. The `EmailProcessed` with `success=False` is returned — the batch runner treats this as a handled failure, not a crash.

**Failure scenarios:**

- **`insert_email` fails** — `email_inserted` stays `False`. No processing record is inserted. Trace is scored as failure.
- **Classification fails** — Email row exists. Processing record is inserted with `success=False` and the fallback result.
- **Flow routing fails** — Same as above. The flow's own internal failure handling also applies independently.
- **`insert_processing` fails** — Logged as part of the exception. Trace is scored as failure.
- **Task-level crash in `asyncio.gather`** — Caught by the batch runner in `run()`, logged, and skipped. Does not affect other emails in the batch.

---

## LLM Provider Fallback

`_call_llm()` iterates through a providers list in order — Groq first, then OpenRouter. Each provider uses structured output parsing via `.parse()` directly into `ExecutorResult`, so no manual JSON parsing is needed. If a provider fails for any reason, the error is logged and the next provider is tried. Token counts and cost are logged per successful call. If all providers fail, the last exception is re-raised and propagates to `_process_email()`'s except block.

---

## Concurrency Model

The batch runner uses `asyncio.gather()` to process all emails concurrently. Each `_process_email()` call is an async coroutine, but downstream flows are synchronous — they are offloaded to a thread pool via `asyncio.to_thread()` so they don't block the event loop. This means multiple emails can be in different stages of their pipeline simultaneously without one blocking another.

---

## Observability

Every email run opens a Langfuse trace via `ExecutorObservability` with the full email metadata. The LLM generation span captures the system prompt, user content, model, provider, token counts, and cost. The trace is closed and scored at the end of every run — success if the pipeline completed, failure with the error reason if it did not. Unlike `BasicFlow`, the Executor does not have a separate send span since delivery is handled entirely within the downstream flows.