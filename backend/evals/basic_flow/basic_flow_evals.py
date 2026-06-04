from openai import OpenAI
from configs import MainSettings
from flows import BasicFlow
from flows.basic.basic_observability import BasicFlowObservability
from schemas import BasicLLMInput, BasicFlowEvalJudgeInput, BasicFlowEvalJudgeOutput
from prompts import BASIC_FLOW_JUDGE_PROMPT
from utils.color import Logger
from pathlib import Path
import json
import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

class BasicFlowEvaluator(Logger):
    name: str = "BasicFlowEvaluator"
    color: str = Logger.BLUE

    def __init__(self):
        self.settings = MainSettings()
        self.openrouter = OpenAI(
            api_key=self.settings.OPENROUTER_API_KEY,
            base_url=self.settings.OPENROUTER_URL,
        )
        self.groq = OpenAI(
            api_key=self.settings.GROQ_API_KEY,
            base_url=self.settings.GROQ_URL,
        )
        self.gpt_oss_model = self.settings.GPT_OSS_MODEL
        self.gpt_nano_model = self.settings.GPT_NANO_MODEL

        base = Path(__file__).parent
        self.data_path = base.parent / "data" / "basic_test_data.jsonl"
        self.output_dir = base / "results"
        self.run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_file = self.output_dir / f"basic_flow_results_{self.run_id}.jsonl"
        self.summary_file = self.output_dir / f"basic_flow_summary_{self.run_id}.md"
        self.flow = BasicFlow()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.log("BasicFlowEvaluator Initialized!")

    def load_data(self) -> list[BasicLLMInput]:
        self.log(f"Loading data from {self.data_path}...")
        data: list[BasicLLMInput] = []
        with open(self.data_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    item = json.loads(line)
                    data.append(BasicLLMInput(**item))
        return data

    def _make_messages(self, llm_input: BasicFlowEvalJudgeInput) -> list[dict]:
        user_content = (
            f"Original Message:\n{llm_input.original_message}\n\n"
            f"RAG reply:\n{llm_input.rag_answer}\n\n"
            f"Generated Reply:\n{llm_input.generated_reply}\n\n"
        )
        return [
            {"role": "system", "content": BASIC_FLOW_JUDGE_PROMPT},
            {"role": "user", "content": user_content},
        ]

    def _judge(self, llm_input: BasicFlowEvalJudgeInput) -> BasicFlowEvalJudgeOutput:
        self.log("Calling LLM providers for evaluation...")

        providers = [
            ("Groq", self.groq, self.gpt_oss_model),
            ("OpenRouter", self.openrouter, self.gpt_oss_model),
        ]

        messages = self._make_messages(llm_input)

        last_error = None
        for provider_name, client, model in providers:
            try:
                self.log(f"Trying LLM provider: {provider_name}")

                raw = client.chat.completions.parse(
                    model=model,
                    messages=messages,
                    response_format=BasicFlowEvalJudgeOutput,
                    temperature=0.0,
                )

                result = raw.choices[0].message.parsed
                usage = raw.usage
                cost = getattr(usage, 'cost', 0) or 0

                self.log(f"{provider_name} response generated successfully")
                self.log(f"Tokens used: {usage.total_tokens}, Prompt tokens: {usage.prompt_tokens}, Completion tokens: {usage.completion_tokens} and total cost: ${cost:.8f}")
                return result

            except Exception as e:
                last_error = e
                self.log(f"{provider_name} failed: {e}")

        self.log("All LLM providers failed")
        raise last_error

    def _write_summary(self, results: list[dict]) -> None:
        total = len(results)
        good = sum(1 for r in results if r["evaluation"]["verdict"] == "GOOD")
        bad = total - good
        pass_rate = (good / total * 100) if total > 0 else 0.0

        lines = [
            f"# BasicFlow Eval Summary — {self.run_id}",
            "",
            "| Metric     | Value         |",
            "|------------|---------------|",
            f"| Total      | {total}        |",
            f"| GOOD       | {good}         |",
            f"| BAD        | {bad}          |",
            f"| Pass Rate  | {pass_rate:.1f}% |",
            "",
            "---",
            "",
            "## Per-Case Breakdown",
            "",
        ]

        for idx, r in enumerate(results, start=1):
            verdict = r["evaluation"]["verdict"]
            reasoning = r["evaluation"]["reasoning"]
            original = r["original_message"][:120].replace("\n", " ")
            generated = r["generated_reply"][:300].replace("\n", " ")  # a bit more room for the reply
            lines += [
                f"### Case {idx} — {verdict}",
                f"**Original message (truncated):** {original}",
                "",
                f"**Generated reply (truncated):** {generated}",
                "",
                f"**Reasoning:** {reasoning}",
                "",
            ]

        self.summary_file.write_text("\n".join(lines), encoding="utf-8")
        self.log(f"Summary saved → {self.summary_file}")

    def run(self):
        self.log("Step 1: Starting BasicFlow evaluation...")
        data = self.load_data()
        results = []
        for idx, item in enumerate(data):
            self.log(f"Step 2: Evaluating item {idx + 1}/{len(data)}...")
            try:
                self.log("Running the BasicFlow pipeline...")
                basic_result = self.flow._call_llm(item, obs=BasicFlowObservability())

                self.log("Evaluating the generated reply with the judge LLM...")
                judge_output = self._judge(BasicFlowEvalJudgeInput(
                    original_message=item.message,
                    rag_answer=item.rag_answer,
                    generated_reply=basic_result.body,
                ))
                results.append({
                    "original_message": item.message,
                    "rag_answer": item.rag_answer,
                    "generated_reply": basic_result.body,
                    "evaluation": judge_output.model_dump(),
                })
                self.log(f"Item {idx + 1} evaluated with verdict: {judge_output.verdict}")

                self.log("Saving results...")
                with open(self.results_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(results[-1]) + "\n")

            except Exception as e:
                self.log(f"Error evaluating item {idx + 1}: {e}")
                continue

        self.log("Step 3: Writing summary report...")
        self._write_summary(results)
        good = sum(1 for r in results if r["evaluation"]["verdict"] == "GOOD")
        self.log(f"Evaluation complete. {good}/{len(results)} GOOD ({good/len(results)*100:.1f}% pass rate)")
        self.log("Evaluation complete.")


if __name__ == "__main__":
    evaluator = BasicFlowEvaluator()
    evaluator.run()