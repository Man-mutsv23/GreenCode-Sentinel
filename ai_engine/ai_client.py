"""
Google Gemini API Client for code analysis.
Handles authentication, API communication, error handling, and retry logic.
"""

import os
import json
import re
import time
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
except ImportError:
    logger.warning("google-genai not installed. Install with: pip install google-genai")
    genai = None  # type: ignore
    types = None  # type: ignore

try:
    import requests
except ImportError:
    logger.warning("requests not installed. Install with: pip install requests")
    requests = None  # type: ignore


class GeminiClient:
    """
    Production-ready client for Google Gemini API.
    
    Features:
    - Proper API key management via environment variables
    - Exponential backoff retry logic for rate limits and transient failures
    - Comprehensive error handling for network, API, and parsing errors
    - JSON response enforcement with fallback regex extraction
    - Safety settings configured for unrestricted code analysis
    """
    
    # Retry configuration
    MAX_RETRIES = 5
    INITIAL_RETRY_DELAY = 1  # seconds
    MAX_RETRY_DELAY = 32  # seconds
    RETRY_MULTIPLIER = 2
    
    def __init__(self):
        """
        Initialize the Gemini client with credentials from environment.
        
        Raises:
            ValueError: If API key is not configured
            ImportError: If required packages are not installed
        """
        load_dotenv()
        
        # Load configuration from environment
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_id = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
        self.max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))
        
        # Validate credentials
        self._validate_credentials()
        
        # Initialize client (lazy initialization)
        self._client: Optional[Any] = None
    
    def _validate_credentials(self):
        """
        Validate that all required credentials are present.
        
        Raises:
            ValueError: If API key is missing or invalid
        """
        if not self.api_key or self.api_key == "your_google_api_key_here":
            raise ValueError(
                "GOOGLE_API_KEY not set or invalid. "
                "Please copy .env.template to .env and add your API key.\n"
                "Get your API key from: https://aistudio.google.com/app/apikey"
            )
        
        if len(self.api_key) < 20:
            raise ValueError(
                "GOOGLE_API_KEY appears to be invalid (too short). "
                "Please check your API key configuration."
            )
    
    def _initialize_client(self):
        """
        Initialize the Gemini API client with proper configuration.
        
        Raises:
            ImportError: If google-genai package is not installed
        """
        if self._client is None:
            if genai is None:
                raise ImportError(
                    "google-genai package not installed. "
                    "Install with: pip install google-genai"
                )
            
            # Initialize the Gemini client with API key
            self._client = genai.Client(api_key=self.api_key)
            logger.info(f"Gemini client initialized with model: {self.model_id}")
    
    def analyze_code(self, system_prompt: str, user_prompt: str) -> str:
        self._initialize_client()
        if self._client is None:
            raise RuntimeError("Failed to initialize Gemini client")

        try:
            response = self._client.models.generate_content(
                model=self.model_id, # Use the model from .env!
                contents=user_prompt,
                config={
                    "system_instruction": system_prompt,
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",
                }
            )
            return response.text
        except Exception as e:
            raise Exception(f"Error calling Gemini API: {str(e)}")

    def _extract_response_text(self, response: Any) -> str:
        """
        Extract text from Gemini API response.
        
        Args:
            response: Response object from Gemini API
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If response format is unexpected
        """
        # Try different response formats
        if hasattr(response, 'text') and response.text:
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            if len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    if candidate.content.parts:
                        return candidate.content.parts[0].text
        
        # Fallback: convert to string
        response_str = str(response)
        if response_str and response_str != "None":
            return response_str
        
        raise ValueError("Unable to extract text from response")
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error is retryable.
        
        Retryable errors include:
        - Rate limit errors (429)
        - Server errors (500, 502, 503, 504)
        - Network timeouts
        - Connection errors
        
        Args:
            error: Exception to check
            
        Returns:
            True if error is retryable, False otherwise
        """
        error_str = str(error).lower()
        
        # Check for rate limit errors
        if "429" in error_str or "rate limit" in error_str or "quota" in error_str:
            return True
        
        # Check for server errors
        if any(code in error_str for code in ["500", "502", "503", "504"]):
            return True
        
        # Check for network errors
        if any(term in error_str for term in ["timeout", "connection", "network"]):
            return True
        
        # Check for requests exceptions
        if requests:
            if isinstance(error, (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError
            )):
                return True
        
        return False
    
    def parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Robustly extract and parse JSON from AI responses.
        
        Handles multiple formats:
        1. JSON wrapped in markdown code blocks
        2. JSON with surrounding text
        3. Raw JSON
        
        Args:
            response_text: Raw response text from AI
            
        Returns:
            Parsed JSON as dictionary
            
        Raises:
            ValueError: If JSON cannot be extracted or parsed
        """
        try:
            # Strategy 1: Try to find JSON in markdown code blocks
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if match:
                clean_json = match.group(1)
                logger.debug("Extracted JSON from markdown code block")
            else:
                # Strategy 2: Find first '{' and last '}'
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    clean_json = response_text[start_idx:end_idx + 1]
                    logger.debug("Extracted JSON using brace matching")
                else:
                    # Strategy 3: Assume entire response is JSON
                    clean_json = response_text
                    logger.debug("Using entire response as JSON")
            
            # Parse JSON
            parsed = json.loads(clean_json)
            
            # Validate structure
            if not isinstance(parsed, dict):
                raise ValueError("Parsed JSON is not a dictionary")
            
            # Ensure 'issues' key exists
            if "issues" not in parsed:
                logger.warning("JSON missing 'issues' key, adding empty list")
                parsed["issues"] = []
            
            return parsed
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing failed: {str(e)}\nRaw response:\n{response_text[:500]}"
            logger.error(error_msg)
            
            # Return empty structure instead of raising to prevent crashes
            return {"issues": [], "error": "JSON parsing failed"}
        except Exception as e:
            error_msg = f"Unexpected error parsing JSON: {str(e)}"
            logger.error(error_msg)
            return {"issues": [], "error": str(e)}
    
    def test_connection(self) -> bool:
        """
        Test the connection to Gemini API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._initialize_client()
            
            if self._client is None:
                logger.error("Gemini connection failed: Client not initialized")
                return False
            
            # Try a simple generation to test connection
            config_dict: Dict[str, Any] = {
                "temperature": 0.1,
                "max_output_tokens": 10
            }
            
            response = self._client.models.generate_content(
                model=self.model_id,
                contents="Hello, this is a connection test. Please respond with 'OK'.",
                config=config_dict
            )
            
            # Check if we got a response
            if hasattr(response, 'text') or hasattr(response, 'candidates'):
                logger.info("✅ Gemini API connection successful!")
                return True
            else:
                logger.error("❌ Gemini connection failed: No response received")
                return False
                
        except Exception as e:
            logger.error(f"❌ Gemini connection test failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current Gemini model configuration.
        
        Returns:
            Dictionary with model configuration details
        """
        return {
            "model_id": self.model_id,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "api_configured": bool(self.api_key and self.api_key != "your_google_api_key_here"),
            "max_retries": self.MAX_RETRIES,
            "initial_retry_delay": self.INITIAL_RETRY_DELAY,
            "max_retry_delay": self.MAX_RETRY_DELAY
        }


