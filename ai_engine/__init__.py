"""
GreenCode Sentinel - AI Engine Module
Handles Google Gemini integration, code analysis, and carbon scoring.
"""

import logging
from pathlib import Path
from typing import Dict, Any

from .analyzer import GeminiClient
from .carbon_scorer import CarbonScorer
from .prompts import get_prompt_for_language

logger = logging.getLogger(__name__)

# Extension → language name map
_EXTENSION_MAP: Dict[str, str] = {
    ".py":  "python",
    ".js":  "javascript",
    ".jsx": "javascript",
    ".ts":  "javascript",
    ".tsx": "javascript",
    ".java": "java",
    ".cpp": "cpp",
    ".cc":  "cpp",
    ".cxx": "cpp",
    ".go":  "go",
    ".rs":  "rust",
}


class CodeAnalyzer:
    """
    High-level facade that ties together the AI client, prompt builder,
    and carbon scorer into a single analyze_file() call.
    """

    def __init__(self) -> None:
        self._client = GeminiClient()
        self._scorer = CarbonScorer()

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a source file, call the AI for sustainability issues, score and
        return the combined result dict.

        Args:
            file_path: Absolute or relative path to the source file.

        Returns:
            Dict with keys: issues, score, grade, category_scores,
            total_issues, co2_savings_kg_year, co2_savings_tons_year, summary.
            On failure the dict contains an "error" key.
        """
        path = Path(file_path)
        language = _EXTENSION_MAP.get(path.suffix.lower(), "python")

        try:
            code = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return {"issues": [], "error": f"Cannot read file: {exc}"}

        system_prompt, user_prompt = get_prompt_for_language(language, code)

        try:
            raw_response = self._client.analyze_code(system_prompt, user_prompt)
        except Exception as exc:
            logger.error(f"AI call failed: {exc}")
            return {"issues": [], "error": str(exc)}

        analysis = self._client.parse_json_response(raw_response)

        if "error" in analysis:
            return analysis

        scored = self._scorer.calculate_score(analysis)
        # Merge issues list into scored result
        scored["issues"] = analysis.get("issues", [])
        return scored


__all__ = ["CodeAnalyzer", "GeminiClient", "CarbonScorer"]

# Made with Bob
