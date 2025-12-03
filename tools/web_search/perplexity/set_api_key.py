#!/usr/bin/env python3
"""
Set Perplexity API Key in Snowflake

Usage:
    python set_api_key.py YOUR_PERPLEXITY_API_KEY
    
Get your API key from: https://www.perplexity.ai/settings/api
"""

import sys
import os
from pathlib import Path

# Load .env
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

import snowflake.connector

def set_perplexity_api_key(api_key: str):
    """Update the Perplexity API key secret in Snowflake."""
    
    conn = snowflake.connector.connect(
        account=os.environ['SNOWFLAKE_ACCOUNT'],
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PAT'],
        warehouse='AGENTS_DEMO_WH',
        database='AGENTS_DEMO',
        schema='PUBLIC',
        role='AGENTS_SERVICE_ROLE'
    )
    
    try:
        cursor = conn.cursor()
        
        # Update the secret
        sql = f"""
        CREATE OR REPLACE SECRET PERPLEXITY_API_KEY
            TYPE = GENERIC_STRING
            SECRET_STRING = '{api_key}'
        """
        cursor.execute(sql)
        print("✅ Perplexity API key updated successfully!")
        
        # Verify
        cursor.execute("SHOW SECRETS LIKE 'PERPLEXITY_API_KEY'")
        result = cursor.fetchone()
        if result:
            print(f"   Secret: {result[1]}")
            print(f"   Type: {result[3]}")
            
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python set_api_key.py YOUR_PERPLEXITY_API_KEY")
        print("\nGet your API key from: https://www.perplexity.ai/settings/api")
        sys.exit(1)
    
    api_key = sys.argv[1]
    set_perplexity_api_key(api_key)

