# Database Design Documentation

## Inbox Manager (AI Email Automation & Management System)

---

# 1. Overview

This system processes incoming emails using AI, classifies them, and executes automated actions based on the classification.

The backend uses PostgreSQL with SQLAlchemy and follows a normalized relational design.

Core principle:

> Each email is stored once, and extended through related tables depending on its classification and processing requirements.

---

# 2. Why this architecture was chosen

This architecture was designed to achieve the following goals:

### 2.1 No duplication of email data

All raw email content is stored in a single table. This avoids redundancy and inconsistency.

### 2.2 Flexible AI processing

Different email types require different AI outputs:

* Basic emails use RAG-based responses
* Priority emails require sensitivity and client classification
* NonBusiness emails store rejection or filtering reasons

### 2.3 Scalable design

New email categories can be added without modifying existing tables.

### 2.4 Easier analytics

Centralized email storage allows simple aggregation and reporting queries.

---

# 3. Database Architecture

## 3.1 Tables Overview

The system consists of five main tables:

1. emails
2. email_processing
3. basic_email_data
4. priority_email_data
5. nonbusiness_email_data

---

## 3.2 Entity Relationship Diagram

```text
                    ┌──────────────────┐
                    │      emails      │
                    │------------------│
                    │ id (PK)          │
                    │ sender_email     │
                    │ subject          │
                    │ body             │
                    └────────┬─────────┘
                             │
                             │ 1
                             │
            ┌────────────────┴────────────────┐
            │                                 │
┌──────────────────────┐        ┌────────────────────────────┐
│ email_processing     │        │ category-specific tables    │
│----------------------│        │----------------------------│
│ email_id (FK)        │        │ basic_email_data           │
│ classification       │        │ priority_email_data        │
│ confidence           │        │ nonbusiness_email_data     │
└──────────┬───────────┘        └────────────────────────────┘
           │
           │ 1
           │
   ┌──────────────────┐
   │ email_actions     │
   │------------------│
   │ action_type      │
   │ payload (JSONB)  │
   └──────────────────┘
```

---

# 4. Table Definitions

## 4.1 emails (Core table)

This table stores all incoming emails.

Fields:

* id (Primary Key)
* thread_id
* sender_name
* sender_email
* subject
* body
* date_received (optional)

This is the single source of truth for email content.

---

## 4.2 email_processing

This table stores AI classification results for each email.

Fields:

* email_id (Foreign Key → emails.id)
* classification (Basic, Priority, NonBusiness)
* confidence (float)
* reasoning (text)

This table tracks how the AI interpreted the email.

---

## 4.3 basic_email_data

Stores additional processing results for Basic emails.

Fields:

* email_id (Primary Key, Foreign Key → emails.id)
* rag_query
* rag_response

Only Basic emails have entries in this table.

---

## 4.4 priority_email_data

Stores additional metadata for Priority emails.

Fields:

* email_id (Primary Key, Foreign Key → emails.id)
* priority_type (legal, vip_client, meeting, etc.)
* client_tier

Only Priority emails have entries in this table.

---

## 4.5 nonbusiness_email_data

Stores metadata for NonBusiness emails.

Fields:

* email_id (Primary Key, Foreign Key → emails.id)
* reason
* notes

Only NonBusiness emails have entries in this table.

---

# 5. Data Flow

## Step 1: Email ingestion

Incoming email is stored in the emails table.

## Step 2: AI processing

The email is passed to the AI system and the result is stored in email_processing.

## Step 3: Classification routing

Based on classification:

* Basic → stored in basic_email_data
* Priority → stored in priority_email_data
* NonBusiness → stored in nonbusiness_email_data

## Step 4: Optional execution

Automation actions triggered by processing are stored in email_actions.

---

# 6. Data Insertion Flow

The insertion flow follows this sequence:

1. Insert raw email into emails table
2. Run AI processing
3. Insert result into email_processing
4. Insert category-specific data based on classification

Pseudo workflow:

```python
email = insert_email(inbound_email)

processed = run_ai(email)

insert_email_processing(email.id, processed)

if processed.classification == "Basic":
    insert_basic_email_data(email.id, ...)

elif processed.classification == "Priority":
    insert_priority_email_data(email.id, ...)

else:
    insert_nonbusiness_email_data(email.id, ...)
```

---

# 7. Why not separate email tables per category

An alternative approach would be:

* basic_emails
* priority_emails
* nonbusiness_emails

This design was rejected for the following reasons:

### 7.1 Data duplication

Each table would repeat:

* sender_email
* subject
* body
* thread metadata

### 7.2 Complex queries

Cross-category queries would require UNION operations.

### 7.3 Poor scalability

Adding a new category requires a new full email table.

### 7.4 Analytics complexity

Aggregations across categories become inefficient.

---

# 8. Benefits of the chosen design

### 8.1 Single source of truth

All emails are stored in one table.

### 8.2 Clean separation of concerns

Category-specific logic is isolated in dedicated tables.

### 8.3 Flexible extension

New categories can be added without modifying existing schema.

### 8.4 Simple analytics

All global queries operate on a single table.

---

# 9. Summary

This design follows a core principle:

> Store core data once, extend behavior through related tables.

It ensures:

* simplicity in core storage
* flexibility in AI processing
* scalability for future features
* clean separation between data and behavior
