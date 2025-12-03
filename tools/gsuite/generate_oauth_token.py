#!/usr/bin/env python3
"""
Generate OAuth refresh token for Google Workspace APIs

This script will:
1. Open a browser for you to authorize the app
2. Generate a refresh token that lasts as long as possible
3. Save the credentials to a file

SETUP:
1. Go to https://console.cloud.google.com/apis/credentials?project=scaleroman
2. Create OAuth 2.0 Client ID (Desktop app)
3. Download the JSON file
4. Run this script and provide the client ID and secret when prompted
"""

import json
import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Load environment variables from .env
load_dotenv()

# Scopes for Google Workspace APIs
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

def generate_refresh_token():
    """Generate OAuth refresh token using credentials from .env"""

    print("="*80)
    print("GOOGLE WORKSPACE OAUTH TOKEN GENERATOR")
    print("="*80)
    print()

    # Auto-load from .env
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("❌ Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in .env!")
        return

    print(f"✅ Loaded credentials from .env")
    print(f"   Client ID: {client_id[:20]}...")
    print()
    print("Opening browser for authorization...")
    print("Sign in and click 'Allow' when prompted.")
    print()
    
    # Create client config
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
        }
    }
    
    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        
        # This will open a browser window
        creds = flow.run_local_server(
            port=0,
            authorization_prompt_message='Opening browser for authorization...',
            success_message='Authorization successful! You can close this window.',
            open_browser=True
        )
        
        print()
        print("="*80)
        print("✅ SUCCESS! Token generated")
        print("="*80)
        print()
        
        # Extract credentials
        credentials_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': creds.refresh_token,
            'token_uri': 'https://oauth2.googleapis.com/token',
            'scopes': SCOPES
        }
        
        # Save to file
        output_file = 'tools/gsuite/oauth_credentials.json'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(credentials_data, f, indent=2)
        
        print(f"✅ Credentials saved to: {output_file}")
        print()
        print("="*80)
        print("CREDENTIALS")
        print("="*80)
        print()
        print(f"Client ID: {client_id}")
        print(f"Client Secret: {client_secret}")
        print(f"Refresh Token: {creds.refresh_token}")
        print()
        print("="*80)
        print("IMPORTANT: Token Longevity")
        print("="*80)
        print()
        print("Your refresh token will remain valid as long as:")
        print("✅ You use it at least once every 6 months")
        print("✅ You don't revoke access in your Google account")
        print("✅ You don't change your Google password")
        print()
        print("To maximize token lifetime:")
        print("- The automated workflows will use it regularly (keeps it active)")
        print("- Don't manually revoke access in Google account settings")
        print("- Keep the client secret secure")
        print()
        print("="*80)
        print("NEXT STEPS")
        print("="*80)
        print()
        print("Provide these credentials to complete the OAuth setup:")
        print()
        print(f"CLIENT_ID={client_id}")
        print(f"CLIENT_SECRET={client_secret}")
        print(f"REFRESH_TOKEN={creds.refresh_token}")
        print()
        
    except Exception as e:
        print()
        print(f"❌ Error generating token: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("TROUBLESHOOTING:")
        print("- Make sure OAuth client is created in Google Cloud Console")
        print("- Make sure APIs are enabled (Docs, Drive, Sheets)")
        print("- Try using 'Desktop app' type for OAuth client")

if __name__ == '__main__':
    generate_refresh_token()

