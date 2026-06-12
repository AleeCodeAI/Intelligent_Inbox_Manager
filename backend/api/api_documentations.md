# Email Automation API Documentation

**Base URL:** `http://localhost:8000`  
**Version:** 1.0.0

---

## General

All endpoints return a consistent JSON envelope:

```json
{ "status": "success", "data": ... }
{ "status": "error", "message": "..." }
```

Rate limit: **30 requests/minute** per IP (10/minute for executor).  
Validation errors return `422`. Server errors return `500`.

---

## Base

### GET `/`
```json
{
  "status": "success",
  "service": "Email Automation API",
  "version": "1.0.0"
}
```

### GET `/health`
```json
{
  "status": "success",
  "executor": "ready",
  "actions": "ready"
}
```

---

## Retrieval — `/retrieval`

All retrieval endpoints are `GET` with no request body.  
All return `{ status, count, data[] }`.

---

### GET `/retrieval/emails`
All emails from the emails table.

**Response:**
```json
{
  "status": "success",
  "count": 10,
  "data": [
    {
      "email_db_id": "uuid",
      "gmail_id": "msg_abc123",
      "thread_id": "thread_xyz",
      "sender_name": "John Doe",
      "sender_email": "john@example.com",
      "subject": "Meeting Request",
      "body": "Hi, I wanted to..."
    }
  ]
}
```

---

### GET `/retrieval/email-processing`
All email processing records joined with their originating email.

**Response:**
```json
{
  "status": "success",
  "count": 10,
  "data": [
    {
      "email_processing_id": "uuid",
      "email_db_id": "uuid",
      "classification": "PRIORITY",
      "confidence": 0.95,
      "reasoning": "Contains legal language...",
      "success": true,
      "processed_date": "2026-05-29T08:00:00",
      "sender_name": "John Doe",
      "sender_email": "john@example.com",
      "subject": "Meeting Request",
      "body": "Hi, I wanted to...",
      "gmail_id": "msg_abc123",
      "thread_id": "thread_xyz"
    }
  ]
}
```

---

### GET `/retrieval/appointments`
All appointments joined with their originating email.

**Response:**
```json
{
  "status": "success",
  "count": 3,
  "data": [
    {
      "email_db_id": "uuid",
      "event_id": "google_event_id",
      "event_title": "Meeting with John",
      "event_start": "2026-05-29T08:00:00",
      "event_end": "2026-05-29T09:00:00",
      "calendar_status": "created",
      "confirmation_email_status": "sent",
      "created_at": "2026-05-29T07:00:00",
      "sender_name": "John Doe",
      "sender_email": "john@example.com",
      "subject": "Meeting Request",
      "body": "Hi, I wanted to...",
      "gmail_id": "msg_abc123",
      "thread_id": "thread_xyz"
    }
  ]
}
```

---

### GET `/retrieval/basic/manual-pending`
Basic emails where RAG failed and manual reply is pending.  
Filters: `needs_manual_reply=True`, `reviewed=False`.

**Response:**
```json
{
  "status": "success",
  "count": 2,
  "data": [
    {
      "email_db_id": "uuid",
      "gmail_id": "msg_abc123",
      "thread_id": "thread_xyz",
      "sender_name": "John Doe",
      "sender_email": "john@example.com",
      "subject": "Product Question",
      "body": "Hi, I wanted to...",
      "rag_status": "failed",
      "failure_reason": "No relevant chunks found",
      "rag_answer": null,
      "citations": null,
      "needs_manual_reply": true,
      "reviewed": false
    }
  ]
}
```

---

### GET `/retrieval/nonbusiness/unreviewed`
Non-business emails not yet reviewed by admin.  
Filters: `reviewed=False`. Ordered by `confidence` descending.

**Response:**
```json
{
  "status": "success",
  "count": 4,
  "data": [
    {
      "email_db_id": "uuid",
      "gmail_id": "msg_abc123",
      "thread_id": "thread_xyz",
      "sender_name": "John Doe",
      "sender_email": "john@example.com",
      "subject": "Hey!",
      "body": "Just checking in...",
      "nonbusiness_type": "PERSONAL",
      "confidence": 0.91,
      "reasoning": "Casual tone, no business intent...",
      "reviewed": false
    }
  ]
}
```

---

### GET `/retrieval/priority/unreviewed`
High-priority emails not yet reviewed by admin.  
Filters: `reviewed=False`. Ordered by `confidence` descending.

