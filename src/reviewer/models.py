from typing import Literal
from pydantic import BaseModel, Field


class Finding(BaseModel):
    file: str
    line: int = Field(description="Line number in the NEW version of the file")
    severity: Literal["low", "medium", "high"]
    category: Literal["security", "bug", "maintainability"]
    message: str
    suggestion: str | None = None


class ReviewResult(BaseModel):
    findings: list[Finding] = Field(
        default_factory=list,
        description="Problems found in the diff. Empty list if there are none.",
    )


class TriageResult(BaseModel):
    reviewers_to_run: list[Literal["security", "bug", "maintainability"]] = Field(
        description="Which specialist reviewers are worth running on this diff. "
        "Include a reviewer only if its focus area is plausibly relevant.",
    )