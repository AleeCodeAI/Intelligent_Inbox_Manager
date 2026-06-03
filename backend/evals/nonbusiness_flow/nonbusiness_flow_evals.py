from flows import NonBusinessFlow
from flows.non_business.nonbusiness_observability import NonBusinessFlowObservability
from schemas import InboundEmail
from utils.color import Logger
import logging
import json
import datetime
from pathlib import Path
from .summary_writer import write_summary

logging.basicConfig(level=logging.INFO, format="%(message)s")

class NonBusinessFlowEvaluator(Logger):
    name: str = "NonBusinessFlowEvaluator"
    color: str = Logger.GOLD

    def __init__(self):
        base = Path(__file__).parent
        self.data_path = base.parent / "data" / "non_business_emails_test_data.jsonl"
        self.output_dir = base / "results"
        self.run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_file = self.output_dir / f"non_business_flow_results_{self.run_id}.jsonl"
        self.summary_file = self.output_dir / f"non_business_flow_summary_{self.run_id}.md"
        self.flow = NonBusinessFlow()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.log("NonBusinessFlowEvaluator Initialized!")

    def load_data(self) -> list[dict]:
        self.log(f"Loading data from {self.data_path}...")
        emails: list[dict] = []
        with open(self.data_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    emails.append(json.loads(line))
        self.log(f"Loaded {len(emails)} samples")
        return emails

    def evaluate_sample(self, data: dict) -> dict:
        self.log(f"Evaluating sample: {data['gmail_id']} | {data['subject']}")

        email = InboundEmail(
            gmail_id=data["gmail_id"],
            thread_id=data["threadId"],
            sender_name=data["senderName"],
            sender_email=data["senderEmail"],
            subject=data["subject"],
            body=data["body"],
            date=data["date"],
        )

        obs = NonBusinessFlowObservability()
        result = self.flow._call_llm(email, obs)

        failures = []

        if result.nonbusiness_type not in ["PERSONAL", "PROMOTIONAL", "INFORMATIONAL", "SPAM"]:
            failures.append(f"Invalid nonbusiness_type: {result.nonbusiness_type}")
        if not (0.0 <= result.confidence <= 1.0):
            failures.append(f"Confidence out of range: {result.confidence}")
        if result.nonbusiness_type != data["expected_classification"]:
            failures.append(
                f"Non-business type mismatch: expected={data['expected_classification']}, got={result.nonbusiness_type}"
            )

        passed = len(failures) == 0

        return {
                "gmail_id": data["gmail_id"],
                "subject": data["subject"],
                "body": data["body"][:1000],
                "expected_classification": data["expected_classification"],

                "result": {
                    "nonbusiness_type": result.nonbusiness_type,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                },

                "passed": passed,
                "failures": failures,
            }
    
    def run(self):
        emails = self.load_data()
        all_results = []

        with open(self.results_file, "w", encoding="utf-8") as f:
            for data in emails:
                record = self.evaluate_sample(data)
                all_results.append(record)
                f.write(json.dumps(record) + "\n")
                status = "✅ PASS" if record["passed"] else "❌ FAIL"
                self.log(f"{status} — {record['gmail_id']}")

        self.log(f"Results saved to {self.results_file}")

        write_summary(
                results=all_results,
                run_id=self.run_id,
                summary_file=self.summary_file,
            )

if __name__ == "__main__":
    evaluator = NonBusinessFlowEvaluator()
    evaluator.run()