#!/bin/bash

# ============================================================================
# The17Project - Manage Scheduled Generation
# Helper script to control scheduled reel generation
# ============================================================================

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

case "$1" in
    start)
        echo "Starting scheduled reel generation..."
        launchctl load "$LAUNCH_AGENTS_DIR/com.the17project.reel1.plist"
        launchctl load "$LAUNCH_AGENTS_DIR/com.the17project.reel2.plist"
        launchctl load "$LAUNCH_AGENTS_DIR/com.the17project.reel3.plist"
        echo "✅ Scheduled generation started"
        echo ""
        echo "Schedule:"
        echo "  • 7:00 AM  - Reel 1/3"
        echo "  • 2:00 PM  - Reel 2/3"
        echo "  • 7:00 PM  - Reel 3/3"
        ;;

    stop)
        echo "Stopping scheduled reel generation..."
        launchctl unload "$LAUNCH_AGENTS_DIR/com.the17project.reel1.plist" 2>/dev/null || true
        launchctl unload "$LAUNCH_AGENTS_DIR/com.the17project.reel2.plist" 2>/dev/null || true
        launchctl unload "$LAUNCH_AGENTS_DIR/com.the17project.reel3.plist" 2>/dev/null || true
        echo "✅ Scheduled generation stopped"
        ;;

    status)
        echo "Checking scheduled generation status..."
        echo ""
        if launchctl list | grep -q "com.the17project"; then
            echo "✅ Scheduled generation is ACTIVE"
            echo ""
            launchctl list | grep "com.the17project"
            echo ""
            echo "Logs location: $PROJECT_DIR/logs/"
            echo ""
            echo "Recent log entries:"
            echo "─────────────────────────────────────────────"
            if [ -f "$PROJECT_DIR/logs/reel1_output.log" ]; then
                echo "Last Reel 1 run:"
                tail -n 5 "$PROJECT_DIR/logs/reel1_output.log" 2>/dev/null || echo "  No logs yet"
            fi
        else
            echo "⚠️  Scheduled generation is NOT ACTIVE"
            echo ""
            echo "Run './manage_schedule.sh start' to enable"
        fi
        ;;

    logs)
        if [ -z "$2" ]; then
            echo "Usage: ./manage_schedule.sh logs [1|2|3]"
            echo "Example: ./manage_schedule.sh logs 1"
            exit 1
        fi

        echo "Showing logs for Reel $2..."
        echo ""
        if [ -f "$PROJECT_DIR/logs/reel${2}_output.log" ]; then
            tail -f "$PROJECT_DIR/logs/reel${2}_output.log"
        else
            echo "⚠️  No logs found for Reel $2"
            echo "Log file: $PROJECT_DIR/logs/reel${2}_output.log"
        fi
        ;;

    test)
        if [ -z "$2" ]; then
            echo "Usage: ./manage_schedule.sh test [1|2|3]"
            echo "Example: ./manage_schedule.sh test 1"
            exit 1
        fi

        echo "Testing Reel $2 generation..."
        echo ""
        cd "$PROJECT_DIR"
        python3 src/main.py --reel-number "$2"
        ;;

    *)
        echo "The17Project - Manage Scheduled Generation"
        echo ""
        echo "Usage: ./manage_schedule.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start       Enable scheduled generation (7 AM, 2 PM, 7 PM)"
        echo "  stop        Disable scheduled generation"
        echo "  status      Check if scheduled generation is active"
        echo "  logs [1-3]  View logs for specific reel (tail -f)"
        echo "  test [1-3]  Test generate a specific reel now"
        echo ""
        echo "Examples:"
        echo "  ./manage_schedule.sh start"
        echo "  ./manage_schedule.sh status"
        echo "  ./manage_schedule.sh logs 1"
        echo "  ./manage_schedule.sh test 2"
        ;;
esac
