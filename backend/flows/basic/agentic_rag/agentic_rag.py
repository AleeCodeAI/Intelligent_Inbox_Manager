import logging
import asyncio
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from pydantic_ai import Agent, UsageLimits
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from utils.color import Logger
from configs import AgenticRAGConfig
from configs import MainSettings
from prompts import AGENTIC_RAG_PROMPT
from schemas import SearchAnswer
from .tools import AgenticRagTools
from .rag_observability import RagObservability

logging.basicConfig(level=logging.INFO, format="%(message)s")

load_dotenv()

NOTES_DIR = (Path(__file__).parent / "notes").resolve()


class AgenticRag(Logger):
    """ 
    Agentic RAG system that uses an LLM agent with file system tools 
    (grep, list_files, read_file) to search markdown notes and answer 
    questions with proper citations from the source material.
    """

    name: str = "AgenticRAG"
    color: str = Logger.GREEN

    def __init__(self):
        self.configs = AgenticRAGConfig()
        self.main_settings = MainSettings()
        self.model = self.main_settings.GPT_OSS_MODEL
        self.tools = AgenticRagTools(
            notes_dir=NOTES_DIR,
            grep_timeout_seconds=self.configs.GREP_TIMEOUT_SECONDS,
            read_max_lines=self.configs.READ_MAX_LINES,
            log_callback=self.log,
        )
        self.observability = RagObservability()
        self.log("AgenticRAG initialized")

    def _build_agent(self) -> Agent:
        self.log("Building model and agent")

        model = OpenAIChatModel(
            self.model,
            provider=OpenAIProvider(
                base_url=self.main_settings.OPENROUTER_URL,
                api_key=self.main_settings.OPENROUTER_API_KEY,
            ),
        )

        self.log(f"Model: {self.model} via OpenRouter")

        agent = Agent(
            model,
            tools=[
                self.tools.grep,
                self.tools.list_files,
                self.tools.read_file,
            ],
            output_type=SearchAnswer,
            instructions=AGENTIC_RAG_PROMPT,
            retries=self.main_settings.RAG_MAX_OUTPUT_RETRIES,
        )

        self.log("Agent built!")
        return agent

    async def answer_question(self, query: str, session_id: str) -> SearchAnswer:
        self.log(f"Agent received query: {query}")

        self.observability.start_trace(
        session_id=session_id,
        query=query,
        system_prompt=AGENTIC_RAG_PROMPT,
        )

        if not hasattr(self, "agent"):
            self.log("Loading agent")
            self.agent = self._build_agent()

        try:
            result = await self.agent.run(
                query,
                usage_limits=UsageLimits(request_limit=self.configs.AGENT_REQUEST_LIMIT),
            )

            usage = result.usage

            input_cost = (usage.input_tokens / 1_000_000) * self.main_settings.GPT_OSS_INPUT_PRICE
            output_cost = (usage.output_tokens / 1_000_000) * self.main_settings.GPT_OSS_OUTPUT_PRICE
            total_cost = round(input_cost + output_cost, 6)

            self.log(
                f"Agent completed | model={self.model} "
                f"requests={usage.requests} input_tokens={usage.input_tokens} "
                f"output_tokens={usage.output_tokens} cost=${total_cost}"
            )

            output: SearchAnswer = result.output

            self.observability.update_trace(
            answer=output.answer,
            citations=output.citations,
            model=self.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            requests=usage.requests,
            cost=total_cost,
            )
            self.observability.score_success()

            return output

        except Exception as e:
            self.log(f"Agent failed: {e}")
            self.observability.score_failure(reason=str(e))
            raise

        finally:
            self.observability.flush()


if __name__ == "__main__":
    assistant = AgenticRag()
    answer = asyncio.run(
        assistant.answer_question(
            query="Hi there, I wanted to know the hourly rates for all your services and offers? regards, Alee",
            session_id=str(uuid4())
        )
    )

    print(answer.answer)
    print(answer.citations)