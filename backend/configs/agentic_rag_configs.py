from pydantic_settings import BaseSettings

class AgenticRAGConfig(BaseSettings):
    """
    Configuration for the Agentic RAG system.
    """
    GREP_TIMEOUT_SECONDS: int = 30
    READ_MAX_LINES: int = 200
    AGENT_REQUEST_LIMIT: int = 20