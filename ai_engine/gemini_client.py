"""
Google Gemini 3 Pro Client for code analysis.
Handles authentication and API communication with high thinking level.
"""

import os
import json
from typing import Optional, Dict, Any, cast
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
    from google.genai.types import GenerateContentConfig
except ImportError:
    print("Warning: google-genai not installed. Install with: pip install google-genai")
    genai = None  # type: ignore
    types = None  # type: ignore
    GenerateContentConfig = None  # type: ignore


class GeminiClient:
    """Client for interacting with Google Gemini 3 Pro API."""
    
    def __init__(self):
        """Initialize the Gemini client with credentials from environment."""
        load_dotenv()
        
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_id = os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview")
        self.thinking_level = os.getenv("GEMINI_THINKING_LEVEL", "high")
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
        self.max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "4096"))
        
        self._validate_credentials()
        self._client: Optional[Any] = None
    
    def _validate_credentials(self):
        """Validate that all required credentials are present."""
        if not self.api_key or self.api_key == "your_google_api_key_here":
            raise ValueError(
                "GOOGLE_API_KEY not set. Please copy .env.template to .env and add your credentials.\n"
                "Get your API key from: https://aistudio.google.com/app/apikey"
            )
    
    def _initialize_client(self):
        """Initialize the Gemini API client."""
        if self._client is None:
            if genai is None:
                raise ImportError(
                    "google-genai package not installed. "
                    "Install with: pip install google-genai"
                )
            
            # Initialize the Gemini client
            self._client = genai.Client(api_key=self.api_key)
    
    def analyze_code(
        self,
        system_prompt: str,
        user_prompt: str,
        thinking_level: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send code to Gemini 3 Pro for analysis with high thinking level.
        
        Args:
            system_prompt: System-level instructions for the AI
            user_prompt: User prompt containing the code to analyze
            thinking_level: Thinking level (low, medium, high) - defaults to 'high'
            temperature: Sampling temperature (lower = more deterministic)
            max_tokens: Maximum tokens in response
            
        Returns:
            AI analysis response as string
        """
        self._initialize_client()
        
        # Use provided values or defaults
        thinking_level = thinking_level or self.thinking_level
        temperature = temperature if temperature is not None else self.temperature
        max_tokens = max_tokens or self.max_tokens
        
        # Combine system and user prompts
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            # Generate response using Gemini with configuration
            if self._client is None:
                raise RuntimeError("Client not initialized")
            
            config_dict: Dict[str, Any] = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "response_mime_type": "application/json",
            }
            
            # Add thinking level if supported by the model
            if thinking_level and thinking_level != "low":
                config_dict["thinking_config"] = {"mode": thinking_level}
            
            response = self._client.models.generate_content(
                model=self.model_id,
                contents=full_prompt,
                config=config_dict
            )
            
            # Extract generated text
            if hasattr(response, 'text') and response.text:
                return response.text
            elif hasattr(response, 'candidates') and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts') and candidate.content.parts:
                    return candidate.content.parts[0].text
            
            return str(response)
                
        except Exception as e:
            raise RuntimeError(f"Error calling Gemini API: {str(e)}")
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from Gemini, handling potential formatting issues.
        
        Args:
            response: Raw response string from Gemini
            
        Returns:
            Parsed JSON as dictionary
        """
        try:
            # Try to parse the entire response as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            try:
                start_idx = response.find("{")
                end_idx = response.rfind("}") + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    # If no JSON found, return a default structure
                    return {
                        "issues": [],
                        "summary": response
                    }
            except json.JSONDecodeError as e:
                print(f"Warning: Could not parse JSON response: {e}")
                return {
                    "issues": [],
                    "summary": response
                }
    
    def test_connection(self) -> bool:
        """
        Test the connection to Gemini 3 Pro.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._initialize_client()
            
            if self._client is None:
                print("❌ Gemini 3 Pro connection failed: Client not initialized")
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
                print("✅ Gemini 3 Pro connection successful!")
                return True
            else:
                print("❌ Gemini 3 Pro connection failed: No response received")
                return False
                
        except Exception as e:
            print(f"❌ Gemini 3 Pro connection test failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current Gemini model configuration.
        
        Returns:
            Dictionary with model configuration details
        """
        return {
            "model_id": self.model_id,
            "thinking_level": self.thinking_level,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "api_configured": bool(self.api_key and self.api_key != "your_google_api_key_here")
        }

# Made with Bob
