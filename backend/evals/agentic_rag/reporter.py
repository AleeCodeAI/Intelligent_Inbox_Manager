import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from schemas import EvalResult, EvalError, EvalSummary, MetricStats, CategoryStats

METRIC_NAMES = ["accuracy", "faithfulness", "relevance", "completeness", "citations_quality"]


class Reporter:
    def __init__(self):
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        self._jsonl_path: Path | None = None

    def init_run(self, timestamp: str):
        self._jsonl_path = self.results_dir / f"eval_results_{timestamp}.jsonl"

    def save_result(self, result: EvalResult):
        if not self._jsonl_path:
            raise RuntimeError("Reporter not initialized. Call init_run() first.")
        with open(self._jsonl_path, "a", encoding="utf-8") as f:
            f.write(result.model_dump_json() + "\n")

    def save_error(self, error: EvalError):
        if not self._jsonl_path:
            raise RuntimeError("Reporter not initialized. Call init_run() first.")
        with open(self._jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "error", **error.model_dump(mode="json")}) + "\n")

    def _compute_metric_stats(self, results: list[EvalResult], metric_name: str) -> MetricStats:
        levels = [
            getattr(r.judge_output.metrics, metric_name).value
            for r in results
        ]
        total = len(levels)
        high_count = levels.count("HIGH")
        medium_count = levels.count("MEDIUM")
        low_count = levels.count("LOW")
        high_percentage = round((high_count / total) * 100, 1) if total else 0.0

        return MetricStats(
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            high_percentage=high_percentage,
            passed=high_percentage >= 60.0,
        )

    def _compute_category_stats(self, results: list[EvalResult]) -> dict[str, CategoryStats]:
        grouped: dict[str, list[EvalResult]] = defaultdict(list)
        for r in results:
            grouped[r.eval_input.category].append(r)

        category_stats = {}
        for category, cat_results in grouped.items():
            passed = sum(
                1 for r in cat_results
                if all(
                    getattr(r.judge_output.metrics, m).value == "HIGH"
                    for m in METRIC_NAMES
                )
            )
            confidences = [r.judge_output.confidence for r in cat_results]
            avg_confidence = round(sum(confidences) / len(confidences), 3) if confidences else 0.0

            category_stats[category] = CategoryStats(
                total=len(cat_results),
                passed=passed,
                failed=len(cat_results) - passed,
                avg_confidence=avg_confidence,
            )

        return category_stats

    def generate_summary(
        self,
        results: list[EvalResult],
        errors: list[EvalError],
        total_time_seconds: float,
        session_id: str,
    ) -> EvalSummary:
        metrics_stats = {
            name: self._compute_metric_stats(results, name)
            for name in METRIC_NAMES
        }

        confidences = [r.judge_output.confidence for r in results]
        avg_confidence = round(sum(confidences) / len(confidences), 3) if confidences else 0.0
        high_confidence_count = sum(1 for c in confidences if c >= 0.9)
        high_confidence_percentage = round((high_confidence_count / len(results)) * 100, 1) if results else 0.0
        confidence_passed = high_confidence_percentage >= 60.0
        all_metrics_passed = all(s.passed for s in metrics_stats.values())
        overall_passed = all_metrics_passed and confidence_passed

        passed = sum(
            1 for r in results
            if all(
                getattr(r.judge_output.metrics, m).value == "HIGH"
                for m in METRIC_NAMES
            )
        )

        return EvalSummary(
            total=len(results) + len(errors),
            passed=passed,
            failed=len(results) - passed,
            error_count=len(errors),
            errors=errors,
            high_confidence_count=high_confidence_count,
            high_confidence_percentage=high_confidence_percentage,
            confidence_passed=confidence_passed,
            avg_confidence=avg_confidence,
            total_time_seconds=round(total_time_seconds, 2),
            metrics=metrics_stats,
            category_stats=self._compute_category_stats(results),
            overall_passed=overall_passed,
        )

    def generate_md_report(self, summary: EvalSummary, session_id: str) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = self.results_dir / f"eval_report_{timestamp}.md"

        overall_status = "PASSED" if summary.overall_passed else "FAILED"
        confidence_status = "PASS" if summary.confidence_passed else "FAIL"

        lines = [
            "# RAG Evaluation Report",
            "",
            f"**Session ID:** `{session_id}`  ",
            f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC  ",
            f"**Overall Result:** {overall_status}",
            "",
            "---",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Examples | {summary.total} |",
            f"| Passed (all HIGH) | {summary.passed} |",
            f"| Failed | {summary.failed} |",
            f"| Errors | {summary.error_count} |",
            f"| Total Time | {summary.total_time_seconds}s |",
            f"| Avg Confidence | {summary.avg_confidence} |",
            f"| High Confidence (>=0.9) | {summary.high_confidence_count} ({summary.high_confidence_percentage}%) - {confidence_status} |",
            "",
            "---",
            "",
            "## Metrics Breakdown",
            "",
            "| Metric | HIGH | MEDIUM | LOW | HIGH % | Status |",
            "|--------|------|--------|-----|--------|--------|",
        ]

        for name, stats in summary.metrics.items():
            status = "PASS" if stats.passed else "FAIL"
            lines.append(
                f"| {name.replace('_', ' ').title()} | {stats.high_count} | {stats.medium_count} | {stats.low_count} | {stats.high_percentage}% | {status} |"
            )

        lines += [
            "",
            "---",
            "",
            "## Results by Category",
            "",
            "| Category | Total | Passed | Failed | Avg Confidence |",
            "|----------|-------|--------|--------|----------------|",
        ]

        for category, stats in summary.category_stats.items():
            lines.append(
                f"| {category} | {stats.total} | {stats.passed} | {stats.failed} | {stats.avg_confidence} |"
            )

        if summary.errors:
            lines += [
                "",
                "---",
                "",
                f"## Errors ({summary.error_count})",
                "",
            ]
            for err in summary.errors:
                lines += [
                    f"### {err.question[:60]}",
                    f"- **Type:** {err.error_type}",
                    f"- **Message:** {err.error_message}",
                    f"- **Time:** {err.timestamp}",
                    "",
                ]

        report_path.write_text("\n".join(lines), encoding="utf-8")
        return report_path