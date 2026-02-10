"""
LLM Service for Swali-AI - Google Gemini Edition

LEARNING NOTE: LLM Integration with Google Gemini
==================================================
This module wraps the Google Gemini API for generating answers.

Why Gemini?
-----------
- Free tier available (great for learning!)
- Fast response times
- Good at code and technical content
- Simple API

How LLM APIs Work:
------------------
1. You send a "prompt" (your question/instructions)
2. The model processes it
3. You get back a "response" (the generated text)

The RAG flow:
    User Question → Retrieve Context → Format Prompt → Gemini → Answer
                                          ↑
                                    (This module)

Key Concepts:
-------------
- API Key: Your secret credential to access the API
- Model: Which Gemini version to use (gemini-1.5-flash, gemini-pro, etc.)
- Temperature: Controls randomness (0 = deterministic, 1 = creative)
- Max Tokens: Maximum length of the response

Package: google-generativeai
----------------------------
This is Google's Python SDK for Gemini. It provides:
- Simple client creation with genai.configure()
- Model instantiation with GenerativeModel()
- Content generation with generate_content()
"""

from typing import Optional
from dataclasses import dataclass

import google.generativeai as genai

from app.config import settings


@dataclass
class LLMResponse:
    """
    Structured response from the LLM.
    
    LEARNING NOTE: Why a dataclass?
    -------------------------------
    Instead of returning raw text, we structure the response.
    This makes it easier to:
    - Track token usage (for cost monitoring)
    - Handle errors consistently
    - Add metadata like model version
    
    Fields:
        content: The actual generated text
        model: Which model was used
        tokens_used: How many tokens consumed (for billing)
        finish_reason: Why generation stopped (length, complete, etc.)
    """
    content: str
    model: str
    tokens_used: int
    finish_reason: str


class LLMService:
    """
    Service for calling Google Gemini API.
    
    LEARNING NOTE: Service Pattern
    ==============================
    We wrap the API client in a service class to:
    - Centralize configuration (API key, model, etc.)
    - Add retry logic for reliability
    - Handle errors consistently
    - Make testing easier (can mock the service)
    
    Usage:
        service = LLMService()
        response = service.generate("How do I solve Two Sum?")
        print(response.content)
    """
    
    def __init__(self, model: str | None = None):
        """
        Initialize the Gemini LLM service.
        
        LEARNING NOTE: Configuration Steps
        ----------------------------------
        1. Configure API with your key
        2. Create a GenerativeModel instance
        3. Use model.generate_content() to get responses
        
        Args:
            model: Gemini model to use. Options:
                   - "gemini-1.5-flash" (fast, great for most uses)
                   - "gemini-pro" (original model, very capable)
        """
        # Configure the API with our key
        genai.configure(api_key=settings.gemini_api_key)
        
        # Choose the model
        self.model_name = model or settings.llm_model
        
        # Create the model instance
        self.model = genai.GenerativeModel(model_name=self.model_name)
        
        print(f"LLM Service initialized with model: {self.model_name}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> LLMResponse:
        """
        Generate a response from Gemini.
        
        LEARNING NOTE: How Generation Works
        -----------------------------------
        1. We combine system instructions + user prompt
        2. Send to Gemini API via generate_content()
        3. Get back generated text + metadata
        4. Return structured response
        
        System Prompt vs User Prompt:
        - System: Sets the AI's personality/role ("You are a coding tutor")
        - User: The actual question ("How do I solve Two Sum?")
        
        Args:
            prompt: The user's question/request
            system_prompt: Optional system instructions (prepended to prompt)
            max_tokens: Maximum response length (prevent runaway generation)
            temperature: Creativity level
                        0.0 = Very focused, deterministic
                        0.7 = Balanced (default)
                        1.0 = Very creative, varied
            
        Returns:
            LLMResponse with content and metadata
        """
        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            # Default system prompt for coding coach
            full_prompt = f"You are a helpful coding interview coach. Be concise and educational.\n\n{prompt}"
        
        # Configure generation parameters
        generation_config = genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        
        # Generate the response
        response = self.model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        # Extract token usage if available
        tokens_used = 0
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            tokens_used = (
                getattr(response.usage_metadata, 'prompt_token_count', 0) +
                getattr(response.usage_metadata, 'candidates_token_count', 0)
            )
        
        # Get finish reason
        finish_reason = "COMPLETE"
        if response.candidates:
            fr = response.candidates[0].finish_reason
            if hasattr(fr, 'name'):
                finish_reason = fr.name
            elif fr:
                finish_reason = str(fr)
        
        # Return structured response
        return LLMResponse(
            content=response.text,
            model=self.model_name,
            tokens_used=tokens_used,
            finish_reason=finish_reason
        )
    
    def generate_with_retry(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> LLMResponse:
        """
        Generate with automatic retry on failure.
        
        LEARNING NOTE: Retry with Exponential Backoff
        --------------------------------------------
        API calls can fail due to:
        - Rate limits (too many requests per minute)
        - Temporary server issues
        - Network problems
        
        We retry with increasing delays: 1s, 2s, 4s...
        This is "exponential backoff" - a common reliability pattern.
        
        Why not just retry immediately?
        If the server is overloaded, hammering it with
        requests makes things worse. Waiting gives it time to recover.
        """
        import time
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return self.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1, 2, 4 seconds
                    print(f"API error: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        
        raise Exception(f"Failed after {max_retries} attempts: {last_error}")


# Global service instance (lazy initialized)
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """
    Get or create the global LLM service instance.
    
    LEARNING NOTE: Lazy Initialization (Singleton Pattern)
    ------------------------------------------------------
    We don't create the service at import time because:
    - The API key might not be loaded yet
    - It's wasteful if the service is never used
    - Delays startup and can cause import errors
    
    Instead, we create it on first use. This is called
    "lazy initialization" - a common optimization pattern.
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


# =============================================================================
# Quick test - run with: poetry run python -m app.rag.llm
# =============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Gemini LLM Service")
    print("="*60 + "\n")
    
    service = LLMService()
    
    print("Sending test prompt...")
    response = service.generate(
        prompt="Explain the Two Sum problem in 2 sentences.",
        max_tokens=100
    )
    
    print(f"\nResponse: {response.content}")
    print(f"\nTokens used: {response.tokens_used}")
    print(f"Finish reason: {response.finish_reason}")
