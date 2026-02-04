"""
Instagram Login with Challenge Handler
Handles security challenges by requesting verification code
"""
import os
from dotenv import load_dotenv
from instagrapi import Client

load_dotenv()

def get_code_from_user(username, choice):
    """Prompt user for verification code"""
    print(f"\n{'='*50}")
    print(f"Instagram requires verification for @{username}")
    print(f"Method: {choice}")
    print(f"{'='*50}")
    code = input("Enter the verification code: ").strip()
    return code

def main():
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    if not username or not password:
        print("❌ Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env")
        return False

    print(f"📱 Logging into Instagram as @{username}...")

    client = Client()
    client.challenge_code_handler = get_code_from_user

    try:
        client.login(username, password)

        # Save session
        os.makedirs('config', exist_ok=True)
        session_file = 'config/instagram_session.json'
        client.dump_settings(session_file)

        print(f"\n✅ Login successful!")
        print(f"✅ Session saved to: {session_file}")

        # Generate base64
        import base64
        with open(session_file, 'rb') as f:
            session_b64 = base64.b64encode(f.read()).decode('utf-8')

        print("\n" + "="*70)
        print("COPY THIS BASE64 STRING TO GITHUB SECRET:")
        print("="*70)
        print(session_b64)
        print("="*70)

        return True

    except Exception as e:
        print(f"❌ Login failed: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    main()
