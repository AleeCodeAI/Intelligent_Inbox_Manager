from openai import OpenAI
from configs import MainSettings
from utils.color import Logger
from schemas import BasicFlowEvalJudgeInput, BasicFlowEvalJudgeOutput
from prompts import BASIC_FLOW_JUDGE_PROMPT
import logging
from pathlib import Path
from datetime import datetime
import json 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BasicFlowEvalJudge(Logger):
    name: str = "BasicFlowEvalJudge"
    color: str = Logger.TURQUOISE

    def __init__(self, data_path: Path):
        self.log("Initializing BasicFlowEvalJudge...")
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

        self.data_path = data_path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        self.judge_critique_path = self.results_dir / f"judge_critique_{timestamp}.jsonl"
            
    def _load_data(self):
        self.log(f"importing data from: {self.data_path}")
        data: list[BasicFlowEvalJudgeInput] = []
        with open(self.data_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    item = json.loads(line)
                    data.append(BasicFlowEvalJudgeInput(
                        original_message=item["message"],
                        rag_answer=item["rag_answer"],
                        generated_reply=item["answer"],
                    ))
        return data
    
    def _make_messages(self, llm_input: BasicFlowEvalJudgeInput) -> list[dict]:
        user_content = (
            f"Original Message:\n{llm_input.original_message}\n\n"
            f"RAG reply:\n{llm_input.rag_answer}\n\n"
            f"Generated Reply:\n{llm_input.generated_reply}\n\n"
        )
        return [
            {"role": "system", "content": BASIC_FLOW_JUDGE_PROMPT},
            {"role": "user", "content": user_content},]
    
    def _call_llm(self, llm_input: BasicFlowEvalJudgeInput) -> BasicFlowEvalJudgeOutput:
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
    
    def run(self):
        data = self._load_data()
        self.log(f"Loaded {len(data)} items for evaluation")

        with open(self.judge_critique_path, "w", encoding="utf-8") as f:
            pass

        for idx, item in enumerate(data):
            self.log(f"Evaluating item {idx + 1}/{len(data)}")
            try:
                result = self._call_llm(item)
                with open(self.judge_critique_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(result.dict()) + "\n")
                self.log(f"Evaluation for item {idx + 1} completed and saved.")
            except Exception as e:
                self.log(f"Failed to evaluate item {idx + 1}: {e}")

if __name__ == "__main__":
    # basic_flow_storage.jsonl contains all good examples, basic_flow_storage_mix_of_good_bad_example.jsonl contains a mix of good and bad examples for more robust evaluation
    judge = BasicFlowEvalJudge(data_path=Path(__file__).parent / "basic_flow_storage_mix_of_good_bad_example.jsonl")
    judge.run()