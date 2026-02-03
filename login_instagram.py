"""
Instagram Session Login Script
===============================

PURPOSE:
- Initial setup: Create Instagram session for first-time authentication
- Session refresh: Regenerate session when it expires (~90 days)

USAGE:
    python login_instagram.py

OUTPUT:
- Saves session to: config/instagram_session.json
- Prints base64-encoded string for GitHub Secret INSTAGRAM_SESSION

WHEN TO RUN:
- First time setting up Instagram automation
- When GitHub Actions fails with LoginRequired or authentication errors
- After changing Instagram password
- Every ~90 days as sessions expire

DOCUMENTATION:
See INSTAGRAM_SETUP.md for full setup and refresh instructions
"""

import os
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired, ChallengeRequired, LoginRequired

load_dotenv()

def create_session():
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    if not username or not password:
        print("❌ ERROR: INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD must be set in .env")
        return False

    print(f"📱 Logging into Instagram as @{username}...")

    client = Client()
    session_file = 'config/instagram_session.json'

    try:
        os.makedirs('config', exist_ok=True)

        client.login(username, password)
        client.dump_settings(session_file)

        print(f"✅ Instagram login successful!")
        print(f"✅ Session saved to: {session_file}")

        # Read and base64 encode the session file
        import base64
        with open(session_file, 'rb') as f:
            session_data = f.read()
            session_b64 = base64.b64encode(session_data).decode('utf-8')

        print("\n" + "="*70)
        print("COPY THIS BASE64 STRING TO GITHUB SECRET:")
        print("="*70)
        print(session_b64)
        print("="*70)
        print("\nNEXT STEPS:")
        print("1. Copy the base64 string above")
        print("2. Go to GitHub repo → Settings → Secrets and variables → Actions")
        print("3. Create new secret: INSTAGRAM_SESSION")
        print("4. Paste the base64 string as the value")
        print("5. The workflow will decode and restore the session automatically")

        return True

    except TwoFactorRequired:
        print("❌ Two-factor authentication is enabled.")
        print("   Disable 2FA temporarily or provide verification code manually")
        return False

    except ChallengeRequired:
        print("❌ Instagram security challenge required.")
        print("   Login manually through Instagram app first, then try again")
        return False

    except LoginRequired:
        print("❌ Login failed. Check your credentials in .env")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = create_session()
    exit(0 if success else 1)
