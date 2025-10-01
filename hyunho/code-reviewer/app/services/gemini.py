from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class GeminiConfig:
    api_key: str
    model: str = "gemini-1.5-flash"
    temperature: float = 0.2
    max_output_tokens: int = 2048


class GeminiClient:
    def __init__(self, cfg: GeminiConfig):
        self.cfg = cfg
        self._client = None

        # Lazy import to avoid hard failure if package isn't installed yet.
        if self.cfg.api_key:
            try:
                import google.generativeai as genai  # type: ignore

                genai.configure(api_key=self.cfg.api_key)
                self._client = genai.GenerativeModel(self.cfg.model)
            except Exception:
                # Keep _client None; we'll mock responses.
                self._client = None

    def is_mock(self) -> bool:
        return self._client is None

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generate a JSON object response. If SDK unavailable, return mock."""
        if self._client is None:
            # Provide a deterministic mock helpful for local testing
            return {
                "summary": "Automated review mock: looks generally good. Consider minor cleanups.",
                "comments": [
                    {
                        "path": "example.py",
                        "line": 10,
                        "comment": "Prefer using context manager for file operations.",
                        "severity": "suggestion",
                    }
                ],
                "suggestions": [
                    "Add tests for edge cases in input parsing.",
                    "Consider typing annotations for public functions.",
                ],
            }

        import google.generativeai as genai  # type: ignore

        prompt = (
            f"<SYSTEM>\n{system_prompt}\n</SYSTEM>\n\n<USER>\n{user_prompt}\n</USER>"
        )
        try:
            response = self._client.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=self.cfg.temperature,
                    max_output_tokens=self.cfg.max_output_tokens,
                    response_mime_type="application/json",
                ),
            )
            text = response.text or "{}"
            return json.loads(text)
        except Exception as e:
            # Last-resort fallback
            return {
                "summary": f"Model call failed: {e}",
                "comments": [],
                "suggestions": [],
            }


def build_gemini_from_env(api_key: Optional[str] = None, **overrides: Any) -> GeminiClient:
    key = api_key or os.getenv("GEMINI_API_KEY", "")
    cfg = GeminiConfig(
        api_key=key,
        model=overrides.get("model", os.getenv("GEMINI_MODEL", "gemini-1.5-flash")),
        temperature=float(overrides.get("temperature", os.getenv("GEMINI_TEMPERATURE", 0.2))),
        max_output_tokens=int(
            overrides.get(
                "max_output_tokens",
                os.getenv("GEMINI_MAX_OUTPUT_TOKENS", 2048),
            )
        ),
    )
    return GeminiClient(cfg)

