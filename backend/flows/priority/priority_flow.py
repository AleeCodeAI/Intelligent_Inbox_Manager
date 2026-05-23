import uuid
import logging
from openai import OpenAI

from schemas import InboundEmail
from database import insert_email
from database import insert_priority
from utils.color import Logger

from schemas import PriorityResult
from prompts import PRIORITY_SYSTEM_PROMPT

from configs import MainSettings

logging.basicConfig(level=logging.INFO, format="%(message)s")


class PriorityFlow(Logger):
    name: str = "PriorityFlow"
    color: str = Logger.MAGENTA

    def __init__(self):
        self.log("Initializing PriorityFlow...")

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

        self.log("Initialized PriorityFlow")

    # ------------------------------------------------------------------
    # Internal Methods
    # ------------------------------------------------------------------

    def _user_prompt(self, email: InboundEmail) -> str:
        """Format email data for classification."""
        return f"""
        Subject: {email.subject}
        Message:
        {email.message}
        """

    def _make_messages(self, email: InboundEmail) -> list[dict]:
        """Construct messages for the LLM."""
        return [
            {"role": "system", "content": PRIORITY_SYSTEM_PROMPT},
            {"role": "user", "content": self._user_prompt(email)},
        ]

    def _call_llm(self, email: InboundEmail) -> PriorityResult:
        self.log("Calling LLM providers for classification...")

        providers = [
            ("Groq", self.groq, self.gpt_oss_model),
            ("OpenRouter", self.openrouter, self.gpt_oss_model),
        ]

        messages = self._make_messages(email)

        last_error = None
        for provider_name, client, model in providers:
            try:
                self.log(f"Trying LLM provider: {provider_name}")

                raw = client.chat.completions.parse(
                    model=model,
                    messages=messages,
                    response_format=PriorityResult,  
                )

                result = raw.choices[0].message.parsed  
                usage = raw.usage

                self.log(f"{provider_name} response generated successfully")
                self.log(f"Tokens used: {usage.total_tokens}, Prompt tokens: {usage.prompt_tokens}, Completion tokens: {usage.completion_tokens}")
                return result

            except Exception as e:
                last_error = e
                self.log(f"{provider_name} failed: {e}")

        self.log("All LLM providers failed")
        raise last_error

    # ------------------------------------------------------------------
    # Main Flow Method
    # ------------------------------------------------------------------

    def run(self, email: InboundEmail) -> PriorityResult:
        """Classify email priority and return results."""
        self.log(f"Running PriorityFlow for email: {email.subject}")

        uuid_id = str(uuid.uuid4())
        
        try:
            self.log(f"Inserting email {email.gmail_id} into database for emails table")
            
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

        try:
            result = self._call_llm(email)

            self.log(f"Inserting priority result for email {email.gmail_id} into database for priorities table")
            insert_priority(
                priority_db_id=str(uuid.uuid4()),
                email_db_id=uuid_id,
                priority_type=result.priority_type,
                confidence=result.confidence,
                reasoning=result.reasoning,
            )

            self.log(f"PriorityFlow completed successfully for email: {email.subject}")
            return result
        
        except Exception as e:
            self.log(f"PriorityFlow failed for email: {email.subject} with error: {e}")
            raise