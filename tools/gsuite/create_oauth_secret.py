"""
Create Google OAuth secret in Snowflake

This script creates the OAuth security integration and secret in Snowflake
using credentials from .env file and the refresh token you obtained.

Usage:
    python tools/gsuite/create_oauth_secret.py <refresh_token>
"""

import os
import sys
from dotenv import load_dotenv
import snowflake.connector

# Load environment variables
load_dotenv()

if len(sys.argv) < 2:
    print("❌ ERROR: Missing refresh token!")
    print("\nUsage: python tools/gsuite/create_oauth_secret.py <refresh_token>")
    print("\nGet refresh token by running: python tools/gsuite/get_oauth_url.py")
    exit(1)

REFRESH_TOKEN = sys.argv[1]

# Get credentials from environment
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PAT = os.getenv('SNOWFLAKE_PAT')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# Validate all required variables
missing = []
if not SNOWFLAKE_ACCOUNT: missing.append('SNOWFLAKE_ACCOUNT')
if not SNOWFLAKE_USER: missing.append('SNOWFLAKE_USER')
if not SNOWFLAKE_PAT: missing.append('SNOWFLAKE_PAT')
if not GOOGLE_CLIENT_ID: missing.append('GOOGLE_CLIENT_ID')
if not GOOGLE_CLIENT_SECRET: missing.append('GOOGLE_CLIENT_SECRET')

if missing:
    print(f"❌ ERROR: Missing environment variables: {', '.join(missing)}")
    print("\nPlease set these in your .env file")
    exit(1)

print("="*70)
print("CREATING GOOGLE OAUTH SECRET IN SNOWFLAKE")
print("="*70)

try:
    # Connect to Snowflake using PAT (programmatic access token as password)
    print("\n[1/4] Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PAT,
        warehouse='AGENTS_DEMO_WH',
        database='AGENTS_DEMO',
        schema='PUBLIC',
        role='AGENTS_SERVICE_ROLE'
    )
    cursor = conn.cursor()
    print("✅ Connected")

    # Create security integration
    print("\n[2/4] Creating OAuth security integration...")
    cursor.execute(f"""
        CREATE OR REPLACE SECURITY INTEGRATION google_workspace_oauth
          TYPE = API_AUTHENTICATION
          AUTH_TYPE = OAUTH2
          OAUTH_CLIENT_ID = '{GOOGLE_CLIENT_ID}'
          OAUTH_CLIENT_SECRET = '{GOOGLE_CLIENT_SECRET}'
          OAUTH_TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
          OAUTH_AUTHORIZATION_ENDPOINT = 'https://accounts.google.com/o/oauth2/auth'
          OAUTH_ALLOWED_SCOPES = (
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents'
          )
          ENABLED = TRUE
    """)
    print("✅ Security integration created")

    # Create secret
    print("\n[3/4] Creating OAuth secret...")
    cursor.execute(f"""
        CREATE OR REPLACE SECRET google_oauth_secret
          TYPE = OAUTH2
          API_AUTHENTICATION = google_workspace_oauth
          OAUTH_REFRESH_TOKEN = '{REFRESH_TOKEN}'
    """)
    print("✅ OAuth secret created")

    # Verify
    print("\n[4/4] Verifying...")
    cursor.execute("SHOW SECRETS LIKE 'google_oauth_secret'")
    result = cursor.fetchone()
    if result:
        print("✅ Secret verified")
    else:
        print("⚠️  Warning: Could not verify secret")

    cursor.close()
    conn.close()

    print("\n" + "="*70)
    print("✅ SUCCESS! Google OAuth secret created in Snowflake")
    print("="*70)
    print("\nNext step: Run deployment script to create UDFs")
    print("  python deployment/deploy_gsuite.py")
    print("="*70)

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    exit(1)

