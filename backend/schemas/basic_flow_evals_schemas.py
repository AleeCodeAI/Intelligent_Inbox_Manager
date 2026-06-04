from pydantic import BaseModel, Field
from typing import Literal

class BasicFlowEvalJudgeInput(BaseModel):
    original_message: str = Field(description="The inbound email message the system received")
    rag_answer: str = Field(description="The factual content retrieved to answer the message")
    generated_reply: str = Field(description="The email body produced by the pipeline")

class BasicFlowEvalJudgeOutput(BaseModel):
    verdict: Literal["GOOD", "BAD"] = Field(description="GOOD or BAD")
    reasoning: str = Field(description="The evaluator's reasoning process leading to the verdict")