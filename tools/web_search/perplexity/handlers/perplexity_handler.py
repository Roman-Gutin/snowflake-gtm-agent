"""
Perplexity API Handler for Snowflake UDFs

This module provides web search capabilities using the Perplexity API.
Designed to work as Snowflake UDFs with secret-based authentication.

Supported Operations:
- Web search with citations
- Configurable model selection (sonar-pro, sonar)
- Related questions retrieval
"""

import json
import requests


class PerplexityHandler:
    """
    Handler class for Perplexity API operations in Snowflake UDFs.
    
    Uses Snowflake secrets for API key authentication.
    Returns structured JSON responses with success/error handling.
    """
    
    API_URL = "https://api.perplexity.ai/chat/completions"
    TIMEOUT = 60  # seconds
    DEFAULT_MODEL = "sonar-pro"
    DEFAULT_MAX_TOKENS = 4000
    
    def __init__(self, snowflake_module=None):
        """
        Initialize the handler.
        
        Args:
            snowflake_module: The _snowflake module (injected in Snowflake UDF context)
        """
        self._snowflake = snowflake_module
    
    def _get_api_key(self):
        """Get API key from Snowflake secret."""
        if self._snowflake is None:
            raise RuntimeError("Snowflake module not initialized")
        return self._snowflake.get_generic_secret_string('api_key')
    
    def web_search(
        self,
        prompt: str,
        model: str = None,
        max_tokens: int = None,
        return_citations: bool = True,
        return_related_questions: bool = True
    ) -> dict:
        """
        Perform a web search using Perplexity API.
        
        Args:
            prompt: Search query/prompt
            model: Model name (sonar-pro, sonar). Default: sonar-pro
            max_tokens: Maximum tokens in response. Default: 4000
            return_citations: Whether to return source citations. Default: True
            return_related_questions: Whether to return related questions. Default: True
            
        Returns:
            dict: Structured response with success status, content, citations, etc.
        """
        model = model or self.DEFAULT_MODEL
        max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
        
        try:
            api_key = self._get_api_key()
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0,
                "return_citations": return_citations,
                "return_images": False,
                "return_related_questions": return_related_questions
            }
            
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=self.TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                return {
                    'success': True,
                    'prompt': prompt,
                    'model_used': model,
                    'content': content,
                    'citations': result.get('citations', []),
                    'related_questions': result.get('related_questions', []),
                    'usage': result.get('usage', {})
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'prompt': prompt
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'prompt': prompt
            }


# ============================================================================
# UDF Entry Points - These functions are called directly by Snowflake UDFs
# ============================================================================

def perplexity_web_search(prompt, model, max_tokens, return_citations, _snowflake_module):
    """
    UDF entry point for web search.
    
    Args:
        prompt: Search query
        model: Model name (sonar-pro, sonar)
        max_tokens: Maximum tokens
        return_citations: Whether to return citations
        _snowflake_module: The _snowflake module injected by Snowflake
        
    Returns:
        str: JSON string with results
    """
    handler = PerplexityHandler(_snowflake_module)
    result = handler.web_search(
        prompt=prompt,
        model=model,
        max_tokens=max_tokens,
        return_citations=return_citations
    )
    return json.dumps(result)

