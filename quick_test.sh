#!/bin/bash

# Quick Test Script for The17Project Automation
# This script helps you test the system locally before deploying

set -e  # Exit on error

echo "================================================"
echo "  The17Project - Quick Test Script"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Check if .env file exists
if [ ! -f "config/.env" ]; then
    echo -e "${RED}Error: config/.env file not found!${NC}"
    echo "Please copy config/.env.example to config/.env and add your credentials."
    echo "Run: cp config/.env.example config/.env"
    exit 1
fi

echo ""
echo "================================================"
echo "  Testing Individual Modules"
echo "================================================"
echo ""

# Test 1: Content Generation
echo -e "${YELLOW}[1/3] Testing content generation (OpenAI)...${NC}"
if python src/generate_content.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Content generation working!${NC}"
else
    echo -e "${RED}✗ Content generation failed. Check your OPENAI_API_KEY${NC}"
    exit 1
fi

# Test 2: Google Sheets
echo -e "${YELLOW}[2/3] Testing Google Sheets integration...${NC}"
if python src/save_to_sheets.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Google Sheets integration working!${NC}"
else
    echo -e "${RED}✗ Google Sheets integration failed. Check your credentials${NC}"
    exit 1
fi

# Test 3: Slack
echo -e "${YELLOW}[3/3] Testing Slack notifications...${NC}"
if python src/send_slack_notification.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Slack notifications working!${NC}"
else
    echo -e "${RED}✗ Slack notifications failed. Check your SLACK_BOT_TOKEN${NC}"
    exit 1
fi

echo ""
echo "================================================"
echo "  Running Full Workflow"
echo "================================================"
echo ""

# Run full workflow
echo -e "${YELLOW}Running complete workflow...${NC}"
if python src/main.py; then
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}  ✓ All tests passed!${NC}"
    echo -e "${GREEN}  Your automation is ready to deploy!${NC}"
    echo -e "${GREEN}================================================${NC}"
else
    echo -e "${RED}Full workflow failed. Check the logs above.${NC}"
    exit 1
fi

echo ""
echo "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Add secrets to GitHub repository (see SETUP_GUIDE.md)"
echo "3. Test with manual workflow trigger"
echo "4. Wait for daily scheduled run at 8 AM EST"
echo ""
