import uuid
import logging
from openai import OpenAI
import asyncio

from schemas import InboundEmail
from database import insert_email
from database import insert_basic, mark_basic_reviewed
from flows.basic.agentic_rag.agentic_rag import AgenticRag
from .send_email import send_to_n8n
from utils.color import Logger

from schemas import BasicLLMInput, BasicEmailResponse
from prompts import BASIC_SYSTEM_PROMPT
from .template import render_email

from configs import MainSettings

logging.basicConfig(level=logging.INFO, format="%(message)s")


class BasicFlow(Logger):
    name = "BasicFlow"
    color = Logger.TURQUOISE

    def __init__(self):
        self.log("Initializing BasicFlow...")
        self.settings = MainSettings()
        self.openrouter = OpenAI(
            api_key=self.settings.OPENROUTER_API_KEY,
            base_url=self.settings.OPENROUTER_URL,
        )
        self.groq = OpenAI(
            api_key=self.settings.GROQ_API_KEY,
            base_url=self.settings.GROQ_URL,
        )
        self.gpt_oss_model = self.settings.GPT_OSS_MODEL
        self.gpt_nano_model = self.settings.GPT_NANO_MODEL
        self.rag = AgenticRag()
        self.log("Initialized BasicFlow")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_llm_input(self, email: InboundEmail) -> BasicLLMInput:
        rag_reply = asyncio.run(
            self.rag.answer_question(query=email.body, session_id="basic_flow_test_session")
        )
        return BasicLLMInput(
            sender_name=email.sender_name,
            sender_email=email.sender_email,
            message=email.body,
            rag_answer=rag_reply.answer,
            citations=rag_reply.citations,
        )

    def _make_messages(self, llm_input: BasicLLMInput) -> list[dict]:
        user_content = (
            f"Sender name: {llm_input.sender_name}\n"
            f"Sender email: {llm_input.sender_email}\n\n"
            f"Their email:\n{llm_input.message}\n\n"
            f"RAG reply:\n{llm_input.rag_answer}"
        )
        return [
            {"role": "system", "content": BASIC_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

    def _call_llm(self, llm_input: BasicLLMInput) -> BasicEmailResponse:
        raw = self.openrouter.chat.completions.create(
            model=self.gpt_oss_model,
            messages=self._make_messages(llm_input),
        )
        body = raw.choices[0].message.content.strip()
        return BasicEmailResponse(body=body)

    def _send(self, email_id: str, html_body: str) -> None:
        result = send_to_n8n({"id": email_id, "body": html_body})
        self.log(f"Send status: {result['status']}  id: {result['emailId']}")

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self, email: InboundEmail) -> BasicEmailResponse:
        self.log(f"Processing {email.gmail_id} from {email.sender_email}")

        # Always persist the raw inbound email first
        self.log(f"Inserting email {email.gmail_id} into database for emails table")
        uuid_id = str(uuid.uuid4())
        insert_email(
            email_db_id=uuid_id,
            gmail_id=email.gmail_id,
            thread_id=email.thread_id,
            sender_name=email.sender_name,
            sender_email=email.sender_email,
            subject=email.subject,
            body=email.body,
        )

        try:
            self.log(f"Step 1: Building LLM input for email {email.gmail_id}")
            llm_input = self._build_llm_input(email)

            self.log(f"Step 2: Calling LLM for email {email.gmail_id}")
            response = self._call_llm(llm_input)

            self.log(f"Step 3: Rendering in HTML the LLM response: {response.body[:60]}...")
            html = render_email(email.sender_name, response.body)

            self.log(f"Step 4: Sending email {email.gmail_id} via n8n")
            self._send(email.gmail_id, html)
            self.log(f"Email reply sent successfully for email: {email.gmail_id}")

            self.log(f"Step 5: Inserting email {email.gmail_id} into database for basic_flow table")
            insert_basic(
                email_db_id=uuid_id,
                rag_answer=llm_input.rag_answer,
                rag_status="success",
                citations=[c.model_dump() for c in llm_input.citations],
                needs_manual_reply=False,
            )

            self.log(f"Step 6: Marking email {email.gmail_id} as reviewed in database")
            mark_basic_reviewed(email_db_id=uuid_id)

            self.log(f"Done for : {email.gmail_id}")
            return response

        except Exception as exc:
            self.log(f"Failed: {email.gmail_id} — {exc}")
            insert_basic(
                email_db_id=uuid_id,
                rag_status="failed",
                failure_reason=str(exc),
                needs_manual_reply=True,
            )
            return BasicEmailResponse(
                body="The system could not generate a response. This email has been flagged for manual review."
            )

if __name__ == "__main__":
    flow = BasicFlow()
    
    email = InboundEmail(
        gmail_id="19e364c001fc1245",
        thread_id="19e364c001fc1245",
        sender_name="Sarah Chen",
        sender_email="testemail00@gmail.com",
        subject="Mentorship Request for Applied AI",
        date="2026-05-17 14:16:51+00:00",
        body="""
Hello! I am an early professional working on a practical AI project. I am interested in your short-term mentorship for project guidance and system design reviews. Can you confirm if you offer paid
"""
    )

    response = flow.run(email)
    print(response)