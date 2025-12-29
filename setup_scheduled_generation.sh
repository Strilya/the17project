#!/bin/bash

# ============================================================================
# The17Project - Scheduled Reel Generation Setup
# Creates launchd jobs for macOS to generate reels at 7 AM, 2 PM, and 7 PM
# ============================================================================

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_PATH=$(which python3)
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "========================================================================"
echo "THE17PROJECT - SCHEDULED GENERATION SETUP"
echo "========================================================================"
echo ""
echo "Project Directory: $PROJECT_DIR"
echo "Python Path: $PYTHON_PATH"
echo "Launch Agents Directory: $LAUNCH_AGENTS_DIR"
echo ""

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# ============================================================================
# CREATE LAUNCHD PLIST FILES
# ============================================================================

# 7 AM - Reel 1/3
cat > "$LAUNCH_AGENTS_DIR/com.the17project.reel1.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.the17project.reel1</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$PROJECT_DIR/src/main.py</string>
        <string>--reel-number</string>
        <string>1</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>7</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/reel1_output.log</string>

    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/reel1_error.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

# 2 PM - Reel 2/3
cat > "$LAUNCH_AGENTS_DIR/com.the17project.reel2.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.the17project.reel2</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$PROJECT_DIR/src/main.py</string>
        <string>--reel-number</string>
        <string>2</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>14</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/reel2_output.log</string>

    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/reel2_error.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

# 7 PM - Reel 3/3
cat > "$LAUNCH_AGENTS_DIR/com.the17project.reel3.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.the17project.reel3</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$PROJECT_DIR/src/main.py</string>
        <string>--reel-number</string>
        <string>3</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>19</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/reel3_output.log</string>

    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/reel3_error.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

echo "✅ Created launchd plist files"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"
echo "✅ Created logs directory"

# ============================================================================
# LOAD LAUNCHD JOBS
# ============================================================================

echo ""
echo "Loading launchd jobs..."

# Unload existing jobs (ignore errors if they don't exist)
launchctl unload "$LAUNCH_AGENTS_DIR/com.the17project.reel1.plist" 2>/dev/null || true
launchctl unload "$LAUNCH_AGENTS_DIR/com.the17project.reel2.plist" 2>/dev/null || true
launchctl unload "$LAUNCH_AGENTS_DIR/com.the17project.reel3.plist" 2>/dev/null || true

# Load new jobs
launchctl load "$LAUNCH_AGENTS_DIR/com.the17project.reel1.plist"
launchctl load "$LAUNCH_AGENTS_DIR/com.the17project.reel2.plist"
launchctl load "$LAUNCH_AGENTS_DIR/com.the17project.reel3.plist"

echo "✅ Loaded all launchd jobs"

# ============================================================================
# VERIFY SETUP
# ============================================================================

echo ""
echo "========================================================================"
echo "✅ SCHEDULED GENERATION SETUP COMPLETE!"
echo "========================================================================"
echo ""
echo "Schedule:"
echo "  • 7:00 AM  - Reel 1/3 (Morning)"
echo "  • 2:00 PM  - Reel 2/3 (Afternoon)"
echo "  • 7:00 PM  - Reel 3/3 (Evening)"
echo ""
echo "Logs Location:"
echo "  $PROJECT_DIR/logs/"
echo ""
echo "Useful Commands:"
echo "  • Check status:  launchctl list | grep the17project"
echo "  • View logs:     tail -f logs/reel1_output.log"
echo "  • Test run:      python3 src/main.py --reel-number 1"
echo ""
echo "To disable scheduled generation:"
echo "  launchctl unload ~/Library/LaunchAgents/com.the17project.reel*.plist"
echo ""
echo "To re-enable:"
echo "  launchctl load ~/Library/LaunchAgents/com.the17project.reel*.plist"
echo ""
echo "========================================================================"
