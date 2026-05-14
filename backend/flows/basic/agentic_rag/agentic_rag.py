import logging
import asyncio
from pathlib import Path

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
        self.tools = AgenticRagTools(
            notes_dir=NOTES_DIR,
            grep_timeout_seconds=self.configs.GREP_TIMEOUT_SECONDS,
            read_max_lines=self.configs.READ_MAX_LINES,
            log_callback=self.log,      # reuse the logger method
        )
        self.log("AgenticRAG initialized")

    def _build_agent(self) -> Agent:
        self.log("Building model and agent")

        model = OpenAIChatModel(
            self.main_settings.GPT_OSS_MODEL,
            provider=OpenAIProvider(
                base_url=self.main_settings.OPENROUTER_URL,
                api_key=self.main_settings.OPENROUTER_API_KEY,
            ),
        )

        agent = Agent(
            model,
            tools=[
                self.tools.grep,
                self.tools.list_files,
                self.tools.read_file,
            ],
            output_type=SearchAnswer,
            instructions=AGENTIC_RAG_PROMPT,
        )

        self.log("Agent built!")
        return agent

    async def answer_question(self, query: str) -> SearchAnswer:
        self.log(f"Agent received query: {query}")

        if not hasattr(self, "agent"):
            self.log("loading agent")
            self.agent = self._build_agent()

        result = await self.agent.run(
            query,
            usage_limits=UsageLimits(request_limit=self.configs.AGENT_REQUEST_LIMIT),
        )

        usage = result.usage()

        self.log(
            f"Agent completed | requests={usage.requests} "
            f"input_tokens={usage.input_tokens} output_tokens={usage.output_tokens}"
        )

        return result.output


if __name__ == "__main__":
    assistant = AgenticRag()
    answer = asyncio.run(
        assistant.answer_question("what are your specialities in LLMs?")
    )

    print(answer.answer)
    print(answer.citations)