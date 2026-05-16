from pydantic import BaseModel, Field

class Citation(BaseModel):
    """One source backing a claim in the answer."""

    file: str = Field(
        description="Relative path to the markdown file, e.g. '01_about_me.md'"
    )
    quote: str = Field(description="Exact line(s) from the file that support the claim")


class SearchAnswer(BaseModel):
    """Structured answer with citations that downstream code can trust."""

    answer: str = Field(description="The answer in plain English")
    citations: list[Citation] = Field(
        description="Files and quotes that support the answer"
    )