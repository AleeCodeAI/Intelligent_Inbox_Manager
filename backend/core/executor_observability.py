import base64
import httpx
from datetime import datetime, timezone
from uuid import uuid4
import json

from configs import MainSettings
from schemas import ExecutorResult, EmailProcessed


class ExecutorObservability:
    """
    Langfuse observability for Executor.

    Tracks one trace per inbound email with:
      - A generation for the LLM classification call  (model, tokens, provider, cost, latency)
      - A final score                                  (success=1 / failure=0)
    """

    def __init__(self):
        configs = MainSettings()
        self.host = configs.LANGFUSE_HOST

        credentials = f"{configs.LANGFUSE_PUBLIC_KEY}:{configs.LANGFUSE_SECRET_KEY}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
        }

        self._trace_id: str | None = None
        self._generation_id: str | None = None

        self._trace_start: datetime | None = None
        self._gen_start: datetime | None = None

    # ------------------------------------------------------------------
    # 1. Trace — one per email, opened at the start of Executor.run()
    # ------------------------------------------------------------------

    def start_trace(
            self,
            gmail_id: str,
            thread_id: str,
            sender_email: str,
            sender_name: str,
            subject: str,
            body: str,
            ) -> None:

        self._trace_id = str(uuid4())
        self._trace_start = datetime.now(timezone.utc)

        self._ingest([
            {
                "id": str(uuid4()),
                "type": "trace-create",
                "timestamp": self._trace_start.isoformat(),
                "body": {
                    "id": self._trace_id,
                    "name": "executor-email",
                    "sessionId": thread_id,
                    "input": body,
                    "tags": ["executor", "email"],
                    "metadata": {
                        "gmail_id": gmail_id,
                        "sender_email": sender_email,
                        "sender_name": sender_name,
                        "subject": subject,
                    },
                },
            }
        ])

    # ------------------------------------------------------------------
    # 2. LLM generation — wraps _call_llm
    # ------------------------------------------------------------------

    def start_generation(self, system_prompt: str, user_content: str) -> None:
        self._generation_id = str(uuid4())
        self._gen_start = datetime.now(timezone.utc)

        self._ingest([
            {
                "id": str(uuid4()),
                "type": "generation-create",
                "timestamp": self._gen_start.isoformat(),
                "body": {
                    "id": self._generation_id,
                    "traceId": self._trace_id,
                    "name": "executor-classify-email",
                    "startTime": self._gen_start.isoformat(),
                    "input": {
                        "system": system_prompt,
                        "user": user_content,
                    },
                },
            }
        ])

    def end_generation(
        self,
        result: ExecutorResult,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        cost: float = 0.0,
    ) -> None:
        if not self._generation_id:
            return
        end = datetime.now(timezone.utc)

        self._ingest([
            {
                "id": str(uuid4()),
                "type": "generation-update",
                "timestamp": end.isoformat(),
                "body": {
                    "id": self._generation_id,
                    "traceId": self._trace_id,
                    "endTime": end.isoformat(),
                    "model": model,
                    "output": json.dumps(result.model_dump()),
                    "usage": {
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": input_tokens + output_tokens,
                        "unit": "TOKENS",
                        "totalCost": cost,
                    },
                    "metadata": {
                        "provider": provider,
                        "latency_ms": _ms(self._gen_start, end),
                        "classification": result.classification,
                        "confidence": result.confidence,
                    },
                },
            }
        ])

    # ------------------------------------------------------------------
    # 3. Trace close
    # ------------------------------------------------------------------

    def finish_trace(self, result: EmailProcessed) -> None:
        if not self._trace_id:
            return
        end = datetime.now(timezone.utc)

        self._ingest([
            {
                "id": str(uuid4()),
                "type": "trace-create",
                "timestamp": end.isoformat(),
                "body": {
                    "id": self._trace_id,
                    "output": json.dumps(result.model_dump(), default=str),
                    "metadata": {
                        "total_latency_ms": _ms(self._trace_start, end),
                        "classification": result.result.classification,
                        "confidence": result.result.confidence,
                        "success": result.success,
                        "processed_date": result.processed_date.isoformat(),
                    },
                },
            }
        ])

    # ------------------------------------------------------------------
    # 4. Score
    # ------------------------------------------------------------------

    def score_success(self, comment: str = "Email classified successfully.") -> None:
        self._score("executor-success", 1, comment)

    def score_failure(self, reason: str) -> None:
        self._score("executor-failure", 0, reason)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _score(self, name: str, value: int, comment: str) -> None:
        if not self._trace_id:
            return
        with httpx.Client() as client:
            client.post(
                f"{self.host}/api/public/scores",
                headers=self.headers,
                json={
                    "traceId": self._trace_id,
                    "name": name,
                    "value": value,
                    "comment": comment,
                },
            )

    def _ingest(self, batch: list[dict]) -> None:
        with httpx.Client() as client:
            client.post(
                f"{self.host}/api/public/ingestion",
                headers=self.headers,
                json={"batch": batch},
            )


# ------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------

def _ms(start: datetime | None, end: datetime) -> int | None:
    if start is None:
        return None
    return round((end - start).total_seconds() * 1000)