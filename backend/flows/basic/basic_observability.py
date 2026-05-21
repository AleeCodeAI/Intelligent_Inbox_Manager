import base64
import httpx
from datetime import datetime, timezone
from uuid import uuid4

from configs import MainSettings


class BasicFlowObservability:
    """
    Langfuse observability for BasicFlow.

    Tracks one trace per inbound email with:
      - A span for the RAG/LLM-input build step   (duration only)
      - A generation for the LLM call             (model, tokens, provider, latency)
      - A span for the n8n send step              (status, attempts)
      - A final score                             (success=1 / failure=0)
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

        # IDs kept in instance state so helpers can reference them
        self._trace_id: str | None = None
        self._rag_span_id: str | None = None
        self._generation_id: str | None = None
        self._send_span_id: str | None = None

        # Wallclock anchors for latency calculations
        self._trace_start: datetime | None = None
        self._rag_start: datetime | None = None
        self._gen_start: datetime | None = None
        self._send_start: datetime | None = None

    # ------------------------------------------------------------------
    # 1. Trace — one per email, opened at the start of BasicFlow.run()
    # ------------------------------------------------------------------

    def start_trace(
        self,
        session_id: str,
        gmail_id: str,
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
                    "name": "basic-flow-email",
                    "sessionId": session_id,
                    "input": body,
                    "tags": ["basic-flow", "email"],
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
    # 2. RAG-input span — wraps _build_llm_input (duration only)
    # ------------------------------------------------------------------

    def start_rag_span(self) -> None:
        self._rag_span_id = str(uuid4())
        self._rag_start = datetime.now(timezone.utc)

        self._ingest([
            {
                "id": str(uuid4()),
                "type": "span-create",
                "timestamp": self._rag_start.isoformat(),
                "body": {
                    "id": self._rag_span_id,
                    "traceId": self._trace_id,
                    "name": "build-llm-input (rag)",
                    "startTime": self._rag_start.isoformat(),
                },
            }
        ])

    def end_rag_span(self) -> None:
        if not self._rag_span_id:
            return
        end = datetime.now(timezone.utc)
        latency_ms = _ms(self._rag_start, end)

        self._ingest([
            {
                "id": str(uuid4()),
                "type": "span-update",
                "timestamp": end.isoformat(),
                "body": {
                    "id": self._rag_span_id,
                    "traceId": self._trace_id,
                    "endTime": end.isoformat(),
                    "metadata": {"latency_ms": latency_ms},
                },
            }
        ])

    # ------------------------------------------------------------------
    # 3. LLM generation — wraps _call_llm
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
                    "name": "compose-reply",
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
        output: str,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
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
                    "output": output,
                    "usage": {
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": input_tokens + output_tokens,
                        "unit": "TOKENS",
                    },
                    "metadata": {
                        "provider": provider,
                        "latency_ms": _ms(self._gen_start, end),
                    },
                },
            }
        ])

    # ------------------------------------------------------------------
    # 4. Send span — wraps _send (n8n delivery)
    # ------------------------------------------------------------------

    def start_send_span(self) -> None:
        self._send_span_id = str(uuid4())
        self._send_start = datetime.now(timezone.utc)

        self._ingest([
            {
                "id": str(uuid4()),
                "type": "span-create",
                "timestamp": self._send_start.isoformat(),
                "body": {
                    "id": self._send_span_id,
                    "traceId": self._trace_id,
                    "name": "send-via-n8n",
                    "startTime": self._send_start.isoformat(),
                },
            }
        ])

    def end_send_span(self, status: str, attempts: int, email_id: str) -> None:
        if not self._send_span_id:
            return
        end = datetime.now(timezone.utc)

        self._ingest([
            {
                "id": str(uuid4()),
                "type": "span-update",
                "timestamp": end.isoformat(),
                "body": {
                    "id": self._send_span_id,
                    "traceId": self._trace_id,
                    "endTime": end.isoformat(),
                    "metadata": {
                        "status": status,
                        "attempts": attempts,
                        "n8n_email_id": email_id,
                        "latency_ms": _ms(self._send_start, end),
                    },
                },
            }
        ])

    # ------------------------------------------------------------------
    # 5. Trace close + score
    # ------------------------------------------------------------------

    def finish_trace(self, output: str) -> None:
        """Close the trace with the final reply body."""
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
                    "output": output,
                    "metadata": {
                        "total_latency_ms": _ms(self._trace_start, end),
                    },
                },
            }
        ])

    def score_success(self, comment: str = "Reply sent successfully.") -> None:
        self._score("basic-flow-success", 1, comment)

    def score_failure(self, reason: str) -> None:
        self._score("basic-flow-failure", 0, reason)

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