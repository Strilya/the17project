#!/bin/bash
# A/B Testing Script - Generate and compare both versions

set -e  # Exit on error

echo "🧪 THE17PROJECT A/B TESTING"
echo "================================"
echo ""

cd /Users/ilyastr/Desktop/the17Project || exit 1

# Ensure we're on feature branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "feature/improved-content-hooks" ]; then
    echo "❌ ERROR: Not on feature/improved-content-hooks branch"
    echo "   Current branch: $BRANCH"
    echo "   Run: git checkout feature/improved-content-hooks"
    exit 1
fi

echo "📦 Test 1: Generating with ORIGINAL content (V1)..."
echo "---------------------------------------------------"
export USE_V2_CONTENT=false
python src/main_v2.py

if [ $? -ne 0 ]; then
    echo "❌ V1 generation failed"
    exit 1
fi

echo ""
echo "✅ V1 content generated successfully"
echo ""
echo "Waiting 5 seconds before next generation..."
sleep 5

echo "🆕 Test 2: Generating with IMPROVED content (V2)..."
echo "---------------------------------------------------"
export USE_V2_CONTENT=true
python src/main_v2.py

if [ $? -ne 0 ]; then
    echo "❌ V2 generation failed"
    exit 1
fi

echo ""
echo "✅ V2 content generated successfully"
echo ""
echo "================================"
echo "✅ A/B TEST COMPLETE"
echo "================================"
echo ""
echo "📱 Check your Slack for both videos."
echo ""
echo "📊 Next steps:"
echo "1. Post BOTH videos to Instagram"
echo "2. Track performance in Google Sheets:"
echo "   - Add columns: content_version, hook_style"
echo "   - After posting, add: views, likes, comments, followers_gained"
echo "3. After 7 days, compare metrics"
echo "4. Run: python scripts/compare_performance.py"
echo ""
