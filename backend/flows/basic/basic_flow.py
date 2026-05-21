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
        providers = [
            ("Groq", self.groq, self.gpt_oss_model),
            ("OpenRouter", self.openrouter, self.gpt_oss_model),
        ]

        last_error = None

        for provider_name, client, model in providers:
            try:
                self.log(f"Trying LLM provider: {provider_name}")

                raw = client.chat.completions.create(
                    model=model,
                    messages=self._make_messages(llm_input),
                )

                body = raw.choices[0].message.content

                if not body or not body.strip():
                    raise ValueError(f"Empty response from {provider_name}")

                body = body.strip()

                self.log(f"{provider_name} response generated successfully")
                return BasicEmailResponse(body=body)

            except Exception as e:
                last_error = e
                self.log(f"{provider_name} failed: {e}")

        self.log("All LLM providers failed")
        raise last_error

    def _send(self, email_id: str, html_body: str):
        for attempt in range(1, self.settings.N8N_MAX_RETRIES + 1):
            try:
                self.log(f"Attempt {attempt} to send email via n8n for email ID: {email_id}")
                result = send_to_n8n({"id": email_id, "body": html_body})
                self.log(f"Send status: {result['status']}  id: {result['emailId']}")
                return result
            except Exception as e:
                self.log(f"Attempt {attempt} failed to send email ID: {email_id} with error: {e}")
                if attempt == self.settings.N8N_MAX_RETRIES:
                    self.log(f"All attempts failed to send email ID: {email_id}")
                    raise 

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

        basic_inserted = False

        try:
            self.log(f"Step 1: Building LLM input for email {email.gmail_id}")

            llm_input = self._build_llm_input(email)

            self.log(f"Step 2: Calling LLM for email {email.gmail_id}")

            response = self._call_llm(llm_input)

            self.log(
                f"Step 3: Rendering in HTML the LLM response: "
                f"{response.body[:60]}..."
            )

            html = render_email(email.sender_name, response.body)

            self.log(f"Step 4: Sending email {email.gmail_id} via n8n")

            result = self._send(email.gmail_id, html)

            self.log(
                f"Email reply sent successfully for email: "
                f"{email.gmail_id} with status: {result['status']}"
            )

            self.log(
                f"Step 5: Inserting email {email.gmail_id} "
                f"into database for basic_flow table"
            )

            insert_basic(
                email_db_id=uuid_id,
                rag_answer=llm_input.rag_answer,
                rag_status=result["status"],
                citations=[c.model_dump() for c in llm_input.citations],
                needs_manual_reply=False,
            )

            basic_inserted = True

            self.log(
                f"Step 6: Marking email {email.gmail_id} "
                f"as reviewed in database"
            )

            try:
                mark_basic_reviewed(email_db_id=uuid_id)

            except Exception as review_error:
                self.log(
                    f"Failed to mark email {email.gmail_id} "
                    f"as reviewed: {review_error}"
                )

            self.log(f"Done for : {email.gmail_id}")

            return response

        except Exception as exc:
            self.log(f"Failed: {email.gmail_id} — {exc}")

            if not basic_inserted:
                try:
                    insert_basic(
                        email_db_id=uuid_id,
                        rag_status="failed",
                        failure_reason=str(exc),
                        needs_manual_reply=True,
                    )

                except Exception as db_error:
                    self.log(
                        f"Failed to insert failure state for "
                        f"{email.gmail_id}: {db_error}"
                    )

            return BasicEmailResponse(
                body=(
                    "The system could not generate a response. "
                    "This email has been flagged for manual review."
                )
            )

if __name__ == "__main__":
    flow = BasicFlow()
    
    email = InboundEmail(
        gmail_id="19e364c2373f3087",
        thread_id="19e364c2373f3087",
        sender_name="Amanda Seyfried",
        sender_email="testemail00@gmail.com",
        subject="Prompt engineering rate inquiry",
        date="2026-05-17 14:16:59+00:00",
        body="""
Hello, I need some assistance with prompt design, evaluation, and LLM integration to ensure consistent behavior in our app. What is your specific hourly rate for Large Language Models (LLMs) work?
"""
    )

    response = flow.run(email)
    print(response)