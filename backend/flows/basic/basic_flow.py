import logging
from openai import OpenAI
import asyncio

from schemas import InboundEmail
from database import insert_basic, mark_basic_reviewed
from flows.basic.agentic_rag.agentic_rag import AgenticRag

from utils.send_email import send_to_n8n
from utils.color import Logger
from utils.template import render_email

from schemas import BasicLLMInput, BasicEmailResponse
from prompts import BASIC_SYSTEM_PROMPT

from .basic_observability import BasicFlowObservability  

from configs import MainSettings

logging.basicConfig(level=logging.INFO, format="%(message)s")


class BasicFlow(Logger):
    """
    BasicFlow
    ---------
    End-to-end pipeline for handling inbound emails.

    Receives a parsed inbound email, runs it through the agentic RAG pipeline
    to generate a context-aware answer, composes a reply via LLM, renders it
    into an HTML email, and delivers it via n8n.

    All steps are persisted to the database and traced in Langfuse under the
    same session as the RAG pipeline using the email's thread ID.
    """
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

    def _build_llm_input(self, email: InboundEmail, session_id: str) -> BasicLLMInput:
        rag_reply = asyncio.run(
            self.rag.answer_question(query=email.body, session_id=session_id)
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
            f"Their email:\n{llm_input.message}\n\n"
            f"RAG reply:\n{llm_input.rag_answer}"
        )
        return [
            {"role": "system", "content": BASIC_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

    def _call_llm(
            self, 
            llm_input: BasicLLMInput, 
            obs: BasicFlowObservability
            ) -> BasicEmailResponse:

        providers = [
            ("Groq", self.groq, self.gpt_oss_model),
            ("OpenRouter", self.openrouter, self.gpt_oss_model),
        ]

        messages = self._make_messages(llm_input)
        system_prompt = messages[0]["content"]
        user_content = messages[1]["content"]

        obs.start_generation(
            system_prompt=system_prompt, 
            user_content=user_content
            )  

        last_error = None
        for provider_name, client, model in providers:
            try:
                self.log(f"Trying LLM provider: {provider_name}")

                completion = client.beta.chat.completions.parse(
                    model=model,
                    messages=messages,
                    response_format=BasicEmailResponse,
                    temperature=0.7,
                )
                
                response = completion.choices[0].message.parsed
                usage = completion.usage
                
                if not response:
                    raise ValueError(f"Failed to parse response from {provider_name}")
                
                # Validate the response
                if response.answered == "TRUE" and not response.body:
                    raise ValueError("TRUE answered but empty body")
                
                obs.end_generation(
                    output=f"answered={response.answered}, body_length={len(response.body)}",
                    model=model,
                    provider=provider_name,
                    input_tokens=usage.prompt_tokens if usage else 0,
                    output_tokens=usage.completion_tokens if usage else 0,
                    cost=getattr(usage, 'cost', 0) or 0,
                )

                self.log(f"{provider_name} returned answered={response.answered}")
                return response

            except Exception as e:
                last_error = e
                self.log(f"{provider_name} failed: {e}")

        self.log("All LLM providers failed")
        raise last_error

    def _send(self, email_id: str, html_body: str, obs: BasicFlowObservability):  

        obs.start_send_span()
        last_error = None
        for attempt in range(1, self.settings.N8N_MAX_RETRIES + 1):
            try:
                self.log(f"Attempt {attempt} to send email via n8n for email ID: {email_id}")
                result = send_to_n8n(
                    {
                        "id": email_id, 
                        "body": html_body, 
                        "email_type": "BASIC"
                    }
                )
                
                if result["status"] == "failed":
                    raise RuntimeError(f"n8n returned failed status for email ID: {email_id}")
                
                self.log(f"Send status: {result['status']}  id: {result['emailId']}")
                obs.end_send_span(
                    status=result["status"],
                    attempts=attempt,
                    email_id=result["emailId"],
                )
                return result

            except Exception as e:
                last_error = e
                self.log(f"Attempt {attempt} failed for email ID: {email_id} — {e}")
                if attempt == self.settings.N8N_MAX_RETRIES:
                    obs.end_send_span(status="failed", attempts=attempt, email_id=email_id)  
                    self.log(f"All {self.settings.N8N_MAX_RETRIES} attempts failed for email ID: {email_id}")
                    raise last_error

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self, email: InboundEmail, email_db_id: str) -> BasicEmailResponse:
        self.log(f"Processing {email.gmail_id} from {email.sender_email}")

        obs = BasicFlowObservability()
        obs.start_trace(
            thread_id=email.thread_id,
            gmail_id=email.gmail_id,
            sender_email=email.sender_email,
            sender_name=email.sender_name,
            subject=email.subject,
            body=email.body,
        )

        basic_inserted = False # Tracks whether a basic_flow record was already created to avoid duplicates.
        llm_input = None # Holds the RAG output so it can be persisted if later steps fail.

        try:
            self.log(f"Step 1: Building LLM input for email {email.gmail_id}")
            obs.start_rag_span()
            llm_input = self._build_llm_input(email, session_id=email.thread_id)
            obs.end_rag_span()

            self.log(f"Step 2: Calling LLM for email {email.gmail_id}")
            response = self._call_llm(llm_input, obs)

            # Handle unanswered case (answered = FALSE)
            if response.answered == "FALSE":
                self.log(f"LLM returned unanswered for email {email.gmail_id} - insufficient information to reply")
                
                # Insert as failed automation with specific reason
                insert_basic(
                    email_db_id=email_db_id,
                    rag_answer=llm_input.rag_answer,
                    rag_status="failed",
                    citations=[c.model_dump() for c in llm_input.citations] if llm_input.citations else None,
                    failure_reason="Insufficient information in RAG context to answer the email",
                    needs_manual_reply=True,
                )
                basic_inserted = True
                
                obs.finish_trace(output="answered=FALSE")
                obs.score_failure(reason="answered=FALSE - insufficient information")
                
                return response

            # For answered == TRUE, proceed with sending the email
            self.log(
                f"Step 3: Rendering in HTML the LLM response: "
                f"{response.body[:60]}..."
            )
            html = render_email(email.sender_name, response.body)

            self.log(f"Step 4: Sending email {email.gmail_id} via n8n")
            result = self._send(email.gmail_id, html, obs)

            self.log(
                f"Email reply sent for email: "
                f"{email.gmail_id} with status: {result['status']}"
            )

            self.log(
                f"Step 5: Inserting email {email.gmail_id} "
                f"into database for basic_flow table"
            )
            insert_basic(
                email_db_id=email_db_id,
                rag_answer=llm_input.rag_answer,
                rag_status=result["status"],
                citations=[c.model_dump() for c in llm_input.citations],
                needs_manual_reply=False,
            )
            basic_inserted = True

            self.log(
                f"Step 6: Marking email {email.gmail_id} as reviewed in database"
            )
            try:
                mark_basic_reviewed(email_db_id=email_db_id)
            except Exception as review_error:
                self.log(
                    f"Failed to mark email {email.gmail_id} "
                    f"as reviewed: {review_error}"
                )

            obs.finish_trace(output=response.body)
            obs.score_success()

            self.log(f"Done for : {email.gmail_id}")
            return response

        except Exception as exc:
            self.log(f"Failed: {email.gmail_id} — {exc}")

            obs.finish_trace(output="")
            obs.score_failure(reason=str(exc))

            if not basic_inserted:
                self.log(f"basic_inserted=False, attempting failure insert for {email.gmail_id}")
                try:
                    insert_basic(
                            email_db_id=email_db_id,
                            rag_answer=(
                                llm_input.rag_answer
                                if llm_input and llm_input.rag_answer
                                else None
                            ),
                            citations=(
                                [c.model_dump() for c in llm_input.citations]
                                if llm_input and llm_input.citations
                                else None
                            ),
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
                answered="FALSE",
                body=""
            )

if __name__ == "__main__":
    flow = BasicFlow()
    # Example usage with a dummy email
    dummy_email = InboundEmail(
        gmail_id="19e7308507c0640f",
        thread_id="19e7308507c0640f",
        sender_name="Tony Stark",
        sender_email="testemail00@gmail.com",
        subject="Partnership proposal for marketing campaign",
        body="Hey, we have a purely promotional partnership opportunity to hype up a new AI tool. Would you be open to this collaboration? It has no defined execution plan yet.",
        date="2024-01-01T12:00:00Z"
        )
    flow.run(dummy_email, email_db_id="2e1d9b6d-4512-4bbc-b15c-44394261c516")