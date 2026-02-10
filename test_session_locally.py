"""
Test Instagram Session Locally
===============================

Verifies that config/instagram_session.json works before using in GitHub Actions.
"""

from instagrapi import Client
import os
import sys

session_file = 'config/instagram_session.json'

print("=" * 70)
print("TESTING INSTAGRAM SESSION LOCALLY")
print("=" * 70)

# Check file exists
if not os.path.exists(session_file):
    print(f"\n❌ Session file not found: {session_file}")
    print("\nRun: python3 login_instagram.py")
    sys.exit(1)

# Check file size
file_size = os.path.getsize(session_file)
print(f"\n✅ Session file exists: {session_file}")
print(f"   File size: {file_size} bytes")

if file_size == 0:
    print("\n❌ Session file is empty!")
    sys.exit(1)

# Validate JSON
import json
try:
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    print(f"✅ Session is valid JSON")
except json.JSONDecodeError as e:
    print(f"\n❌ Session is not valid JSON: {e}")
    sys.exit(1)

# Test loading with instagrapi
print(f"\n🔐 Testing Instagram authentication...")
try:
    cl = Client()
    cl.load_settings(session_file)
    print(f"✅ Session loaded into client")

    # Try to get account info
    info = cl.account_info()
    print(f"✅ Authenticated as: @{info.username}")
    print(f"   User ID: {info.pk}")
    print(f"   Followers: {info.follower_count}")
    print(f"\n" + "=" * 70)
    print("✅ SESSION TEST PASSED - Ready for GitHub Actions!")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ Authentication failed: {type(e).__name__}")
    print(f"   Error: {e}")
    print(f"\n" + "=" * 70)
    print("SESSION IS INVALID - Need to regenerate")
    print("=" * 70)
    print("\nRun: python3 login_instagram.py (from mobile hotspot)")
    sys.exit(1)
