from typing import List, Optional
from pydantic import BaseModel, Field


class ChangedFile(BaseModel):
    path: str = Field(..., description="File path relative to repo root")
    status: str = Field(..., description="added|modified|removed|renamed")
    patch: Optional[str] = Field(
        None, description="Unified diff hunk(s) for this file, if available"
    )


class ReviewRequest(BaseModel):
    repo: str = Field(..., description="owner/repo")
    pr_number: int
    title: str
    description: str = ""
    base_sha: Optional[str] = None
    head_sha: Optional[str] = None
    author: Optional[str] = None
    changed_files: List[ChangedFile] = Field(default_factory=list)


class InlineComment(BaseModel):
    path: str
    line: Optional[int] = None
    comment: str
    severity: Optional[str] = Field(
        default=None, description="nit|suggestion|warning|error"
    )


class ReviewResponse(BaseModel):
    summary: str
    comments: List[InlineComment] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    model: Optional[str] = None
    tokens_used: Optional[int] = None

