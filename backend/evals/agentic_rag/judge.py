import json
from openai import OpenAI

from utils.color import Logger
from configs import MainSettings
from prompts import JUDGE_SYSTEM_PROMPT
from schemas import JudgeOutput, JudgeMetrics, MetricLevel


def _build_user_prompt(
    question: str,
    reference_answer: str,
    generated_answer: str,
    citations: list[dict],
) -> str:
    citations_text = "\n".join(
        f"- [{c.get('file', 'unknown')}]: {c.get('quote', '')}"
        for c in citations
    )
    return (
        f"Question: {question}\n\n"
        f"Reference Answer:\n{reference_answer}\n\n"
        f"Generated Answer:\n{generated_answer}\n\n"
        f"Citations used:\n{citations_text}"
    )


class Judge(Logger):
    name: str = "Judge"
    color: str = Logger.CYAN

    def __init__(self):
        settings = MainSettings()
        self.client = OpenAI(
            base_url=settings.GROQ_URL,
            api_key=settings.GROQ_API_KEY,
        )
        self.model = settings.GROQ_JUDGE_MODEL
        self.log(f"Judge initialized | model={self.model}")

    def evaluate(
        self,
        question: str,
        reference_answer: str,
        generated_answer: str,
        citations: list[dict],
    ) -> JudgeOutput:
        self.log(f"Evaluating: {question[:60]}...")

        user_prompt = _build_user_prompt(
            question=question,
            reference_answer=reference_answer,
            generated_answer=generated_answer,
            citations=citations,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
        )

        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)

        output = JudgeOutput(
            metrics=JudgeMetrics(
                accuracy=MetricLevel(data["metrics"]["accuracy"]),
                faithfulness=MetricLevel(data["metrics"]["faithfulness"]),
                relevance=MetricLevel(data["metrics"]["relevance"]),
                completeness=MetricLevel(data["metrics"]["completeness"]),
                citations_quality=MetricLevel(data["metrics"]["citations_quality"]),
            ),
            confidence=float(data["confidence"]),
            reasoning=data["reasoning"],
        )

        self.log(
            f"Evaluated | confidence={output.confidence} "
            f"accuracy={output.metrics.accuracy.value} "
            f"faithfulness={output.metrics.faithfulness.value} "
            f"relevance={output.metrics.relevance.value}"
        )

        return output