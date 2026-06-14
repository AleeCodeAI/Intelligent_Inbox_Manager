# Inbox Manager — AI Email Automation and Management

## Client Brief
### Context and Persona
The target user for this system is an independent professional, such as a specialized AI Engineer, Consultant, Lawyer, or Freelancer, who handles a high volume of client interactions daily. Managing an inbox containing hundreds or thousands of messages monthly quickly becomes a bottleneck, draining time that should be spent on core technical or billable work.

### The Problem
Repetitive Overhead: Between 60% and 70% of all incoming emails consist of repetitive, low-risk inquiries. These typically include questions regarding pricing tiers, basic service offerings, professional background, past project journeys, or immediate availability.

**Clutter and Noise:** A notable percentage of incoming traffic consists of non-business emails, including spam, newsletters, personal notifications, and promotional offers.

**The Critical Core:** A small but vital subset of emails contains high-value project leads, critical ongoing client negotiations, legal notifications, financial communications, or immediate booking requests.

**The Risk:** Sorting through a traditional, noisy inbox makes it remarkably easy to miss high-priority communications. Entrusting automated AI to handle sensitive, high-value discussions entirely on autopilot poses an unacceptable business risk.

### The Solution
This platform splits the inbox traffic into three distinct streams to isolate noise, automate routine answers, and elevate sensitive conversations:

Basic Queries (Automated): Automatically answered using an Agentic Retrieval-Augmented Generation (RAG) system running against the professional's comprehensive documentation, notes, and business FAQs.

Priority Conversations (Human-in-the-Loop): Flagged, categorized, and safely stored in a local database. They are surfaced on a clean web frontend for manual human responses and single-click appointment scheduling.

Non-Business Volume (Isolated): Saved silently to keep records intact without triggering notifications or automation, allowing the user to review or clear them out globally.

## Project Summary

Inbox Manager is a backend + frontend application that automates routine email replies with LLMs, classifies incoming mail, and provides a human-facing UI for review, appointment scheduling, and manual replies.

- Backend: receives emails, preprocesses and classifies content, routes messages to flow implementations, and stores records.
- Frontend: operator UI for reviewing failed Basic, Priority and Non-Business messages, sending manual replies, scheduling appointments, and viewing analytics.

For detailed backend docs see [backend/README.md](backend/README.md). For frontend details see [frontend/README.md](frontend/README.md).

## Scope & documentation

This `README.md` provides a high-level overview of Inbox Manager. The system is complex and contains many implementation details, flow documents, and evaluation artifacts. For a deeper understanding consult the dedicated documentation included in the repository:

- `backend/README.md` and the documents under `backend/core/`, `backend/flows/`, and `backend/evals/` for executor logic, flow implementations, and evaluation notes.
- `frontend/README.md` and the files under `frontend/src/` for UI behavior, API usage, and service integration details.

There are many independent documentations you can use to understand the system.

## Key Features

- Automated replies for routine (Basic) emails using retrieval-augmented generation (RAG) and LLM rewriting.
- Manual review and action for Priority emails with appointment creation and calendar confirmation.
- Safe handling of Non-Business emails: stored and visible but not auto-responded.
- Provider fallback for LLM clients to improve resilience.
- Observability of LLM calls via Langfuse for debugging and auditing.
- n8n-based Gmail and calendar integrations to keep OAuth and plumbing separate from core code.

## How It Works (Core Workflow)

1. An email arrives (via n8n webhook or ingestion pipeline).
2. Backend preprocesses the email text and metadata.
3. The system classifies the message as Basic, Priority, or Non-Business.
4. Routing by category:
   - Basic: run agentic RAG to gather supporting content, generate a draft reply, rewrite into a polished email, and send automatically (with error handling and provider fallback).
   - Priority: save the message, run a secondary classification to add tags (e.g., APPOINTMENT, SENSITIVE, HIGH_VALUE), surface in the frontend for manual response, and support appointment workflows that mark calendar events and send confirmations.
   - Non-Business: store the message for review or deletion; do not auto-reply.
5. All processed data and artifacts are stored in the database and exposed through API endpoints for the frontend.

## Email Categories (Quick)

- Basic: common service inquiries, pricing, availability. Automated and usually auto-replied.
- Priority: confidential or high-value messages. Always reviewed by a human. Appointment scheduling supported.
- Non-Business: personal, promotional, or spam. Stored for record; optional manual action.

## Frontend Experience

- Tabs for Basic, Priority, and Non-Business messages.
- Manual reply editor and appointment scheduling in Priority flows.
- Processed emails page for audit and history.
- Executor control to manually trigger the master pipeline when needed.
- Dashboard for analytics and volume/latency metrics.

## Technology Stack

