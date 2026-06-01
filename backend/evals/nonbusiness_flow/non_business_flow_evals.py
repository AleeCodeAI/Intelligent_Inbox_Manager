import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock

from flows import NonBusinessFlow
from schemas import InboundEmail, NonBusinessResult, SampleResult, ClassStats
import logging
from utils.color import Logger

logging.basicConfig(level=logging.INFO, format="%(message)s")

class NonBusinessFlowEvaluator(Logger):
    name: str = "NonBusinessFlowEvaluator"
    color: str = Logger.GOLD

    def __init__(self, data_path: Path, output_dir: Path):
        self.data_path = data_path
        self.output_dir = output_dir
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_file = output_dir / f"non_business_flow_results_{self.run_id}.jsonl"
        self.summary_file = output_dir / f"non_business_flow_summary_{self.run_id}.md"
        self.flow = NonBusinessFlow()
        self.obs = Mock()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.log("NonBusinessFlowEvaluator Initialized!")

    # -------------------------
    # Data Loading
    # -------------------------

    def load_data(self) -> list[dict]:
        self.log(f"Loading data from {self.data_path}...")

        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")

        data_list = []
        with open(self.data_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data_list.append(json.loads(line))

        self.log(f"Loaded {len(data_list)} samples")
        return data_list

    # -------------------------
    # Single Sample
    # -------------------------

    def evaluate_sample(self, data: dict) -> SampleResult:
        self.log(f"Evaluating sample: {data['gmail_id']} | {data['subject']}")

        email = InboundEmail(
            gmail_id=data["gmail_id"],
            threadId=data["threadId"],
            senderName=data["senderName"],
            senderEmail=data["senderEmail"],
            subject=data["subject"],
            body=data["body"],
            date=data["date"],
        )

        result: NonBusinessResult = self.flow._call_llm(email=email, obs=self.obs)

        sample_result = SampleResult(
            gmail_id=data["gmail_id"],
            subject=data["subject"],
            expected=data["expected_classification"],
            predicted=result.nonbusiness_type,
            confidence=result.confidence,
            reasoning=result.reasoning,
        )

        status = "✅ PASS" if sample_result.passed else "❌ FAIL"
        self.log(f"{status} | expected: {sample_result.expected} | predicted: {sample_result.predicted} | confidence: {result.confidence:.2f}")

        return sample_result

    # -------------------------
    # Aggregation
    # -------------------------

    def compute_class_stats(self, results: list[SampleResult]) -> dict[str, ClassStats]:
        self.log("Computing per-class stats...")

        stats: dict[str, ClassStats] = {}

        for r in results:
            if r.expected not in stats:
                stats[r.expected] = ClassStats(label=r.expected)

            stats[r.expected].total += 1
            stats[r.expected].confidence_sum += r.confidence
            if r.passed:
                stats[r.expected].correct += 1

        for label, s in stats.items():
            self.log(f"{label} → {s.correct}/{s.total} ({s.accuracy:.2%}) | avg confidence: {s.avg_confidence:.2f}")

        return stats

    def compute_confusion(self, results: list[SampleResult]) -> dict[str, dict[str, int]]:
        self.log("Computing confusion matrix...")

        confusion: dict[str, dict[str, int]] = {}

        for r in results:
            if r.expected not in confusion:
                confusion[r.expected] = {}
            confusion[r.expected][r.predicted] = confusion[r.expected].get(r.predicted, 0) + 1

        return confusion

    # -------------------------
    # Run
    # -------------------------

    def run(self):
        self.log("Starting evaluation run...")

        dataset = self.load_data()

        results = []
        for sample in dataset:
            try:
                result = self.evaluate_sample(sample)
                results.append(result)
            except Exception as e:
                self.log(f"Sample {sample.get('gmail_id', 'UNKNOWN')} failed — skipping. Error: {e}")

        if not results:
            self.log("No results to evaluate. Exiting.")
            return

        total = len(results)
        correct = sum(1 for r in results if r.passed)
        accuracy = correct / total if total else 0

        self.log(f"Evaluation complete — {correct}/{total} passed ({accuracy:.2%})")

        class_stats = self.compute_class_stats(results)
        confusion = self.compute_confusion(results)

        self.write_results(results)
        self.write_summary(results, correct, class_stats, confusion)

        print(f"\nRun ID   : {self.run_id}")
        print(f"Total    : {total}")
        print(f"Passed   : {correct}")
        print(f"Failed   : {total - correct}")
        print(f"Accuracy : {accuracy:.2%}")
        print(f"Results  : {self.results_file}")
        print(f"Summary  : {self.summary_file}")

    # -------------------------
    # JSONL Output
    # -------------------------

    def write_results(self, results: list[SampleResult]):
        self.log(f"Writing results to {self.results_file}...")

        with open(self.results_file, "w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r.model_dump()) + "\n")

        self.log(f"Results written — {len(results)} samples")

    # -------------------------
    # Markdown Summary
    # -------------------------

    def write_summary(self, results: list[SampleResult], correct: int, class_stats: dict[str, ClassStats], confusion: dict[str, dict[str, int]]):
        self.log(f"Writing summary to {self.summary_file}...")

        total = len(results)
        accuracy = correct / total if total else 0

        md = []
        md.append("# Non-Business Flow Evaluation\n")
        md.append(f"**Run ID:** `{self.run_id}`")
        md.append(f"**Total:** {total} | **Passed:** {correct} | **Failed:** {total - correct} | **Accuracy:** {accuracy:.2%}\n")

        # Per-class performance
        md.append("## Per-Class Performance\n")
        for label, stats in class_stats.items():
            md.append(
                f"- **{label}** → {stats.correct}/{stats.total} "
                f"({stats.accuracy:.2%}) | avg confidence: {stats.avg_confidence:.2f}"
            )

        # Confusion matrix
        md.append("\n## Confusion Matrix\n")
        all_labels = sorted(class_stats.keys())
        md.append("| Actual \\ Predicted | " + " | ".join(all_labels) + " |")
        md.append("| --- " * (len(all_labels) + 1) + "|")
        for actual in all_labels:
            row = f"| **{actual}** |"
            for predicted in all_labels:
                count = confusion.get(actual, {}).get(predicted, 0)
                row += f" {count} |"
            md.append(row)

        # Failed samples
        failed = [r for r in results if not r.passed]
        md.append(f"\n## Failed Samples ({len(failed)})\n")
        if failed:
            for r in failed:
                md.append(f"### `{r.gmail_id}` — {r.subject}")
                md.append(f"- **Expected:** {r.expected}")
                md.append(f"- **Predicted:** {r.predicted}")
                md.append(f"- **Confidence:** {r.confidence:.2f}")
                md.append(f"- **Reasoning:** {r.reasoning[:200]}...")
                md.append("")
        else:
            md.append("_All samples passed._")

        md.append("\n---")
        md.append(f"_Generated by NonBusinessFlowEvaluator — Run `{self.run_id}`_")

        with open(self.summary_file, "w", encoding="utf-8") as f:
            f.write("\n".join(md))

        self.log("Summary written")


# -------------------------
# Entry Point
# -------------------------

if __name__ == "__main__":
    evaluator = NonBusinessFlowEvaluator(
        data_path=Path(__file__).parent.parent / "data" / "non_business_emails_test_data.jsonl",
        output_dir=Path(__file__).parent / "results",
    )
    evaluator.run()