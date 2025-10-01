from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict

from ..schemas import ReviewRequest, ReviewResponse, InlineComment
from .gemini import build_gemini_from_env


@dataclass
class ReviewServiceConfig:
    model: str
    api_key: str
    temperature: float = 0.2
    max_output_tokens: int = 2048


class ReviewService:
    def __init__(self, cfg: ReviewServiceConfig):
        self.cfg = cfg
        self.gemini = build_gemini_from_env(
            api_key=cfg.api_key,
            model=cfg.model,
            temperature=cfg.temperature,
            max_output_tokens=cfg.max_output_tokens,
        )

    @classmethod
    def from_env(cls, cfg: ReviewServiceConfig) -> "ReviewService":
        return cls(cfg)

    async def generate_review(self, req: ReviewRequest) -> ReviewResponse:
        system_prompt = (
            "You are a senior software engineer performing code reviews. "
            "Provide concise, actionable feedback, prioritizing correctness, security, readability, and performance. "
            "Prefer inline comments that reference specific lines and files. "
            "Use the schema: {summary: string, comments: [{path, line?, comment, severity?}], suggestions: [string]}"
        )

        user_prompt = self._build_user_prompt(req)
        data = self.gemini.generate_json(system_prompt=system_prompt, user_prompt=user_prompt)

        # Normalize model output
        summary = str(data.get("summary", ""))
        comments_raw = data.get("comments", []) or []
        suggestions_raw = data.get("suggestions", []) or []

        comments = []
        for c in comments_raw:
            try:
                comments.append(
                    InlineComment(
                        path=str(c.get("path", "")),
                        line=(int(c["line"]) if c.get("line") is not None else None),
                        comment=str(c.get("comment", "")),
                        severity=(str(c["severity"]) if c.get("severity") else None),
                    )
                )
            except Exception:
                # Skip malformed entries
                continue

        suggestions = [str(s) for s in suggestions_raw if str(s).strip()]

        return ReviewResponse(
            summary=summary or "No summary provided.",
            comments=comments,
            suggestions=suggestions,
            model=self.cfg.model,
            tokens_used=None,
        )

    def _build_user_prompt(self, req: ReviewRequest) -> str:
        header = (
            f"Repository: {req.repo}\n"
            f"PR: #{req.pr_number}\n"
            f"Title: {req.title}\n"
            f"Author: {req.author or 'unknown'}\n"
            f"Base: {req.base_sha or '-'}\n"
            f"Head: {req.head_sha or '-'}\n\n"
            f"Description:\n{req.description or '(no description)'}\n\n"
            "Changed Files (diffs below):\n"
        )

        diffs = []
        for f in req.changed_files:
            patch = f.patch or ""
            diffs.append(
                "\n".join(
                    [
                        f"---\nFile: {f.path} ({f.status})",
                        "```diff",
                        patch.strip() if patch else "(no patch provided)",
                        "```",
                    ]
                )
            )

        prompt = header + "\n\n".join(diffs)

        # Guide the model to return the desired JSON structure
        schema_hint = (
            "\n\nReturn ONLY JSON with keys: summary, comments, suggestions. "
            "Example: {\"summary\": \"...\", \"comments\": [{\"path\": \"a.py\", \"line\": 12, \"comment\": \"...\", \"severity\": \"suggestion\"}], \"suggestions\": [\"...\"]}"
        )
        return prompt + schema_hint

