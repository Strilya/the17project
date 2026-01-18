"""
One-time script to create Instagram session file
Run this locally once: python login_instagram.py
Session file saved to: config/instagram_session.json
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
        print("\nNEXT STEPS:")
        print("1. Copy the content of config/instagram_session.json")
        print("2. Go to GitHub repo → Settings → Secrets and variables → Actions")
        print("3. Create new secret: INSTAGRAM_SESSION")
        print("4. Paste the entire JSON content as the value")
        print("5. The session file will be restored automatically in GitHub Actions")

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
