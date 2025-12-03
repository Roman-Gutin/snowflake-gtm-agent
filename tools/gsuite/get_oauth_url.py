"""
Generate OAuth URL for Google OAuth Playground

This script helps you obtain a refresh token for Google Workspace APIs.
You must provide your own OAuth credentials from Google Cloud Console.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ ERROR: Missing Google OAuth credentials!")
    print("\nPlease set these in your .env file:")
    print("  GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com")
    print("  GOOGLE_CLIENT_SECRET=your-client-secret")
    print("\nGet credentials from: https://console.cloud.google.com/apis/credentials")
    exit(1)

# All scopes needed for Google Workspace integration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
]

print("="*70)
print("GOOGLE OAUTH - GET REFRESH TOKEN")
print("="*70)
print("\n📋 INSTRUCTIONS:")
print("\n1. Go to: https://developers.google.com/oauthplayground/")
print("\n2. Click the gear icon (⚙️) in the top right")
print("\n3. Check 'Use your own OAuth credentials'")
print("\n4. Enter:")
print(f"   OAuth Client ID: {CLIENT_ID}")
print(f"   OAuth Client secret: {CLIENT_SECRET}")
print("\n5. In Step 1, manually enter these scopes (one per line):")
print("   " + "-"*60)
for scope in SCOPES:
    print(f"   {scope}")
print("   " + "-"*60)
print("\n6. Click 'Authorize APIs'")
print("\n7. Sign in and grant permissions")
print("\n8. Click 'Exchange authorization code for tokens'")
print("\n9. Copy the 'refresh_token' from the response")
print("\n10. Run: python tools/gsuite/create_oauth_secret.py <refresh_token>")
print("\n" + "="*70)
print("\n✅ SCOPES INCLUDED:")
print("   ✓ Google Sheets (read/write)")
print("   ✓ Google Drive (full access)")
print("   ✓ Google Docs (read/write)")
print("\n" + "="*70)

