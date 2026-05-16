import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from utils.color import Logger
from flows.basic.agentic_rag.agentic_rag import AgenticRag
from .judge import Judge
from .metrices import compute_keyword_coverage
from .reporter import Reporter
from schemas import EvalInput, EvalResult, EvalError

DATA_PATH = Path(__file__).parent.parent / "data" / "agentic_rag_test_data.jsonl"


class EvalRunner(Logger):
    name: str = "EvalRunner"
    color: str = Logger.CYAN

    def __init__(self):
        self.rag = AgenticRag()
        self.judge = Judge()
        self.reporter = Reporter()
        self.log("EvalRunner initialized")

    async def run(self):
        session_id = str(uuid4())
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.reporter.init_run(timestamp)

        examples: list[EvalInput] = []
        with open(DATA_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    examples.append(EvalInput(**data))

        self.log(f"Loaded {len(examples)} examples | session_id={session_id}")

        results = []
        errors = []
        pipeline_start = time.time()

        for i, example in enumerate(examples, 1):
            self.log(f"[{i}/{len(examples)}] {example.question[:60]}...")
            example_start = time.time()

            try:
                rag_result = await self.rag.answer_question(
                    query=example.question,
                    session_id=session_id,
                )

                citations_as_dicts = [c.model_dump() for c in rag_result.citations]

                keyword_coverage = compute_keyword_coverage(
                    answer=rag_result.answer,
                    keywords=example.keywords,
                )

                judge_output = self.judge.evaluate(
                    question=example.question,
                    reference_answer=example.reference_answer,
                    generated_answer=rag_result.answer,
                    citations=citations_as_dicts,
                )

                latency_ms = round((time.time() - example_start) * 1000)

                result = EvalResult(
                    eval_input=example,
                    rag_answer=rag_result.answer,
                    rag_citations=citations_as_dicts,
                    keyword_coverage=keyword_coverage,
                    judge_output=judge_output,
                    session_id=session_id,
                    latency_ms=latency_ms,
                    timestamp=datetime.utcnow(),
                )

                results.append(result)
                self.reporter.save_result(result)
                self.log(
                    f"Done | confidence={judge_output.confidence} "
                    f"keyword_coverage={keyword_coverage.coverage_score} "
                    f"latency={latency_ms}ms"
                )

            except Exception as e:
                error = EvalError(
                    question=example.question,
                    error_type=type(e).__name__,
                    error_message=str(e),
                )
                errors.append(error)
                self.reporter.save_error(error)
                self.log(f"Error | {type(e).__name__}: {e}")
                continue

        total_time = time.time() - pipeline_start

        summary = self.reporter.generate_summary(
            results=results,
            errors=errors,
            total_time_seconds=total_time,
            session_id=session_id,
        )

        report_path = self.reporter.generate_md_report(summary, session_id)
        self.log(f"Eval complete | {summary.passed}/{summary.total} passed | {summary.error_count} errors")
        self.log(f"Report: {report_path}")


if __name__ == "__main__":
    runner = EvalRunner()
    asyncio.run(runner.run())