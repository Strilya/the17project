import json

# Paste your sessionid here
sessionid = "71047272092%3AKB1e7VyWrhvm8H%3A29%3AAYih6q4O4xHkfIbJM5oHkFFD6DzuiSYigQU8do3ArQ"

# Create minimal session structure
session_data = {
    "cookies": {
        "sessionid": sessionid
    },
    "authorization_data": {},
    "user_id": "",
    "device_settings": {},
    "user_agent": "Instagram 123.0.0.21.114 (iPhone; iOS 14_6; en_US; en-US; scale=2.00; 1170x2532; 190542906) AppleWebKit/420+"
}

# Save to file
with open('config/instagram_session.json', 'w') as f:
    json.dump(session_data, f, indent=2)

print("✅ Session file created at config/instagram_session.json")
