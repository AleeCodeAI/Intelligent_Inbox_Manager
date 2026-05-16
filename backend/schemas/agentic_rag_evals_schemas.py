from __future__ import annotations
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class MetricLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EvalInput(BaseModel):
    question: str
    keywords: list[str]
    reference_answer: str
    category: str


class JudgeMetrics(BaseModel):
    accuracy: MetricLevel
    faithfulness: MetricLevel
    relevance: MetricLevel
    completeness: MetricLevel
    citations_quality: MetricLevel


class JudgeOutput(BaseModel):
    metrics: JudgeMetrics
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class KeywordCoverage(BaseModel):
    matched: list[str]
    missed: list[str]
    coverage_score: float = Field(ge=0.0, le=1.0)


class EvalError(BaseModel):
    question: str
    error_type: str
    error_message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EvalResult(BaseModel):
    eval_input: EvalInput
    rag_answer: str
    rag_citations: list[dict]
    keyword_coverage: KeywordCoverage
    judge_output: JudgeOutput
    session_id: str
    latency_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MetricStats(BaseModel):
    high_count: int
    medium_count: int
    low_count: int
    high_percentage: float
    passed: bool  # True if high_percentage >= 60%

class CategoryStats(BaseModel):
    total: int
    passed: int
    failed: int
    avg_confidence: float


class EvalSummary(BaseModel):
    total: int
    passed: int
    failed: int
    error_count: int
    errors: list[EvalError]
    high_confidence_count: int
    high_confidence_percentage: float
    confidence_passed: bool
    avg_confidence: float
    total_time_seconds: float
    metrics: dict[str, MetricStats]
    category_stats: dict[str, CategoryStats]
    overall_passed: bool

