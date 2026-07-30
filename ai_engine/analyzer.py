"""
Google Gemini & OpenRouter Fallback API Client for GreenCode Sentinel.

Handles primary communication with Google Gemini and provides resilient fallback 
to OpenRouter (e.g., Meta Llama 3.3 or DeepSeek) if Gemini fails or rate limits.
"""

import os
import json
import re
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy import try-blocks for optional SDK dependencies
try:
    from google import genai
    from google.genai import types
except ImportError:
    logger.warning("google-genai SDK not installed. Install with: pip install google-genai")
    genai = None  # type: ignore
    types = None  # type: ignore

try:
    import requests
except ImportError:
    logger.warning("requests library not installed. Install with: pip install requests")
    requests = None  # type: ignore


class GeminiClient:
    """
    Production-ready client with multi-provider fallback strategy.
    
    Features:
    - Primary routing to Google Gemini API
    - Fallback routing to OpenRouter when Gemini rate-limits or throws errors
    - Robust JSON extraction and parsing for structured issue output
    """
    
    MAX_RETRIES: int = 5
    INITIAL_RETRY_DELAY: int = 1
    MAX_RETRY_DELAY: int = 32
    
    def __init__(self) -> None:
        """Initialize client settings and environment variables."""
        load_dotenv()
        
        # Load API Keys
        self.api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
        self.open_router_key: Optional[str] = os.getenv("OPEN_ROUTER_KEY")
        
        # Model Configurations
        self.model_id: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.openrouter_model: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")
        
        self.temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
        self.max_tokens: int = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))
        
        # Validate primary credentials
        self._validate_credentials()
        
        # Lazy initialization for Google GenAI client
        self._client: Optional[Any] = None

    def _validate_credentials(self) -> None:
        """Ensure at least one API key is present."""
        if not self.api_key and not self.open_router_key:
            raise ValueError(
                "Neither GOOGLE_API_KEY nor OPEN_ROUTER_KEY is configured in .env!"
            )
        
        if self.api_key and len(self.api_key) < 20:
            logger.warning("GOOGLE_API_KEY appears unusually short. Please check your .env file.")

    def _initialize_client(self) -> None:
        """Initialize the Google GenAI client if available."""
        if self._client is None and self.api_key:
            if genai is None:
                logger.warning("google-genai SDK not installed. Will rely on OpenRouter fallback.")
                return
            
            try:
                self._client = genai.Client(api_key=self.api_key)
                logger.info(f"Gemini client initialized with model: {self.model_id}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")

    def analyze_code(self, system_prompt: str, user_prompt: str) -> str:
        """
        Main execution point. Attempts analysis via Gemini first. 
        Falls back to OpenRouter if Gemini encounters an error.
        """
        # 1. Attempt Primary Execution via Gemini
        if self.api_key:
            try:
                self._initialize_client()
                if self._client is not None:
                    logger.info("Attempting code analysis via Primary Provider (Gemini)...")
                    response = self._client.models.generate_content(
                        model=self.model_id,
                        contents=user_prompt,
                        config={
                            "system_instruction": system_prompt,
                            "max_output_tokens": self.max_tokens,
                            "response_mime_type": "application/json",
                        }
                    )
                    if hasattr(response, 'text') and response.text:
                        return str(response.text)
            except Exception as e:
                logger.warning(f"⚠️ Primary Provider (Gemini) failed: {e}. Switching to OpenRouter Fallback...")

        # 2. Attempt Fallback Execution via OpenRouter
        if self.open_router_key:
            return self._call_openrouter(system_prompt, user_prompt)
        
        raise RuntimeError("Both Primary (Gemini) and Fallback (OpenRouter) executions failed or are unconfigured.")

    def _call_openrouter(self, system_prompt: str, user_prompt: str) -> str:
        """Helper method to invoke OpenRouter API via HTTP REST."""
        if requests is None:
            raise ImportError("The 'requests' library is required for OpenRouter fallback. Install via: pip install requests")

        logger.info(f"Attempting code analysis via Fallback Provider (OpenRouter: {self.openrouter_model})...")

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.open_router_key}",
            "HTTP-Referer": "https://github.com/GreenCode-Sentinel",
            "X-Title": "GreenCode Sentinel",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.openrouter_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            logger.info("✅ Successfully retrieved response from OpenRouter fallback.")
            return str(content)

        except Exception as e:
            logger.error(f"❌ OpenRouter fallback also failed: {str(e)}")
            raise RuntimeError(f"OpenRouter API call failed: {str(e)}") from e

    def parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Robustly extract and parse JSON from AI responses.
        Guarantees returning a Dict[str, Any] on all execution paths.
        """
        if not response_text or not response_text.strip():
            return {"issues": [], "error": "Empty response received"}

        try:
            # Strategy 1: Find JSON inside markdown code blocks ```json ...
            markdown_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            match = re.search(markdown_pattern, response_text, re.DOTALL)
            
            if match:
                clean_json = match.group(1)
            else:
                # Strategy 2: Extract string between first '{' and last '}'
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    clean_json = response_text[start_idx:end_idx + 1]
                else:
                    clean_json = response_text

            parsed: Any = json.loads(clean_json)
            
            if isinstance(parsed, dict):
                dict_parsed: Dict[str, Any] = parsed
                if "issues" not in dict_parsed:
                    dict_parsed["issues"] = []
                return dict_parsed
            else:
                return {"issues": [], "error": "Parsed JSON is not a dictionary"}

        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding failed: {e}")
            return {"issues": [], "error": f"JSON parsing failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON: {e}")
            return {"issues": [], "error": str(e)}

    def test_connection(self) -> bool:
        """
        Test API connection for both primary (Gemini) and fallback (OpenRouter).
        
        Returns:
            True if at least one API provider connects successfully, False otherwise.
        """
        logger.info("Testing API connections...")
        gemini_ok = False
        openrouter_ok = False

        # 1. Test Gemini Connection Block
        if self.api_key:
            try:
                self._initialize_client()
                if self._client:
                    res = self._client.models.generate_content(
                        model=self.model_id,
                        contents="Respond with 'OK'"
                    )
                    if hasattr(res, 'text') and res.text:
                        logger.info("✅ Gemini API Connection: Success")
                        gemini_ok = True
                    else:
                        logger.warning("❌ Gemini API Connection: Received empty response")
            except Exception as e:
                logger.warning(f"❌ Gemini Connection Test Failed: {e}")

        # 2. Test OpenRouter Connection Block
        if self.open_router_key and requests is not None:
            try:
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.open_router_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.openrouter_model,
                    "messages": [{"role": "user", "content": "Respond with 'OK'"}],
                    "max_tokens": 10
                }
                res = requests.post(url, headers=headers, json=payload, timeout=15)
                if res.status_code == 200:
                    logger.info("✅ OpenRouter API Connection: Success")
                    openrouter_ok = True
                else:
                    logger.warning(f"❌ OpenRouter Connection Failed with Status {res.status_code}: {res.text[:200]}")
            except Exception as e:
                logger.warning(f"❌ OpenRouter Connection Test Failed: {e}")

        return gemini_ok or openrouter_ok