from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, SelectContactPointRecoveryForm, RecaptchaChallengeForm, TwoFactorRequired
from dotenv import load_dotenv
import os
import sys
import subprocess

load_dotenv()

username = os.getenv('INSTAGRAM_USERNAME')
password = os.getenv('INSTAGRAM_PASSWORD')

def challenge_code_handler(username, choice):
    """Handle Instagram verification code challenge"""
    print(f"\n📧 INSTAGRAM VERIFICATION CODE REQUIRED")
    print(f"=" * 70)
    print(f"Instagram sent a verification code to: {choice}")
    print(f"")
    print(f"CHECK THESE PLACES:")
    print(f"  1. Email linked to @{username}")
    print(f"  2. Phone number linked to @{username}")
    print(f"  3. Spam/Junk folder in email")
    print(f"  4. Instagram app notifications")
    print(f"")
    print(f"Code should arrive within 30 seconds...")
    print(f"=" * 70)

    code = input("\nEnter the 6-digit verification code: ").strip()
    return code

def change_password_handler(username):
    """Handle password change request from Instagram"""
    print(f"\n🔑 INSTAGRAM PASSWORD CHANGE REQUIRED")
    print(f"=" * 70)
    new_password = input("Enter new password for @{username}: ").strip()
    confirm = input("Confirm new password: ").strip()

    if new_password != confirm:
        print("❌ Passwords don't match!")
        sys.exit(1)

    print(f"⚠️  REMEMBER TO UPDATE .env FILE WITH NEW PASSWORD!")
    return new_password

# Get current IP
print("\n📡 Checking current network...")
try:
    ip = subprocess.check_output(['curl', '-s', 'ifconfig.me'], text=True).strip()
    print(f"   Current IP: {ip}")
except:
    print("   Could not determine IP")

print(f"\n📱 Logging into Instagram as @{username}...")
print(f"⚠️  If this fails, switch to mobile hotspot and try again")
print(f"=" * 70)

# Create client with challenge handlers
cl = Client()
cl.challenge_code_handler = challenge_code_handler
cl.change_password_handler = change_password_handler

try:
    print("\n🔐 Attempting login...")
    cl.login(username, password)

    # Save session
    os.makedirs('config', exist_ok=True)
    cl.dump_settings("config/instagram_session.json")

    print("\n" + "=" * 70)
    print("✅ LOGIN SUCCESSFUL!")
    print("=" * 70)
    print(f"✅ Session saved to config/instagram_session.json")
    print(f"")

    # Generate base64 for GitHub Secret
    print("GITHUB SECRET - Copy this entire string:")
    print("-" * 70)
    try:
        b64 = subprocess.check_output(
            ['sh', '-c', "cat config/instagram_session.json | base64 | tr -d '\\n'"],
            text=True
        )
        print(b64)
    except:
        print("(Run manually: cat config/instagram_session.json | base64 | tr -d '\\n')")

    print("-" * 70)
    print("\nNEXT STEPS:")
    print("1. Copy the base64 string above")
    print("2. Go to: GitHub → Settings → Secrets → Actions")
    print("3. Update secret: INSTAGRAM_SESSION")
    print("4. Paste the base64 string")
    print("5. Run workflow manually to test")
    print("=" * 70)

except TwoFactorRequired as e:
    print("\n❌ TWO-FACTOR AUTHENTICATION ENABLED")
    print("=" * 70)
    print("Instagram has 2FA enabled on this account.")
    print("")
    print("SOLUTION:")
    print("1. Go to Instagram app → Settings → Security")
    print("2. Temporarily disable Two-Factor Authentication")
    print("3. Run this script again")
    print("4. Re-enable 2FA after getting session")
    print("=" * 70)
    sys.exit(1)

except ChallengeRequired as e:
    print(f"\n⚠️  SECURITY CHALLENGE REQUIRED")
    print("=" * 70)
    print(f"Instagram triggered a security challenge.")
    print(f"")
    print(f"Attempting to resolve challenge automatically...")

    try:
        # Try to resolve challenge
        cl.challenge_resolve(cl.last_json)

        # If successful, try login again
        print("✅ Challenge resolved! Attempting login...")
        cl.login(username, password)

        # Save session
        os.makedirs('config', exist_ok=True)
        cl.dump_settings("config/instagram_session.json")

        print("\n✅ LOGIN SUCCESSFUL AFTER CHALLENGE!")
        print("✅ Session saved to config/instagram_session.json")

        # Generate base64
        print("\nGITHUB SECRET:")
        print("-" * 70)
        try:
            b64 = subprocess.check_output(
                ['sh', '-c', "cat config/instagram_session.json | base64 | tr -d '\\n'"],
                text=True
            )
            print(b64)
        except:
            print("(Run: cat config/instagram_session.json | base64 | tr -d '\\n')")
        print("-" * 70)

    except Exception as e2:
        print(f"\n❌ CHALLENGE RESOLUTION FAILED: {e2}")
        print("=" * 70)
        print("")
        print("TRY THESE SOLUTIONS:")
        print("")
        print("1. SWITCH TO MOBILE HOTSPOT:")
        print("   - Connect Mac to phone's cellular hotspot")
        print("   - Wait 2-3 minutes for stable connection")
        print("   - Run this script again")
        print("")
        print("2. VERIFY ACCOUNT:")
        print("   - Login to Instagram via mobile app")
        print("   - Complete any security prompts")
        print("   - Then run this script")
        print("")
        print("3. WAIT 1-2 HOURS:")
        print("   - Instagram may be rate-limiting")
        print("   - Try again later from mobile hotspot")
        print("=" * 70)
        sys.exit(1)

except Exception as e:
    print(f"\n❌ LOGIN FAILED")
    print("=" * 70)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    print("")
    print("TROUBLESHOOTING:")
    print("1. Verify credentials in .env file")
    print(f"   INSTAGRAM_USERNAME={username}")
    print("   INSTAGRAM_PASSWORD=***")
    print("")
    print("2. Try from mobile hotspot (cellular network)")
    print("3. Check Instagram account isn't locked")
    print("4. Disable 2FA if enabled")
    print("=" * 70)
    sys.exit(1)
