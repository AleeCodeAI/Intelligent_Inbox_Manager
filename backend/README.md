# Inbox Manager — Backend

## Overview
This system is an AI email automation and management platform designed for individuals, freelancers, and small professional teams who need to manage business email efficiently.

It is not built as a traditional large-scale customer support ticketing system. Instead, it is optimized for people such as:

- Lawyers managing client inquiries and contracts
- Freelancers handling client communications and proposals
- Consultants coordinating appointments and project requests
- Developers receiving service inquiries and business questions

The platform helps users:

- Automate repetitive inquiry responses
- Quickly identify high-priority messages
- Keep non-business emails organized
- Improve response workflows with a focused UI

## Why This System Matters
Many professionals receive dozens or hundreds of emails every week. Most of those messages are routine inquiries that can be answered automatically, while only a small subset requires immediate human attention.

This system solves that problem by:

- Reducing the time spent reading and replying to repetitive requests
- Preserving attention for priority emails that require judgment or confidentiality
- Preventing important messages from getting lost in the inbox
- Giving users a single place to manage the most critical email interactions

## Core Workflow
The backend is powered by an executor pipeline that acts as the main master workflow.
The executor receives incoming emails, preprocesses the content, chooses the correct category, and routes the message to the suitable flow implementation in `flows/`.

This pipeline is described in detail in `core/executor_documentations.md`.

## Architecture Diagram

![Architecture Diagram](architecture_diagram.png)

The diagram above visualizes the executor pipeline and high-level components: a `BackendManager` starts the `Executor` which reads and preprocesses incoming emails, classifies them (Basic / Priority / Non-business), and routes each message to the appropriate flow. It highlights decision points, storage of messages and metadata, and how automated vs. manual review branches are handled.

The backend processes each incoming email through a category-driven workflow:

1. Receive an incoming email
2. Preprocess the email content
3. Classify it into one of three categories:
   - Basic emails
   - Priority emails
   - Non-business emails
4. Route the email to the appropriate flow implementation
5. Store emails and generated outputs as needed
6. Expose data to the frontend for review and manual actions

## Email Categories

### Basic Emails
These messages make up the majority of incoming traffic—often 60–70% of emails.

Typical content includes:
 - Service inquiries
 - Pricing questions
 - Availability requests
 - Offer details
 - Expertise and capabilities questions

Behavior:

 - The system routes basic emails through the basic flow implementation in `flows/basic/`.
 - The email body is passed to an agentic RAG system as a query.
 - The RAG system searches the library of documents, notes, and service information to find the most relevant supporting content.
 - It produces a strong answer with citations and context drawn from the data.
 - A second LLM call then rewrites that answer into a polished email reply.
 - The formatted reply is inserted into an HTML email template for a clean presentation.
 - The final generated email is sent automatically as a reply.
 - The basic flow also includes robust error handling, retry logic, and client fallback behavior. If one LLM client fails, the system can switch to another client and continue processing.

This allows the system to automate routine business communications safely and efficiently.

### Priority Emails
Priority messages are high-value, sensitive, or ongoing client communications that should not be auto-replied by AI.

Examples include:

- Legal inquiries
- Confidential project discussions
- High-value contract negotiation
- Sensitive client requests
- Ongoing client relationship emails

Behavior:

- Priority emails are saved in the database.
- They are surfaced in the frontend for manual review.
- The user can compose a custom response instead of relying on automation.
- If needed, the user can schedule appointments and mark calendar events from the UI.
- Appointment workflows include calendar marking and confirmation email generation before sending the final reply.

When the priority flow receives a message, it runs a second classification pass to label the email as one of the following:
 - Client communication
 - Sensitive
 - High value
 - Appointment

That additional classification helps the system store the message with the right review context and ensures the frontend shows the correct priority and action options.

The priority flow also includes client fallback behavior so any LLM-assisted enrichment remains resilient when a provider fails.

### Non-Business Emails
Non-business emails are stored for later review but are intentionally not automated.

This category includes:

- Personal emails
- Spam or promotional messages
- Informational newsletters
- Non-work-related content

Behavior:

- Non-business emails are saved in the database.
- They are displayed in the frontend for optional action.
- Users can choose to respond manually or delete them.

When the non-business flow receives a message, it classifies it as one of:
 - Spam
 - Promotional
 - Informational
 - Personal

That classification helps the frontend organize and present non-business messages clearly.

The non-business flow also supports client fallback logic for any LLM clients used in auxiliary processing.

## Frontend Experience
The frontend provides a centralized interface so users can:

- Review priority emails that need human attention
- See non-business messages in one place
- Schedule appointments and confirm calendar events
- Send manual replies to important conversations
- Avoid hunting through a traditional inbox for high-priority content

## System Benefits

- Automates repetitive email replies for predictable inquiries
- Improves visibility into urgent and sensitive communications
- Keeps non-business messages organized without unnecessary automation
- Helps professionals focus on the emails that matter most
- Provides a modern workflow for managing email-driven client work

## Technologies Used

