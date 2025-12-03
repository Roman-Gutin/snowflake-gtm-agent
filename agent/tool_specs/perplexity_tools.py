"""
Perplexity Tools

Tool definitions for Perplexity web search.
"""

ALL_TOOLS = [
    {
        "tool_spec": {
            "type": "generic",
            "name": "PERPLEXITY_WEB_SEARCH",
            "description": "AI-powered web search using Perplexity API. Returns current information from the web with citations. Use for questions about current events, recent news, company information, or when up-to-date information is needed. Uses sonar-pro model with citations enabled by default.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "PROMPT": {
                        "type": "string",
                        "description": "The search query or question to answer using web search"
                    }
                },
                "required": ["PROMPT"]
            }
        }
    }
]

