from flows import BasicFlow
from flows.basic.basic_observability import BasicFlowObservability
from schemas import BasicLLMInput, BasicEmailResponse
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
    
    def evaluate_sample(self, data: BasicLLMInput) -> BasicEmailResponse:
        self.log(f"Evaluating sample: {data.id} | {data.input_text[:50]}...")

        obs = BasicFlowObservability()
        self.flow._call_llm(data, obs)
        pass

        