"""
Tool Specs Module

Tool specifications (schemas) for Snowflake Cortex Agents.
These define what tools the agent can call - they map to UDFs in Snowflake.
"""

from . import gsuite_tools
from . import salesforce_tools
from . import perplexity_tools
from . import parallel_web_tools

# Registry of available tool sets
TOOL_REGISTRY = {
    "gsuite_tools": gsuite_tools.ALL_TOOLS,
    "salesforce_tools": salesforce_tools.ALL_TOOLS,
    "perplexity_tools": perplexity_tools.ALL_TOOLS,
    "parallel_web_tools": parallel_web_tools.ALL_TOOLS,
}

def get_tools(tool_set_names: list) -> list:
    """Get combined tools from multiple tool sets."""
    tools = []
    for name in tool_set_names:
        if name in TOOL_REGISTRY:
            tools.extend(TOOL_REGISTRY[name])
        else:
            raise ValueError(f"Unknown tool set: {name}. Available: {list(TOOL_REGISTRY.keys())}")
    return tools

