# Scheduled Reel Generation

The17Project can automatically generate reels at scheduled times throughout the day using macOS's built-in `launchd` system.

## Schedule

- **7:00 AM** - Reel 1/3 (Morning)
- **2:00 PM** - Reel 2/3 (Afternoon)
- **7:00 PM** - Reel 3/3 (Evening)

## Quick Start

### 1. Initial Setup (One-Time)

Run the setup script to create and load the scheduled jobs:

```bash
./setup_scheduled_generation.sh
```

This will:
- Create 3 launchd plist files (one for each scheduled time)
- Load them into the system
- Create a `logs/` directory for output
- Start the scheduled generation

### 2. Manage Scheduled Generation

Use the management script to control the scheduler:

```bash
# Check if scheduled generation is active
./manage_schedule.sh status

# Stop scheduled generation
./manage_schedule.sh stop

# Start scheduled generation
./manage_schedule.sh start

# View logs for a specific reel
./manage_schedule.sh logs 1

# Test generate a reel manually
./manage_schedule.sh test 2
```

## How It Works

### Content Planning

The system automatically determines what to generate based on the day of week:

- **Monday/Wednesday/Friday** → Life Path content
- **Tuesday/Thursday/Saturday** → Angel Number content
- **Sunday** → Wildcard (random)

Each day, 3 reels are generated at the scheduled times. All 3 reels for that day follow the same content plan.

### Manual Generation

You can still generate reels manually without affecting the schedule:

```bash
# Generate all 3 reels at once
python3 src/main.py

# Generate only a specific reel
python3 src/main.py --reel-number 1
python3 src/main.py --reel-number 2
python3 src/main.py --reel-number 3
```

## Logs

Logs are stored in the `logs/` directory:

- `reel1_output.log` - Output from 7 AM generation
- `reel1_error.log` - Errors from 7 AM generation
- `reel2_output.log` - Output from 2 PM generation
- `reel2_error.log` - Errors from 2 PM generation
- `reel3_output.log` - Output from 7 PM generation
- `reel3_error.log` - Errors from 7 PM generation

View logs in real-time:

```bash
tail -f logs/reel1_output.log
```

## Troubleshooting

### Check if jobs are loaded

```bash
launchctl list | grep the17project
```

You should see:
```
com.the17project.reel1
com.the17project.reel2
com.the17project.reel3
```

### Manually trigger a job (for testing)

```bash
launchctl start com.the17project.reel1
```

### View recent errors

```bash
cat logs/reel1_error.log
```

### Completely remove scheduled generation

```bash
./manage_schedule.sh stop
rm ~/Library/LaunchAgents/com.the17project.reel*.plist
```

## Technical Details

### File Locations

- **Plist files**: `~/Library/LaunchAgents/com.the17project.reel[1-3].plist`
- **Logs**: `./logs/`
- **Output videos**: `./output/`

### Environment Variables

The scheduled jobs will load your `.env` file automatically since they run from the project directory. Make sure your `.env` contains:

- `ANTHROPIC_API_KEY`
- `ELEVENLABS_API_KEY`
- `GOOGLE_SHEETS_CREDS`
- `GOOGLE_SHEET_ID`
- `SLACK_BOT_TOKEN`
- `SLACK_CHANNEL_ID`

### System Requirements

- macOS (uses launchd)
- Python 3
- All dependencies installed (`pip install -r requirements.txt`)

## Advanced Usage

### Modify Schedule Times

Edit the plist files directly:

```bash
nano ~/Library/LaunchAgents/com.the17project.reel1.plist
```

Change the `Hour` and `Minute` values:

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>7</integer>  <!-- Change this -->
    <key>Minute</key>
    <integer>0</integer>  <!-- Change this -->
</dict>
```

Then reload:

```bash
launchctl unload ~/Library/LaunchAgents/com.the17project.reel1.plist
launchctl load ~/Library/LaunchAgents/com.the17project.reel1.plist
```

### Force a Specific Day Type

You can force the system to generate specific content types for testing. Edit `src/main.py`:

```python
FORCE_DAY_TYPE = 'life_path'  # Options: 'life_path', 'angel_number', 'wildcard', or None
```

Set back to `None` for normal operation.

## Notes

- The scheduled jobs will run even when you're not logged in (as long as the Mac is awake)
- Each reel takes approximately 2-5 minutes to generate
- Videos, captions, and notifications are sent automatically to Google Sheets and Slack
- The system tracks which angel numbers have been used to avoid repeats
