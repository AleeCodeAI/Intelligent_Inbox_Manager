import uuid
import logging
from datetime import datetime, timezone
from openai import OpenAI

from schemas import (
    InboundEmail,
    InboundEmailBatch,
    EmailProcessed,
    ExecutorResult,
)

from database import (
    insert_email,
    get_email_by_thread,
    insert_processing,
)

from .executor_observability import ExecutorObservability
from .email_receiver import EmailReceiver
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

        self.email_receiver = EmailReceiver()

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

        obs.start_generation(
            system_prompt=system_prompt,
            user_content=user_content,
        )

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
                cost = getattr(usage, "cost", 0) or 0

                obs.end_generation(
                    result=result,
                    model=model,
                    provider=provider_name,
                    input_tokens=usage.prompt_tokens if usage else 0,
                    output_tokens=usage.completion_tokens if usage else 0,
                    cost=cost,
                )

                self.log(f"{provider_name} response generated successfully")

                self.log(
                    f"Tokens used: {usage.total_tokens}, "
                    f"Prompt tokens: {usage.prompt_tokens}, "
                    f"Completion tokens: {usage.completion_tokens}, "
                    f"Total cost: ${cost:.8f}"
                )

                return result

            except Exception as e:
                last_error = e
                self.log(f"{provider_name} failed: {e}")

        self.log("All LLM providers failed")
        raise last_error

    # ------------------------------------------------------------------
    # Single Email Processor
    # ------------------------------------------------------------------

    def _process_email(self, email: InboundEmail) -> EmailProcessed | None:
        self.log(f"Running Executor for email: {email.subject}")

        existing = get_email_by_thread(email.thread_id)
        if existing:
            self.log(f"Thread {email.thread_id} already exists in database, skipping.")
            return None

        uuid_id = str(uuid.uuid4())  # This is your email_db_id
        obs = ExecutorObservability()

        obs.start_trace(
            gmail_id=email.gmail_id,
            thread_id=email.thread_id,
            sender_email=email.sender_email,
            sender_name=email.sender_name,
            subject=email.subject,
            body=email.body,
        )

        email_inserted = False

        try:
            self.log(f"Inserting email {email.gmail_id} into database")
            insert_email(
                email_db_id=uuid_id,  # ← This is the key
                gmail_id=email.gmail_id,
                thread_id=email.thread_id,
                sender_name=email.sender_name,
                sender_email=email.sender_email,
                subject=email.subject,
                body=email.body,
            )
            email_inserted = True

            result = self._call_llm(email, obs)
            self.log(f"Classification result: {result.classification} (confidence: {result.confidence})")

            # Pass email_db_id to the flows
            if result.classification == "BASIC":
                self.log("Routing to BasicFlow...")
                BasicFlow().run(email, email_db_id=uuid_id)  # ← Make sure your flow accepts this
            elif result.classification == "PRIORITY":
                self.log("Routing to PriorityFlow...")
                PriorityFlow().run(email, email_db_id=uuid_id)  # ← Make sure your flow accepts this
            elif result.classification == "NON_BUSINESS":
                self.log("Routing to NonBusinessFlow...")
                NonBusinessFlow().run(email, email_db_id=uuid_id)  # ← Make sure your flow accepts this
            else:
                self.log(f"Unknown classification: {result.classification}, skipping routing.")

            processed = EmailProcessed(
                gmail_id=email.gmail_id,
                result=result,
                processed_date=datetime.now(timezone.utc),
                success=True,
            )

            self.log(f"Inserting processing result for email {processed.gmail_id} into database")
            insert_processing(email_db_id=uuid_id, data=processed)  # ← Added email_db_id

            obs.finish_trace(processed)
            obs.score_success()

            self.log(f"Executor completed successfully for email: {email.subject}")
            return processed

        except Exception as e:
            fallback_result = ExecutorResult(
                classification="UNKNOWN",
                confidence=0.0,
                reasoning=f"Executor failed: {str(e)}",
            )

            processed = EmailProcessed(
                gmail_id=email.gmail_id,
                result=result if "result" in locals() else fallback_result,
                processed_date=datetime.now(timezone.utc),
                success=False,
            )

            if email_inserted:
                insert_processing(email_db_id=uuid_id, data=processed)  # ← Added email_db_id

            obs.score_failure(str(e))
            self.log(f"Executor failed for email: {email.subject} with error: {e}")
            return processed

    # ------------------------------------------------------------------
    # Main Batch Runner
    # ------------------------------------------------------------------

    def run(self) -> list[EmailProcessed]:
        self.log("Fetching emails from EmailReceiver...")

        batch: InboundEmailBatch = self.email_receiver.get_emails()

        self.log(f"Fetched {batch.total} emails")

        processed_emails: list[EmailProcessed] = []

        for email in batch.emails:
            try:
                self.log(
                    f"Processing email "
                    f"{email.gmail_id} "
                    f"({email.subject})"
                )

                result = self._process_email(email)

                if result:
                    processed_emails.append(result)

            except Exception as e:
                self.log(
                    f"Failed processing email "
                    f"{email.gmail_id}: {e}"
                )

        self.log(
            f"Executor finished. "
            f"Successfully processed "
            f"{len(processed_emails)} emails."
        )

        return processed_emails

if __name__ == "__main__":
    executor = Executor()

    try:
        results = executor.run()

        print("\n" + "=" * 50)
        print("EXECUTOR FINISHED")
        print(f"Processed Emails: {len(results)}")
        print("=" * 50)

        for result in results:
            print(
                f"- {result.gmail_id} | "
                f"{result.result.classification} | "
                f"Success: {result.success}"
            )

    except Exception as e:
        print(f"\nExecutor crashed: {e}")