- **Programming language:** Python — the entire backend is implemented in Python for consistency and simplicity.
- **Web framework:** FastAPI — used for the API layer and endpoints in `api/` for high-performance async HTTP handling.
- **LLM client:** OpenAI SDK — primary client interface for LLM calls and integrations.
- **Database:** PostgreSQL — production-grade relational database for storing emails, metadata, and generated artifacts.
- **Observability:** Langfuse — used to capture and visualize LLM calls, traces, and metrics for debugging and performance analysis.
- **Schemas & settings:** Pydantic & Pydantic Settings — typed schemas and centralized configuration management across the app.
- **Low-code automation:** n8n — used for Gmail and calendar integrations (webhooks, send/receive email, create/delete calendar events).
- **Other tools:** Openrouter and Groq (for alternative LLM providers), plus other Python core libraries used throughout the project.

## Why Langfuse and n8n

- **Langfuse (LLM observability):**
   - **Traceability:** records inputs, outputs, latencies, and errors for every LLM call so you can reproduce and debug behavior.
   - **Performance insights:** helps identify high-latency calls or costly patterns and optimize prompt structure or routing.
   - **Auditability:** useful for compliance and monitoring when model outputs affect user-facing actions.

- **n8n (low-code Gmail & calendar workflows):**
   - **Rapid integration:** provides prebuilt Gmail and calendar nodes so you can offload authentication and event handling without custom code.
   - **Webhook support:** manages incoming email events and calendar actions (create/update/delete) via webhooks, simplifying orchestration.
   - **Separation of concerns:** keeps Gmail/calendar plumbing out of the core backend, making the system easier to maintain and secure.

## LLMs and Model Strategy

- **Primary providers:**
   - **Groq:** used where free-tier or low-cost API access suffices; great for many routine LLM calls.
   - **Openrouter:** configured as a fallback and for higher-volume routes when Groq reaches rate limits.

- **Models used in the system:**
   - **`gpt-oss-120b`:** primary model used across the system for most tasks — reliable, cost-effective, and performs well with carefully designed prompts.
   - **`gpt-4.1-nano`:** reserved for agentic RAG and other higher-sensitivity tasks where stronger reasoning or retrieval-augmented responses are needed.

- **Strategy highlights:**
   - Use lightweight, well-prompted models for common tasks to keep costs and latency down (`gpt-oss-120b`).
   - Route complex retrieval or agentic RAG flows to stronger models (`gpt-4.1-nano`) or fallbacks as necessary.
   - Employ provider fallback (Openrouter) when primary endpoints (Groq) hit limits, and use Langfuse to monitor which calls are most expensive or error-prone.

## Environment variables & n8n workflows

This project expects several environment variables (commonly stored in a `.env` file or your deployment secrets) to configure LLM providers, observability, n8n webhooks, and the database. Below are the variables used in development:

- `OPENROUTER_API_KEY`, `OPENROUTER_URL` — credentials and base URL for the Openrouter provider.
- `GROQ_API_KEY`, `GROQ_URL` — credentials and base URL for Groq (primary free/low-cost provider).
- `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST` — Langfuse keys and host (default local dev: `http://localhost:3100`).
- `N8N_GET_EMAILS_WEBHOOK_URL`, `SEND_EXAMPLE_EMAILS_N8N_URL`, `SEND_EMAILS`, `MARK_CALENDAR`, `DELETE_CALENDAR` — webhook endpoints hosted by your n8n instance for receiving email events and performing calendar/email actions.
- `POSTGRESQL_URL` — PostgreSQL connection string (example: `postgres://user:pass@host:5432/dbname`).

Notes and setup guidance:
- Keep all API keys and connection strings secret; do not commit `.env` to version control.
- `N8N_*` variables must point to the webhook URLs created in your n8n workflows (for example `https://n8n.example.com/webhook/get-emails`).
- We will provide the n8n workflow JSON files that define Gmail/calendar flows and webhook nodes; import those JSONs into your n8n instance, enable the workflows, and then copy the generated webhook URLs into your `.env` values above.
- n8n will handle Gmail authentication and calendar access; ensure you complete OAuth setup in your n8n environment before enabling the workflows.
- For local testing, `LANGFUSE_HOST` can point to a local Langfuse instance (`http://localhost:3100`) or to your hosted Langfuse endpoint.

If you want, I can save the provided n8n workflow JSONs into `backend/n8n_workflows/` (or another path you prefer) so they're easy to import. Tell me where you'd like them placed.


## Project Structure
 - `api/` — FastAPI endpoints for receiving and managing email events; API details are documented in `api/api_documentations.md`
 - `core/` — Core application files for the main executor pipeline, preprocessing, classification, and routing logic; see `core/executor_documentations.md`
 - `database/` — Models, repositories, and persistence for incoming messages
 - `schemas/` — Pydantic schemas for the entire system
 - `prompts/` — AI prompt templates and flow definitions
 - `utils/` — HTML templates, calendar support, and loggings
 - `flows/` — Flow and pipeline implementations for each classification branch: `basic`, `priority`, and `non_business`
 - `evals/` — Comprehensive evaluation artifacts and documentation for system performance and behavior

## Documentation

- `core/executor_documentations.md` — executor pipeline documentation and overall routing behavior
- `api/api_documentations.md` — API endpoint documentation and request/response details
- `flows/basic/basic_flow_documentations.md` — automated BASIC email flow and agentic RAG processing
- `evals/` — evaluation reports and documentation for model and workflow quality

> This README focuses on the backend architecture and workflow around AI-driven email classification, automation, and manual message management.
