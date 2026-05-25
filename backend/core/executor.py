import uuid
import logging
from datetime import datetime, timezone
from openai import OpenAI

from schemas import InboundEmail, EmailProcessed, ExecutorResult
from database import (
    insert_email,
    get_email_by_thread,
    insert_processing,
)

from .executor_observability import ExecutorObservability
from utils.color import Logger

from flows import (
    BasicFlow,
    PriorityFlow,
    NonBusinessFlow,
)

from prompts import EXECUTOR_SYSTEM_PROMPT
from configs import MainSettings

logging.basicConfig(level=logging.INFO, format="%(message)s")


class Executor(Logger):
    name: str = "EXECUTOR"
    color: str = Logger.VIOLET

    def __init__(self):
        self.log("Initializing EXECUTOR...")

        self.settings = MainSettings()
        self.openrouter = OpenAI(
            api_key=self.settings.OPENROUTER_API_KEY,
            base_url=self.settings.OPENROUTER_URL,
        )
        self.groq = OpenAI(
            api_key=self.settings.GROQ_API_KEY,
            base_url=self.settings.GROQ_URL,
        )
        self.gpt_nano_model = self.settings.GPT_NANO_MODEL
        self.gpt_oss_model = self.settings.GPT_OSS_MODEL

        self.log("Initialized EXECUTOR")

    # ------------------------------------------------------------------
    # Internal Methods
    # ------------------------------------------------------------------

    def _user_prompt(self, email: InboundEmail) -> str:
        return f"""
        Subject: {email.subject}
        Message:
        {email.body}
        """

    def _make_messages(self, email: InboundEmail) -> list[dict]:
        return [
            {"role": "system", "content": EXECUTOR_SYSTEM_PROMPT},
            {"role": "user", "content": self._user_prompt(email)},
        ]

    def _call_llm(self, email: InboundEmail, obs: ExecutorObservability) -> ExecutorResult:
        self.log("Calling LLM providers for classification...")

        providers = [
            ("Groq", self.groq, self.gpt_oss_model),
            ("OpenRouter", self.openrouter, self.gpt_nano_model),
        ]

        messages = self._make_messages(email)
        system_prompt = messages[0]["content"]
        user_content = messages[1]["content"]

        obs.start_generation(system_prompt=system_prompt, user_content=user_content)

        last_error = None
        for provider_name, client, model in providers:
            try:
                self.log(f"Trying LLM provider: {provider_name}")

                raw = client.chat.completions.parse(
                    model=model,
                    messages=messages,
                    response_format=ExecutorResult,
                    temperature=0.0,
                )

                result = raw.choices[0].message.parsed
                usage = raw.usage
                cost = getattr(usage, 'cost', 0) or 0

                obs.end_generation(
                    result=result,
                    model=model,
                    provider=provider_name,
                    input_tokens=usage.prompt_tokens if usage else 0,
                    output_tokens=usage.completion_tokens if usage else 0,
                    cost=cost,
                )

                self.log(f"{provider_name} response generated successfully")
                self.log(f"Tokens used: {usage.total_tokens}, Prompt tokens: {usage.prompt_tokens}, Completion tokens: {usage.completion_tokens} and total cost: ${cost:.8f}")
                return result

            except Exception as e:
                last_error = e
                self.log(f"{provider_name} failed: {e}")

        self.log("All LLM providers failed")
        raise last_error

    # ------------------------------------------------------------------
    # Main Flow Method
    # ------------------------------------------------------------------

    def run(self, email: InboundEmail) -> EmailProcessed:
        self.log(f"Running Executor for email: {email.subject}")

        # --- Deduplication: skip if thread already processed ---
        existing = get_email_by_thread(email.thread_id)
        if existing:
            self.log(f"Thread {email.thread_id} already exists in database, skipping.")
            return None

        uuid_id = str(uuid.uuid4())
        obs = ExecutorObservability()

        obs.start_trace(
            gmail_id=email.gmail_id,
            thread_id=email.thread_id,
            sender_email=email.sender_email,
            sender_name=email.sender_name,
            subject=email.subject,
            body=email.body,
        )

        # --- Insert raw email into database ---
        try:
            self.log(f"Inserting email {email.gmail_id} into database")
            insert_email(
                email_db_id=uuid_id,
                gmail_id=email.gmail_id,
                thread_id=email.thread_id,
                sender_name=email.sender_name,
                sender_email=email.sender_email,
                subject=email.subject,
                body=email.body,
            )
        except Exception as db_error:
            self.log(f"Failed to insert email {email.gmail_id} into database: {db_error}")
            raise

        # --- Classify and route ---
        try:
            result = self._call_llm(email, obs)

            self.log(f"Classification result: {result.classification} (confidence: {result.confidence})")

            if result.classification == "BASIC":
                self.log("Routing to BasicFlow...")
                BasicFlow().run(email)

            elif result.classification == "PRIORITY":
                self.log("Routing to PriorityFlow...")
                PriorityFlow().run(email)

            elif result.classification == "NON_BUSINESS":
                self.log("Routing to NonBusinessFlow...")
                NonBusinessFlow().run(email)

            else:
                self.log(f"Unknown classification: {result.classification}, skipping routing.")

            # --- Build EmailProcessed ---
            processed = EmailProcessed(
                gmail_id=email.gmail_id,
                result=result,
                processed_date=datetime.now(timezone.utc),
                success=True,
            )

            # --- Persist and observe ---
            insert_processing(email_db_id=uuid_id, data=processed)

            obs.finish_trace(processed)
            obs.score_success()

            self.log(f"Executor completed successfully for email: {email.subject}")
            return processed

        except Exception as e:
            fallback_result = ExecutorResult(
                classification="UNKNOWN",
                confidence=0.0,
                reasoning=f"Executor failed before classification: {str(e)}",
            )

            processed = EmailProcessed(
                gmail_id=email.gmail_id,
                result=result if 'result' in locals() else fallback_result,
                processed_date=datetime.now(timezone.utc),
                success=False,
            )

            insert_processing(gmail_id=email.gmail_id, data=processed)
            obs.score_failure(str(e))
            self.log(f"Executor failed for email: {email.subject} with error: {e}")
            raise