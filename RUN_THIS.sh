#!/bin/bash
# THE17PROJECT - SIMPLE RUN COMMANDS

cd /Users/ilyastr/Desktop/the17Project

echo "════════════════════════════════════════════════════════"
echo "THE17PROJECT - Choose what to generate:"
echo "════════════════════════════════════════════════════════"
echo ""
echo "1) Generate V1 (Original - generic hooks)"
echo "2) Generate V2 (Improved - controversial hooks)"
echo "3) Generate BOTH (A/B test)"
echo ""
read -p "Enter choice (1, 2, or 3): " choice

case $choice in
    1)
        echo ""
        echo "Generating V1 (Original)..."
        python3 src/main.py
        ;;
    2)
        echo ""
        echo "Generating V2 (Improved)..."
        USE_V2_CONTENT=true python3 src/main_v2.py
        ;;
    3)
        echo ""
        echo "Generating V1..."
        python3 src/main.py
        echo ""
        echo "Waiting 5 seconds..."
        sleep 5
        echo ""
        echo "Generating V2..."
        USE_V2_CONTENT=true python3 src/main_v2.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ DONE! Check Slack for your video(s)"
echo "════════════════════════════════════════════════════════"
