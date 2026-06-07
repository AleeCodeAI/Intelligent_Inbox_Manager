from .email_repo import insert_email
from .basic_repo import insert_basic

FAILED_EMAILS = [
    {
        "email": {
            "email_db_id": "test-email-001",
            "gmail_id": "gmail-test-001",
            "thread_id": "thread-test-001",
            "sender_name": "John Doe",
            "sender_email": "john@example.com",
            "subject": "Question about mentorship",
            "body": "Can you tell me more about your mentorship program?",
        },
        "basic": {
            "rag_status": "failed",
            "rag_answer": None,
            "citations": None,
            "failure_reason": "No relevant documents retrieved",
            "needs_manual_reply": True,
        },
    },
    {
        "email": {
            "email_db_id": "test-email-002",
            "gmail_id": "gmail-test-002",
            "thread_id": "thread-test-002",
            "sender_name": "Sarah Smith",
            "sender_email": "sarah@example.com",
            "subject": "AI consulting rates",
            "body": "What are your AI consulting rates?",
        },
        "basic": {
            "rag_status": "failed",
            "rag_answer": "Our AI consulting services are available at $50/hour.",
            "citations": [],
            "failure_reason": "Answer generated but failed citation validation",
            "needs_manual_reply": True,
        },
    },
    {
        "email": {
            "email_db_id": "test-email-003",
            "gmail_id": "gmail-test-003",
            "thread_id": "thread-test-003",
            "sender_name": "Michael Brown",
            "sender_email": "michael@example.com",
            "subject": "Technical support",
            "body": "Do you support LangGraph deployments?",
        },
        "basic": {
            "rag_status": "failed",
            "rag_answer": "Yes, we provide full LangGraph deployment support.",
            "citations": [],
            "failure_reason": "Response not supported by retrieved context",
            "needs_manual_reply": True,
        },
    },
    {
        "email": {
            "email_db_id": "test-email-004",
            "gmail_id": "gmail-test-004",
            "thread_id": "thread-test-004",
            "sender_name": "Emily Davis",
            "sender_email": "emily@example.com",
            "subject": "Partnership inquiry",
            "body": "Would you be interested in a strategic partnership?",
        },
        "basic": {
            "rag_status": "failed",
            "rag_answer": None,
            "citations": None,
            "failure_reason": "Vector search timeout",
            "needs_manual_reply": True,
        },
    },
    {
        "email": {
            "email_db_id": "test-email-005",
            "gmail_id": "gmail-test-005",
            "thread_id": "thread-test-005",
            "sender_name": "David Wilson",
            "sender_email": "david@example.com",
            "subject": "Machine learning mentorship",
            "body": "Do you offer mentorship for machine learning engineers?",
        },
        "basic": {
            "rag_status": "failed",
            "rag_answer": "We offer mentorship for aspiring machine learning engineers.",
            "citations": [
                {
                    "source": "knowledge_base",
                    "title": "Mentorship Overview",
                }
            ],
            "failure_reason": "Confidence score below threshold",
            "needs_manual_reply": True,
        },
    },
]


def seed_failed_emails():
    for item in FAILED_EMAILS:
        email = insert_email(**item["email"])

        insert_basic(
            email_db_id=email.email_db_id,
            **item["basic"],
        )

        print(f"Inserted {email.email_db_id}")


if __name__ == "__main__":
    seed_failed_emails()