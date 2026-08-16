"""OpenRouter LLM client for the Cisco Network Troubleshooting AI."""

import json
import logging
import time
from typing import Optional, List
from openai import OpenAI
from src.config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL, LLM_TIMEOUT, LLM_TEMPERATURE, LLM_MAX_TOKENS

logger = logging.getLogger(__name__)

# Free models to try in order (as of 2024)
FREE_MODELS = [
    "openrouter/auto",
    "google/gemma-2-9b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
]


class LLMClient:
    """Client for interacting with OpenRouter API with fallback models."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.primary_model = model or OPENROUTER_MODEL
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set. Please configure .env file.")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=OPENROUTER_BASE_URL,
            timeout=LLM_TIMEOUT
        )
    
    def diagnose(self, system_prompt: str, user_prompt: str) -> dict:
        """Send a diagnosis request to the LLM and return parsed JSON."""
        models_to_try = [self.primary_model] + [m for m in FREE_MODELS if m != self.primary_model]
        
        for model in models_to_try:
            logger.info(f"Trying model: {model}")
            result = self._try_model(model, system_prompt, user_prompt)
            if result:
                return result
            logger.warning(f"Model {model} failed, trying next...")
            time.sleep(1)
        
        logger.error("All models failed, returning default response")
        return self._default_response()
    
    def _try_model(self, model: str, system_prompt: str, user_prompt: str) -> Optional[dict]:
        """Try a single model, return parsed result or None on failure."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                logger.warning(f"Model {model} returned empty content")
                return None
            
            logger.info(f"Model {model} responded successfully")
            return self._parse_json(content)
            
        except Exception as e:
            logger.warning(f"Model {model} error: {e}")
            return None
    
    def _parse_json(self, content: str) -> dict:
        """Robustly parse JSON from LLM response, handling extra text."""
        import re
        
        # Try direct parse first
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                if parsed and isinstance(parsed[0], dict):
                    return parsed[0]
                else:
                    return self._default_response()
            return parsed
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON object from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                if isinstance(parsed, list):
                    if parsed and isinstance(parsed[0], dict):
                        return parsed[0]
                    else:
                        return self._default_response()
                return parsed
            except json.JSONDecodeError:
                pass
        
        # Try to fix common issues
        fixed = content.strip()
        fixed = re.sub(r'^```json\s*', '', fixed)
        fixed = re.sub(r'^```\s*', '', fixed)
        fixed = re.sub(r'\s*```$', '', fixed)
        fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        
        try:
            parsed = json.loads(fixed)
            if isinstance(parsed, list):
                if parsed and isinstance(parsed[0], dict):
                    return parsed[0]
                else:
                    return self._default_response()
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Content was: {content[:500]}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")
    
    def _default_response(self) -> dict:
        """Return a default valid response structure."""
        return {
            "predicted_fault": "Unknown",
            "confidence": 0.0,
            "reasoning_summary": "Failed to parse LLM response",
            "evidence_used": [],
            "recommended_fix": "Manual review required",
            "commands": [],
            "needs_more_evidence": True
        }


def create_llm_client() -> LLMClient:
    """Factory function to create an LLM client."""
    return LLMClient()