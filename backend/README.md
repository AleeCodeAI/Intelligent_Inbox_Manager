# AI Email Automation and Management System

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
