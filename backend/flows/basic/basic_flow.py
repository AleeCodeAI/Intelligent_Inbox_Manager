import os
import uuid
import logging
from openai import OpenAI

from schemas import InboundEmail
from database import insert_email
from database import insert_basic
from flows.basic.agentic_rag.agentic_rag import AgenticRag
from .send_email import send_to_n8n
from utils.color import Logger

from schemas import AgentInput, EmailResponse
from prompts import BASIC_SYSTEM_PROMPT
from .template import render_email

from configs import MainSettings

logging.basicConfig(level=logging.INFO, format="%(message)s")


class BasicFlow(Logger):
    name = "BasicFlow"
    color = Logger.GREEN

    def __init__(self):
        self.settings = MainSettings()
        self.model = self.settings.GPT_NANO_MODEL
        self.openrouter = OpenAI(
            api_key=self.settings.OPENROUTER_API_KEY,
            base_url=self.settings.OPENROUTER_URL,
        )
        self.groq = OpenAI(
            api_key=self.settings.GROQ_API_KEY,
            base_url=self.settings.GROQ_URL,
        )
        self.rag = AgenticRag()
        self.log("Initialized BasicFlow")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_agent_input(self, email: InboundEmail) -> AgentInput:
        rag_reply = self.rag.answer_question(email.body or "")
        return AgentInput(
            sender_name=email.sender_name,
            sender_email=email.sender_email,
            message=email.body or "",
            rag_reply=rag_reply.answer,
        )

    def _make_messages(self, agent_input: AgentInput) -> list[dict]:
        user_content = (
            f"Sender name: {agent_input.sender_name}\n"
            f"Sender email: {agent_input.sender_email}\n\n"
            f"Their message:\n{agent_input.message}\n\n"
            f"RAG reply:\n{agent_input.rag_reply}"
        )
        return [
            {"role": "system", "content": BASIC_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

    def _call_llm(self, agent_input: AgentInput) -> EmailResponse:
        raw = self.openrouter.chat.completions.create(
            model=self.model,
            messages=self._make_messages(agent_input),
        )
        body = raw.choices[0].message.content.strip()
        return EmailResponse(body=body)

    def _send(self, email_id: str, html_body: str) -> None:
        result = send_to_n8n({"id": email_id, "body": html_body})
        self.log(f"Send status: {result['status']}  id: {result['emailId']}")

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self, email: InboundEmail) -> EmailResponse:
        self.log(f"Processing {email.id} from {email.sender_email}")

        # Always persist the raw inbound email first
        insert_email(
            id=str(uuid.uuid4()),
            email_id=email.id,
            thread_id=email.thread_id,
            sender_name=email.sender_name,
            sender_email=email.sender_email,
            subject=email.subject,
            body=email.body,
        )

        try:
            agent_input = self._build_agent_input(email)
            response = self._call_llm(agent_input)
            html = render_email(email.sender_name, response.body)
            self._send(email.id, html)

            insert_basic(
                email_id=email.id,
                rag_response=agent_input.rag_reply,
                rag_status="success",
            )
            self.log(f"Done: {email.id}")
            return response

        except Exception as exc:
            self.log(f"Failed: {email.id} — {exc}")
            insert_basic(
                email_id=email.id,
                rag_status="failed",
                failure_reason=str(exc),
                needs_manual_reply=True,
            )
            return EmailResponse(
                body="The system could not generate a response. This email has been flagged for manual review."
            )