**Response:**
```json
{
  "status": "success",
  "count": 2,
  "data": [
    {
      "email_db_id": "uuid",
      "gmail_id": "msg_abc123",
      "thread_id": "thread_xyz",
      "sender_name": "John Doe",
      "sender_email": "john@example.com",
      "subject": "Contract Review Needed",
      "body": "Please review the attached...",
      "priority_type": "LEGAL",
      "confidence": 0.97,
      "reasoning": "Contains contract and legal terminology...",
      "reviewed": false
    }
  ]
}
```

---

## Delete — `/delete`

### DELETE `/delete/email/{gmail_id}`

Deletes an email by Gmail ID. Cascades to all extension tables (processing, basic, priority, nonbusiness, appointments).

**Path Parameter:** `gmail_id` — Gmail message ID of the email to delete.

**Response:**
```json
{ "status": "success", "deleted_gmail_id": "msg_abc123" }
```

---

### DELETE `/delete/appointment`

**Rate limit: 30 requests/minute**

Deletes an appointment and its corresponding calendar event. Takes a `DeleteAppointmentSchema` payload with `gmail_id` and `event_id`, then cascades deletion to the database and removes the calendar event via n8n.

**Request Body:**
```json
{
  "gmail_id": "msg_abc123",
  "event_id": "google_event_id"
}
```

**Response:**
```json
{
  "status": "success",
  "deleted_gmail_id": "msg_abc123",
  "deleted_event_id": "google_event_id"
}
```

---

## Actions — `/actions`

### POST `/actions/priority-action`

Triggers the action flow for a priority email — sends the manual response via n8n and optionally creates a calendar event.

**Request Body:**
```json
{
  "gmail_id": "msg_abc123",
  "sender_name": "John Doe",
  "priority_type": "APPOINTMENT",
  "manual_response": "Thank you for reaching out. I've scheduled a meeting...",
  "calendar_details": {
    "title": "Meeting with John",
    "start": "2026-05-29T08:00:00+05:00",
    "end": "2026-05-29T09:00:00+05:00"
  }
}
```

> `calendar_details` is optional. Omit it if the priority type does not involve scheduling.

**Response:**
```json
{
  "status": "success",
  "result": {
    "status": "sent",
    "emailId": "msg_abc123"
  }
}
```

---

### POST `/actions/nonbusiness-action`

Triggers the action flow for a non-business email — sends the manual response via n8n.

**Request Body:**
```json
{
  "gmail_id": "msg_abc123",
  "sender_name": "John Doe",
  "manual_response": "Thank you for your message. This falls outside our business scope...",
  "nonbusiness_type": "PERSONAL"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "status": "sent",
    "emailId": "msg_abc123"
  }
}
```

---

## Analysis — `/analysis`

### POST `/analysis/get-analysis`

**Rate limit: 100 requests/minute**

Triggers the email analysis workflow to compute analytical data for the dashboard. Aggregates metrics and statistics across all processed emails.

**Request Body:** No parameters required.

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_emails": 150,
    "processed_emails": 142,
    "priority_count": 25,
    "nonbusiness_count": 45,
    "basic_count": 72,
    "appointments_created": 12,
    "manual_pending": 8
  }
}
```

---

## Master Pipeline — `/master-pipeline`

### POST `/master-pipeline/run`

**Rate limit: 10 requests/minute**

Fetches all unprocessed emails and runs them through the full classification and action pipeline.

#### Why this endpoint is async

The executor (`executor.run()`) is a coroutine — it does multiple async operations internally (fetching emails, calling LLMs, hitting n8n, writing to DB). In a regular Python script you'd run it with `asyncio.run()`. Inside FastAPI you `await` it directly because FastAPI's event loop is already running. This means the endpoint is non-blocking — while the executor is processing, the server can still handle other incoming requests.

```python
# correct inside FastAPI
results = await executor.run()

# what you'd use in a standalone script
results = asyncio.run(executor.run())
```

**Response:**
```json
{
  "status": "success",
  "processed_count": 5,
  "results": [
    { "gmail_id": "msg_abc123", "classification": "PRIORITY", "success": true },
    { "gmail_id": "msg_def456", "classification": "NONBUSINESS", "success": true },
    { "gmail_id": "msg_ghi789", "classification": "BASIC", "success": false }
  ]
}
```

---

## Interactive Docs

Swagger UI available at `http://localhost:8000/docs` when the server is running.