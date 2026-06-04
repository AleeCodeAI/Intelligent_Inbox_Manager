from flows import BasicFlow
from flows.basic.basic_observability import BasicFlowObservability
from schemas import BasicLLMInput
from utils.color import Logger
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

class BasicFlowRunner(Logger):
    name: str = "BasicFlowRunner"
    color: str = Logger.TURQUOISE

    def __init__(self):
        base = Path(__file__).parent
        self.data_path = base.parent.parent / "data" / "basic_test_data.jsonl"
        self.flow = BasicFlow()
        self.basic_flow_storage_path = base / "basic_flow_storage.jsonl"

        self.log("BasicFlowRunner Initialized!")

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
    
    def run(self):
        self.log(f"Running basic flow on data from {self.data_path}...")

        obs = BasicFlowObservability()
        data = self.load_data()
        storage_data: list[dict] = []
        for item in data:
            result = self.flow._call_llm(item, obs)
            result = {
                "message": item.message,
                "rag_answer": item.rag_answer,
                "answer": result.body,
            }
            storage_data.append(result)

        
        with open(self.basic_flow_storage_path, "w", encoding="utf-8") as f:
            for item in storage_data:
                json.dump(item, f)
                f.write("\n")
        
        self.log(f"Basic flow run complete! Results stored in {self.basic_flow_storage_path}")
        return storage_data
    
if __name__ == "__main__":
    runner = BasicFlowRunner()
    runner.run()