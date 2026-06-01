"""
the shcemas here are used for the evaluation of classifications, such as priority and non-business flow. They define the structure of the results and statistics that will be generated during the evaluation process.
"""

from pydantic import BaseModel, computed_field

class SampleResult(BaseModel):
    gmail_id: str
    subject: str
    expected: str
    predicted: str
    confidence: float
    reasoning: str

    @computed_field
    @property
    def passed(self) -> bool:
        return self.predicted == self.expected


class ClassStats(BaseModel):
    label: str
    total: int = 0
    correct: int = 0
    confidence_sum: float = 0.0

    @computed_field
    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @computed_field
    @property
    def avg_confidence(self) -> float:
        return self.confidence_sum / self.total if self.total else 0.0