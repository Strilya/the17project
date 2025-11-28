#!/bin/bash

echo "=================================================="
echo "The17Project - EXTREME VARIETY UPGRADE"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}This script will:${NC}"
echo "1. Backup your current video generator files"
echo "2. Install the new EXTREME VARIETY system"
echo "3. Check that all fonts are available"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Setup cancelled."
    exit 1
fi

echo ""
echo "=================================================="
echo "STEP 1: Backing up current files..."
echo "=================================================="

# Backup current files
if [ -f "video_generator.py" ]; then
    cp video_generator.py video_generator_backup_$(date +%Y%m%d_%H%M%S).py
    echo -e "${GREEN}✓${NC} Backed up video_generator.py"
else
    echo -e "${YELLOW}⚠${NC} No existing video_generator.py found"
fi

if [ -f "video_config.json" ]; then
    cp video_config.json video_config_backup_$(date +%Y%m%d_%H%M%S).json
    echo -e "${GREEN}✓${NC} Backed up video_config.json"
else
    echo -e "${YELLOW}⚠${NC} No existing video_config.json found"
fi

echo ""
echo "=================================================="
echo "STEP 2: Installing new files..."
echo "=================================================="

# Install new files
if [ -f "video_generator_v2.py" ]; then
    cp video_generator_v2.py video_generator.py
    echo -e "${GREEN}✓${NC} Installed video_generator.py (V2)"
else
    echo -e "${RED}✗${NC} video_generator_v2.py not found!"
    exit 1
fi

if [ -f "video_config_v2.json" ]; then
    cp video_config_v2.json video_config.json
    echo -e "${GREEN}✓${NC} Installed video_config.json (V2)"
else
    echo -e "${RED}✗${NC} video_config_v2.json not found!"
    exit 1
fi

echo ""
echo "=================================================="
echo "STEP 3: Checking fonts..."
echo "=================================================="

# Check fonts directory
if [ ! -d "fonts" ]; then
    echo -e "${YELLOW}⚠${NC} Creating fonts/ directory..."
    mkdir -p fonts
fi

# Check for required fonts
FONTS_OK=true

if [ -f "fonts/DejaVuSans.ttf" ]; then
    echo -e "${GREEN}✓${NC} DejaVuSans.ttf found"
else
    echo -e "${YELLOW}⚠${NC} DejaVuSans.ttf missing (will use default)"
    FONTS_OK=false
fi

if [ -f "fonts/DejaVuSans-Bold.ttf" ]; then
    echo -e "${GREEN}✓${NC} DejaVuSans-Bold.ttf found"
else
    echo -e "${YELLOW}⚠${NC} DejaVuSans-Bold.ttf missing (will use default)"
    FONTS_OK=false
fi

if [ -f "fonts/DejaVuSerif.ttf" ]; then
    echo -e "${GREEN}✓${NC} DejaVuSerif.ttf found"
else
    echo -e "${YELLOW}⚠${NC} DejaVuSerif.ttf missing (will use default)"
    FONTS_OK=false
fi

if [ -f "fonts/DejaVuSerif-Bold.ttf" ]; then
    echo -e "${GREEN}✓${NC} DejaVuSerif-Bold.ttf found"
else
    echo -e "${YELLOW}⚠${NC} DejaVuSerif-Bold.ttf missing (will use default)"
    FONTS_OK=false
fi

echo ""
echo "=================================================="
echo "STEP 4: Creating output directories..."
echo "=================================================="

mkdir -p output/reels
mkdir -p output/audio
mkdir -p output/background_cache

echo -e "${GREEN}✓${NC} Output directories created"

echo ""
echo "=================================================="
echo "INSTALLATION COMPLETE!"
echo "=================================================="
echo ""

if [ "$FONTS_OK" = true ]; then
    echo -e "${GREEN}✓ All fonts available${NC}"
    echo "  System will use all 4 font families"
else
    echo -e "${YELLOW}⚠ Some fonts missing${NC}"
    echo "  System will work but will use default fonts for missing ones"
    echo "  For best results, add missing fonts to fonts/ directory"
fi

echo ""
echo "Your system now has:"
echo "  • 5 complete visual styles"
echo "  • 4 font families" 
echo "  • 30+ unique colors"
echo "  • 3 text positions"
echo "  • 80+ background searches"
echo "  • Smart rotation system"
echo ""
echo "Test it out:"
echo "  python video_generator.py"
echo ""
echo "Generate 5 videos to see variety:"
echo "  for i in {1..5}; do python video_generator.py; done"
echo ""
echo -e "${GREEN}Happy creating! 🎨${NC}"
echo ""
