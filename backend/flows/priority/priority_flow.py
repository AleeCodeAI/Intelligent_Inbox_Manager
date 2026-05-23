import uuid
import logging
from openai import OpenAI

from schemas import InboundEmail
from database import insert_email
from database import insert_priority
from .priority_observability import PriorityFlowObservability
from utils.color import Logger

from schemas import PriorityResult
from prompts import PRIORITY_SYSTEM_PROMPT

from configs import MainSettings

logging.basicConfig(level=logging.INFO, format="%(message)s")


class PriorityFlow(Logger):
    """
    Classifies incoming emails by priority using an LLM.
    Tries Groq first, falls back to OpenRouter if it fails.
    Persists both the raw email and classification result to the database.

    Args:
        email (InboundEmail): The incoming email to classify.

    Returns:
        PriorityResult: The classification result containing priority type, confidence score, and reasoning.

    Raises:
        Exception: If all LLM providers fail or database insertion fails.
    """

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
        {email.body}
        """

    def _make_messages(self, email: InboundEmail) -> list[dict]:
        """Construct messages for the LLM."""
        return [
            {"role": "system", "content": PRIORITY_SYSTEM_PROMPT},
            {"role": "user", "content": self._user_prompt(email)},
        ]

    def _call_llm(self, email: InboundEmail, obs: PriorityFlowObservability) -> PriorityResult:
        self.log("Calling LLM providers for classification...")

        providers = [
            ("Groq", self.groq, self.gpt_oss_model),
            ("OpenRouter", self.openrouter, self.gpt_oss_model),
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
                    response_format=PriorityResult,
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

    def run(self, email: InboundEmail) -> PriorityResult:
        """Classify email priority and return results."""
        self.log(f"Running PriorityFlow for email: {email.subject}")

        uuid_id = str(uuid.uuid4())
        obs = PriorityFlowObservability()

        obs.start_trace(
            gmail_id=email.gmail_id,
            thread_id=email.thread_id,
            sender_email=email.sender_email,
            sender_name=email.sender_name,
            subject=email.subject,
            body=email.body,
        )

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
            result = self._call_llm(email, obs)

            self.log(f"Inserting priority result for email {email.gmail_id} into database for priorities table")
            insert_priority(
                email_db_id=uuid_id, 
                data=result, 
                reviewed=False
                )

            obs.finish_trace(result)
            obs.score_success()

            self.log(f"PriorityFlow completed successfully for email: {email.subject}")
            return result

        except Exception as e:
            obs.score_failure(str(e))
            self.log(f"PriorityFlow failed for email: {email.subject} with error: {e}")
            raise

if __name__ == "__main__":
    flow = PriorityFlow()

    email = InboundEmail(
        gmail_id="19e4f235400a0e36",
        thread_id="19e4f235400a0e36",
        sender_name="Dr. Aris Vance",
        sender_email="testemail00@gmail.com",
        subject="Request for Architecture Review Appointment",
        date="2026-05-22 10:02:56+00:00",
        body="""
Hi, I am looking to schedule a 30-minute consultation meeting next Tuesday to review our agent workflow design choices. Please let me know your availability so we can confirm an appointment.
"""
    )

    result = flow.run(email)
    print("============== Answer ==============")
    print(f"Priority Type: {result.priority_type}")
    print(f"Confidence: {result.confidence}")
    print(f"Reasoning: {result.reasoning}")