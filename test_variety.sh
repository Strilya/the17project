#!/bin/bash

echo "=================================================="
echo "Testing Video Variety System"
echo "Generating 3 consecutive videos..."
echo "=================================================="

for i in {1..3}; do
  echo ""
  echo "===================================="
  echo "GENERATING VIDEO $i/3"
  echo "===================================="
  
  python3 src/main_v2.py
  
  if [ $? -eq 0 ]; then
    echo "✅ Video $i generated successfully"
  else
    echo "❌ Video $i failed"
    exit 1
  fi
  
  echo ""
  sleep 2
done

echo ""
echo "=================================================="
echo "All 3 videos generated!"
echo "=================================================="
echo ""
echo "Checking generated videos:"
ls -lht output/reels/ | head -5
