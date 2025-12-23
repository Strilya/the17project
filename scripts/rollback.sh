#!/bin/bash
# Emergency Rollback Script

set -e

echo "🚨 EMERGENCY ROLLBACK PROCEDURE"
echo "================================"
echo ""
echo "This will revert to the last stable version (v1.0-stable)"
echo ""
read -p "Are you sure you want to rollback? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Rollback cancelled."
    exit 0
fi

cd /Users/ilyastr/Desktop/the17Project || exit 1

echo ""
echo "Step 1: Checking out master branch..."
git checkout master

echo "Step 2: Resetting to v1.0-stable tag..."
git reset --hard v1.0-stable

echo "Step 3: Cleaning any uncommitted files..."
git clean -fd

echo ""
echo "✅ ROLLBACK COMPLETE"
echo ""
echo "Your code is now back to the stable working version."
echo "Testing original workflow..."
echo ""

python3 src/main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Original workflow working correctly"
    echo ""
    echo "You are now on: $(git branch --show-current)"
    echo "At commit: $(git log --oneline -1)"
else
    echo ""
    echo "❌ Original workflow failed"
    echo "This is unexpected. Check logs."
fi
