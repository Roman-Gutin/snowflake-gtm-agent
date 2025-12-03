#!/usr/bin/env python3
"""
Build Agent

Generic agent builder that combines a config with tool sets.

Usage:
    python build_agent.py gtm_engineer          # Build GTM Engineer agent
    python build_agent.py gtm_engineer --delete # Delete then rebuild
    python build_agent.py --list                # List available configs
"""

import argparse
import requests
import json
import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from configs import get_config, CONFIG_REGISTRY
from tool_specs import get_tools

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Snowflake config
SNOWFLAKE_ACCOUNT_BASE_URL = f"https://{os.environ['SNOWFLAKE_ACCOUNT']}.snowflakecomputing.com"
PAT = os.environ['SNOWFLAKE_PAT']

# Agent location (where it appears in Snowsight)
AGENT_DATABASE = "snowflake_intelligence"
AGENT_SCHEMA = "agents"

# Functions location (where UDFs are deployed)
FUNCTIONS_DATABASE = "AGENTS_DEMO"
FUNCTIONS_SCHEMA = "PUBLIC"
WAREHOUSE = "AGENTS_DEMO_WH"


def build_tool_resources(tools: list) -> dict:
    """Build tool_resources mapping from tools list."""
    resources = {}
    for tool in tools:
        tool_name = tool["tool_spec"]["name"]
        function_name = tool_name.upper()
        resources[tool_name] = {
            "type": "function",
            "execution_environment": {
                "type": "warehouse",
                "warehouse": WAREHOUSE
            },
            "identifier": f"{FUNCTIONS_DATABASE}.{FUNCTIONS_SCHEMA}.{function_name}"
        }
    return resources


def delete_agent(agent_name: str) -> bool:
    """Delete an existing agent."""
    url = f"{SNOWFLAKE_ACCOUNT_BASE_URL}/api/v2/databases/{AGENT_DATABASE}/schemas/{AGENT_SCHEMA}/agents/{agent_name}"
    headers = {
        "Authorization": f"Bearer {PAT}",
        "X-Snowflake-Role": "AGENTS_SERVICE_ROLE"
    }
    
    print(f"Deleting agent: {agent_name}...")
    response = requests.delete(url, headers=headers)
    
    if response.status_code in [200, 204]:
        print(f"✅ Deleted {agent_name}")
        return True
    elif response.status_code == 404:
        print(f"Agent {agent_name} does not exist (nothing to delete)")
        return True
    else:
        print(f"❌ Failed to delete: {response.text}")
        return False


def create_agent(config) -> bool:
    """Create an agent from a config module."""
    # Get tools from config's TOOL_SETS
    tools = get_tools(config.TOOL_SETS)
    tool_resources = build_tool_resources(tools)
    
    # Build payload
    payload = {
        "name": config.AGENT_NAME,
        "comment": config.AGENT_COMMENT,
        "models": {
            "orchestration": config.MODEL
        },
        "instructions": config.INSTRUCTIONS,
        "tools": tools,
        "tool_resources": tool_resources
    }
    
    url = f"{SNOWFLAKE_ACCOUNT_BASE_URL}/api/v2/databases/{AGENT_DATABASE}/schemas/{AGENT_SCHEMA}/agents"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {PAT}",
        "X-Snowflake-Role": "AGENTS_SERVICE_ROLE"
    }
    
    print(f"\nCreating agent: {config.AGENT_NAME}")
    print(f"  Model: {config.MODEL}")
    print(f"  Tools: {len(tools)} total from {config.TOOL_SETS}")
    print()
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Agent {config.AGENT_NAME} created successfully!")
        return True
    else:
        print(f"❌ Failed to create agent: {response.status_code}")
        print(response.text)
        return False


def main():
    parser = argparse.ArgumentParser(description="Build Snowflake Cortex Agent")
    parser.add_argument("config", nargs="?", help="Config name (e.g., gtm_engineer)")
    parser.add_argument("--delete", action="store_true", help="Delete agent before creating")
    parser.add_argument("--list", action="store_true", help="List available configs")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available agent configs:")
        for name in CONFIG_REGISTRY:
            cfg = CONFIG_REGISTRY[name]
            print(f"  - {name}: {cfg.AGENT_NAME} ({cfg.MODEL})")
        return
    
    if not args.config:
        parser.print_help()
        return
    
    config = get_config(args.config)
    
    if args.delete:
        delete_agent(config.AGENT_NAME)
    
    create_agent(config)


if __name__ == "__main__":
    main()

