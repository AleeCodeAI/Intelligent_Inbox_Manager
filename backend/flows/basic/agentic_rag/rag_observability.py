import httpx
import base64
from datetime import datetime, timezone
from uuid import uuid4
from configs import MainSettings


class RagObservability:
    def __init__(self):
        configs = MainSettings()
        self.host = configs.LANGFUSE_HOST
        self._trace_id = None
        self._generation_id = None
        self._start_time: datetime | None = None

        credentials = f"{configs.LANGFUSE_PUBLIC_KEY}:{configs.LANGFUSE_SECRET_KEY}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
        }

    def start_trace(self, session_id: str, query: str):
        self._trace_id = str(uuid4())
        self._generation_id = str(uuid4())
        self._start_time = datetime.now(timezone.utc)

        payload = {
            "batch": [
                {
                    "id": str(uuid4()),
                    "type": "trace-create",
                    "timestamp": self._start_time.isoformat(),
                    "body": {
                        "id": self._trace_id,
                        "name": "agentic-rag-answer",
                        "sessionId": session_id,
                        "input": query,
                        "tags": ["rag", "answer"],
                    },
                },
                {
                    "id": str(uuid4()),
                    "type": "generation-create",
                    "timestamp": self._start_time.isoformat(),
                    "body": {
                        "id": self._generation_id,
                        "traceId": self._trace_id,
                        "name": "rag-agent-run",
                        "startTime": self._start_time.isoformat(),
                        "input": query,
                    },
                },
            ]
        }
        self._ingest(payload)

    def update_trace(
        self,
        answer: str,
        citations: list,
        model: str,
        input_tokens: int,
        output_tokens: int,
        requests: int,
        cost: float,
    ):
        if not self._trace_id:
            return

        end_time = datetime.now(timezone.utc)
        latency_ms = (
            round((end_time - self._start_time).total_seconds() * 1000)
            if self._start_time else None
        )
        input_cost = round(cost * (input_tokens / max(input_tokens + output_tokens, 1)), 6)
        output_cost = round(cost - input_cost, 6)

        payload = {
            "batch": [
                {
                    "id": str(uuid4()),
                    "type": "trace-create",
                    "timestamp": end_time.isoformat(),
                    "body": {
                        "id": self._trace_id,
                        "output": answer,
                        "metadata": {
                            "citations": [c.model_dump() for c in citations],
                            "total_tokens": input_tokens + output_tokens,
                            "agent_requests": requests,
                            "latency_ms": latency_ms,
                        },
                    },
                },
                {
                    "id": str(uuid4()),
                    "type": "generation-update",
                    "timestamp": end_time.isoformat(),
                    "body": {
                        "id": self._generation_id,
                        "traceId": self._trace_id,
                        "model": model,
                        "endTime": end_time.isoformat(),
                        "output": answer,
                        "usage": {
                            "input": input_tokens,
                            "output": output_tokens,
                            "total": input_tokens + output_tokens,
                            "unit": "TOKENS",
                            "inputCost": input_cost,
                            "outputCost": output_cost,
                            "totalCost": cost,
                        },
                        "metadata": {
                            "agent_requests": requests,
                        },
                    },
                },
            ]
        }
        self._ingest(payload)

    def score_success(self, comment="Successfully answered question with proper citations from the source material."):
        self._score(name="rag-success", value=1, comment=comment)

    def score_failure(self, reason: str):
        self._score(name="rag-failure", value=0, comment=reason)

    def _score(self, name: str, value: int, comment: str):
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

    def _ingest(self, payload: dict):
        with httpx.Client() as client:
            client.post(
                f"{self.host}/api/public/ingestion",
                headers=self.headers,
                json=payload,
            )

    def flush(self):
        pass