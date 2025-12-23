#!/bin/bash
# Setup Environment Variables

echo "════════════════════════════════════════════════════════"
echo "THE17PROJECT - Environment Setup"
echo "════════════════════════════════════════════════════════"
echo ""
echo "You need to configure 3 things:"
echo ""
echo "1. ANTHROPIC_API_KEY (Required)"
echo "   Get from: https://console.anthropic.com/settings/keys"
echo ""
echo "2. SHEET_ID (Required)"
echo "   Your Google Sheets ID from the URL"
echo ""
echo "3. SLACK_BOT_TOKEN + SLACK_CHANNEL_ID (Optional)"
echo "   For Slack notifications"
echo ""
echo "════════════════════════════════════════════════════════"
echo ""

read -p "Enter your ANTHROPIC_API_KEY: " ANTHROPIC_KEY
read -p "Enter your SHEET_ID: " SHEET_ID
read -p "Enter SLACK_BOT_TOKEN (or press Enter to skip): " SLACK_TOKEN
read -p "Enter SLACK_CHANNEL_ID (or press Enter to skip): " SLACK_CHANNEL

# Create .env file
cat > .env << EOF
# The17Project Environment Variables
ANTHROPIC_API_KEY=$ANTHROPIC_KEY
SHEET_ID=$SHEET_ID
EOF

if [ ! -z "$SLACK_TOKEN" ]; then
    echo "SLACK_BOT_TOKEN=$SLACK_TOKEN" >> .env
    echo "SLACK_CHANNEL_ID=$SLACK_CHANNEL" >> .env
fi

echo ""
echo "✅ .env file created!"
echo ""
echo "Test it:"
echo "  python3 src/main.py"
echo ""
