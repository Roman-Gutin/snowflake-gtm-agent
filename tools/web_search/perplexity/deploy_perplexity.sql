-- ============================================================================
-- Perplexity Web Search - Snowflake Deployment
-- ============================================================================
-- Deploy Perplexity API web search UDF to AGENTS_DEMO
-- Follows same pattern as gsuite and salesforce deployments
-- ============================================================================

USE ROLE AGENTS_SERVICE_ROLE;
USE DATABASE AGENTS_DEMO;
USE SCHEMA PUBLIC;
USE WAREHOUSE AGENTS_DEMO_WH;

-- ============================================================================
-- Step 1: Create Secret for Perplexity API Key (if not exists)
-- ============================================================================
-- NOTE: Set your API key using: python perplexity/set_api_key.py YOUR_KEY
-- Or run: ALTER SECRET PERPLEXITY_API_KEY SET SECRET_STRING = 'your-key';

-- CREATE SECRET IF NOT EXISTS PERPLEXITY_API_KEY
--     TYPE = GENERIC_STRING
--     SECRET_STRING = 'YOUR_PERPLEXITY_API_KEY_HERE';

-- ============================================================================
-- Step 2: Create the Web Search UDF (uses ALLOW_ALL_INTEGRATION)
-- ============================================================================

CREATE OR REPLACE FUNCTION PERPLEXITY_WEB_SEARCH(
    PROMPT VARCHAR,
    MODEL VARCHAR DEFAULT 'sonar-pro',
    MAX_TOKENS INTEGER DEFAULT 4000,
    RETURN_CITATIONS BOOLEAN DEFAULT TRUE
)
RETURNS VARCHAR
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('requests')
EXTERNAL_ACCESS_INTEGRATIONS = (PERPLEXITY_API_INTEGRATION)
SECRETS = ('api_key' = PERPLEXITY_API_KEY)
HANDLER = 'perplexity_search_handler'
COMMENT = 'AI-powered web search using Perplexity API. Returns current web information with citations.'
AS
$$
import json
import requests
import _snowflake

def perplexity_search_handler(prompt, model, max_tokens, return_citations):
    """Handler for Perplexity web search UDF."""
    try:
        api_key = _snowflake.get_generic_secret_string('api_key')
        api_url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0,
            "return_citations": return_citations,
            "return_images": False,
            "return_related_questions": True
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            return json.dumps({
                'success': True,
                'prompt': prompt,
                'model_used': model,
                'content': content,
                'citations': result.get('citations', []),
                'related_questions': result.get('related_questions', []),
                'usage': result.get('usage', {})
            })
        else:
            return json.dumps({
                'success': False,
                'error': f'HTTP {response.status_code}: {response.text}',
                'prompt': prompt
            })
            
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e),
            'prompt': prompt
        })
$$;

-- ============================================================================
-- Step 6: Verify Deployment
-- ============================================================================

SHOW FUNCTIONS LIKE 'PERPLEXITY_WEB_SEARCH' IN SCHEMA AGENTS_DEMO.PUBLIC;

-- ============================================================================
-- Step 7: Test (after setting API key)
-- ============================================================================
-- SELECT PERPLEXITY_WEB_SEARCH('What is Snowflake Inc?') AS result;
-- SELECT PERPLEXITY_WEB_SEARCH('Latest news about AI agents', 'sonar', 2000, TRUE) AS result;

