"""
Universal code analyzer that works with multiple programming languages.
Orchestrates the analysis workflow using watsonx.ai and carbon scoring.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


from .gemini_client import GeminiClient
from .carbon_scorer import CarbonScorer
from .prompts import get_prompt_for_language


class CodeAnalyzer:
    """Universal code analyzer for sustainability assessment."""
    
    # Supported file extensions and their language mappings
    LANGUAGE_MAP = {
        ".py": "python",
        ".java": "java",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "javascript",  # TypeScript treated as JavaScript
        ".tsx": "javascript"
    }
    
    def __init__(self):
        """Initialize the code analyzer."""
        self.gemini_client = GeminiClient()
        self.carbon_scorer = CarbonScorer()
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a source code file for carbon footprint.
        
        Args:
            file_path: Path to the source code file
            
        Returns:
            Dictionary containing analysis results and sustainability score
        """
        # Read file content
        code_content = self._read_file(file_path)
        
        # Detect language
        language = self._detect_language(file_path)
        
        # Analyze code
        return self.analyze_code(code_content, language, file_path)
    
    def analyze_code(
        self,
        code: str,
        language: Optional[str] = None,
        file_name: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Analyze source code content for carbon footprint.
        
        Args:
            code: Source code content as string
            language: Programming language (auto-detected if None)
            file_name: Name of the file (for reporting)
            
        Returns:
            Dictionary containing analysis results and sustainability score
        """
        # Auto-detect language if not provided
        if language is None:
            language = self._detect_language(file_name)
        
        # Get language-specific prompts
        system_prompt, user_prompt = get_prompt_for_language(language, code)
        
        try:
            # Call Gemini 3 Pro for analysis
            raw_response = self.gemini_client.analyze_code(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            # Parse JSON response
            analysis = self.gemini_client.parse_json_response(raw_response)
            
            # Calculate sustainability score
            score_results = self.carbon_scorer.calculate_score(analysis)
            
            # Combine results
            return {
                "file_name": file_name,
                "language": language,
                "analysis": analysis,
                "score": score_results.get("score", 0),
                "grade": score_results.get("grade", "F"),
                "issues": analysis.get("issues", []),
                "total_issues": score_results.get("total_issues", 0),
                "critical_issues": score_results.get("critical_issues", 0),
                "high_issues": score_results.get("high_issues", 0),
                "medium_issues": score_results.get("medium_issues", 0),
                "low_issues": score_results.get("low_issues", 0),
                "issue_breakdown": score_results.get("issue_breakdown", {}),
                "average_severity": score_results.get("average_severity", 0.0),
                "co2_savings_g_day": score_results.get("co2_savings_g_day", 0.0),
                "co2_savings_kg_year": score_results.get("co2_savings_kg_year", 0.0),
                "co2_savings_tons_year": score_results.get("co2_savings_tons_year", 0.0),
                "summary": score_results.get("summary", "Analysis completed."),
                "raw_response": raw_response
            }
            
        except Exception as e:
            return {
                "file_name": file_name,
                "language": language,
                "error": str(e),
                "score": 0,
                "grade": "F",
                "issues": [],
                "total_issues": 0,
                "summary": f"Analysis failed: {str(e)}"
            }
    
    def _read_file(self, file_path: str) -> str:
        """
        Read file content.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _detect_language(self, file_path: str) -> str:
        """
        Detect programming language from file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Language name (python, java, javascript)
        """
        extension = Path(file_path).suffix.lower()
        return self.LANGUAGE_MAP.get(extension, "python")
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported programming languages.
        
        Returns:
            List of supported language names
        """
        return list(set(self.LANGUAGE_MAP.values()))
    
    def is_supported_file(self, file_path: str) -> bool:
        """
        Check if a file is supported for analysis.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is supported, False otherwise
        """
        extension = Path(file_path).suffix.lower()
        return extension in self.LANGUAGE_MAP
    
    def test_connection(self) -> bool:
        """
        Test connection to Gemini 3 Pro.
        
        Returns:
            True if connection successful, False otherwise
        """
        return self.gemini_client.test_connection()

# Made with Bob