- Backend: Python, FastAPI
- Frontend: React + Vite
- Database: PostgreSQL
- LLM Providers: Groq (primary), Openrouter (fallback), OpenAI SDK supportable
- Observability: Langfuse
- Integration/Automation: n8n for Gmail and calendar workflows

## Environment Variables (development)

Keep secrets out of version control. Common variables used in development:

- `POSTGRESQL_URL` — PostgreSQL connection string (e.g. `postgres://user:pass@host:5432/dbname`)
- `GROQ_API_KEY`, `GROQ_URL` — Groq provider credentials
- `OPENROUTER_API_KEY`, `OPENROUTER_URL` — Openrouter credentials
- `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST` — Langfuse config (dev default: `http://localhost:3100`)
- `N8N_GET_EMAILS_WEBHOOK_URL`, `SEND_EXAMPLE_EMAILS_N8N_URL`, `SEND_EMAILS`, `MARK_CALENDAR`, `DELETE_CALENDAR` — n8n webhook URLs for Gmail/calendar automation
- `VITE_API_BASE_URL` — Frontend: base URL for backend API (set in `.env.local` for Vite)

## n8n Workflows

The project includes n8n workflow JSON files to import into an n8n instance. Place or find them in `n8n_workflows/`. Import those workflows into your n8n installation, enable them, and copy the generated webhook URLs into your backend `.env`.

## API Contract (endpoints used by frontend)

Use these routes as the canonical frontend→backend contract (see frontend code for exact usage):

- `GET /retrieval/basic/manual-pending` — list Basic emails pending manual review
- `POST /actions/basic-action` — send manual response / take action on a Basic email
- `GET /retrieval/priority/unreviewed` — list Priority emails awaiting review
- `POST /actions/priority-action` — take action on a Priority email (payload may include appointment data)
- `GET /retrieval/nonbusiness/unreviewed` — list Non-Business emails awaiting review
- `POST /actions/nonbusiness-action` — take action on a Non-Business email
- `DELETE /delete/email/:gmailId` — delete an email by Gmail ID
- `GET /retrieval/emails` — list all emails
- `GET /retrieval/email-processing` — list processed emails
- `POST /master-pipeline/executor-run` — run the master pipeline manually
- `GET /retrieval/appointments` — list appointments
- `DELETE /delete/appointment` — delete an appointment (payload expected in DELETE body)
- `POST /analysis/get-dashboard-analysis` — dashboard analytics endpoint

## Local Development (quick)

Backend (recommended inside a virtual environment)

1. Copy example env: create `.env` from `backend/example.env` and fill secrets.
2. Install dependencies: follow `backend/pyproject.toml` instructions (Poetry or pip as used in the repo).
3. Start PostgreSQL and ensure `POSTGRESQL_URL` is reachable.
4. Run database migrations / init (see `backend/database/init_db.py`).
5. Run the API:

```powershell
# from backend/
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend

1. Create `.env.local` with `VITE_API_BASE_URL=http://localhost:8000`.
2. Install and run:

```bash
cd frontend
npm install
npm run dev
```

Docker (compose)

If you use the provided `docker-compose.yml`, verify environment variables are set in your environment or compose overrides. Then:

```powershell
docker-compose up --build
```

## Observability & LLM Strategy

- Langfuse: record LLM inputs, outputs, latencies, and errors so you can reproduce or debug model decisions.
- Model routing: use lightweight models (cost-effective) for common tasks and route higher-sensitivity retrieval/RAG flows to stronger models. Use provider fallback when primary services hit limits.

## Project Structure (high level)

- `backend/` — API, executor, flows, schemas, DB models, utils
- `backend/api/` — FastAPI endpoints
- `backend/core/` — executor pipeline and preprocessors
- `backend/flows/` — flow implementations: `basic`, `priority`, `non_business`
- `backend/n8n_workflows/` — JSON files for n8n imports
- `frontend/` — React + Vite app, UI pages and services

See `backend/README.md` and `frontend/README.md` for flow-specific and UI-specific details.

## Troubleshooting & Tips

- If LLM calls fail frequently, enable Langfuse tracing and check provider quotas.
- If webhook events from n8n do not arrive, confirm the workflow is enabled and the webhook URL matches `N8N_*` env values.
- For local testing, `LANGFUSE_HOST` can point to `http://localhost:3100`.

## About the developer

I am Ali Sina Ghulami, a 17-year-old aspiring AI engineer learning to build production-grade AI systems. I focus on creating practical tools that let professionals automate routine work while keeping humans in control of sensitive decisions.

Acknowledgements

- This project uses Langfuse for LLM observability and n8n for Gmail & calendar automation.
- Thanks to contributors, reviewers, and users who test flows and improve prompts.
