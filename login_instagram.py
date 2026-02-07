"""
Instagram Login - ONE TIME ONLY
================================

PURPOSE: Login ONCE and save session. Session lasts ~90 days.

IMPORTANT: Run this from mobile hotspot/cellular network to avoid API blocks.

WHEN TO RUN:
1. First time setup
2. When session expires (~90 days)
3. After changing Instagram password

STEPS BEFORE RUNNING:
1. Connect Mac to mobile hotspot (cellular network)
2. Wait 2-3 minutes for stable connection
3. Run: python3 login_instagram.py
4. Copy config/instagram_session.json content
5. Add to GitHub Secret: INSTAGRAM_SESSION
6. Switch back to regular WiFi

DO NOT RUN THIS FROM REGULAR WIFI - it will trigger Error 572
"""

from instagrapi import Client
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('INSTAGRAM_USERNAME')
password = os.getenv('INSTAGRAM_PASSWORD')

if not username or not password:
    print("❌ ERROR: INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD must be set in .env")
    exit(1)

print(f"📱 Logging into Instagram as @{username}...")
print("   NOTE: This should be run from mobile hotspot to avoid API blocks")

# Create config directory
os.makedirs('config', exist_ok=True)

cl = Client()
cl.login(username, password)

# Save session
session_file = "config/instagram_session.json"
cl.dump_settings(session_file)

print("✅ Instagram login successful!")
print(f"✅ Session saved to: {session_file}")

print("\n" + "="*70)
print("NEXT STEPS:")
print("="*70)
print("1. Copy the ENTIRE content of config/instagram_session.json")
print("2. Go to GitHub → Settings → Secrets → Actions")
print("3. Create/update secret: INSTAGRAM_SESSION")
print("4. Paste the JSON content as the value")
print("5. Session will auto-restore in GitHub Actions")
print("6. This session lasts ~90 days - no more logins needed!")
print("="*70)
