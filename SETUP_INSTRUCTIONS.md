# Setup Instructions - Scheduled Generation

## What's Been Configured

The17Project now supports **scheduled reel generation** at 7 AM, 2 PM, and 7 PM daily.

### New Files Created

1. **setup_scheduled_generation.sh** - One-time setup script
2. **manage_schedule.sh** - Daily management script
3. **SCHEDULED_GENERATION.md** - Full documentation

### Code Changes

- **src/main.py** - Added `--reel-number` argument support
- **.gitignore** - Added logs/ directory

## To Activate Scheduled Generation

### Step 1: Run Setup (One-Time)

```bash
cd /Users/ilyastr/Desktop/The17Project
./setup_scheduled_generation.sh
```

This will:
- Create 3 launchd jobs (7 AM, 2 PM, 7 PM)
- Load them into macOS
- Create logs directory
- Start scheduled generation

### Step 2: Verify It's Working

```bash
./manage_schedule.sh status
```

You should see:
```
✅ Scheduled generation is ACTIVE
```

### Step 3: Wait for First Run OR Test Now

**Option A: Wait for scheduled time**
- Tomorrow at 7 AM, the first reel will auto-generate

**Option B: Test immediately**
```bash
./manage_schedule.sh test 1
```

## Daily Management

### Check Status
```bash
./manage_schedule.sh status
```

### View Logs
```bash
./manage_schedule.sh logs 1    # View Reel 1 logs (7 AM)
./manage_schedule.sh logs 2    # View Reel 2 logs (2 PM)
./manage_schedule.sh logs 3    # View Reel 3 logs (7 PM)
```

### Stop Scheduled Generation
```bash
./manage_schedule.sh stop
```

### Restart Scheduled Generation
```bash
./manage_schedule.sh start
```

## How It Works

### Daily Schedule

Every day, 3 reels are generated automatically:
- **7:00 AM** - Reel 1/3 posted
- **2:00 PM** - Reel 2/3 posted
- **7:00 PM** - Reel 3/3 posted

### Content Plan

The system determines content type based on day of week:
- **Mon/Wed/Fri** → Life Path content
- **Tue/Thu/Sat** → Angel Number content
- **Sunday** → Wildcard (random)

All 3 reels for a given day follow the same content plan (e.g., Monday = 3 Life Path reels).

### What Happens Automatically

For each scheduled run:
1. ✅ Generates content using Claude API
2. ✅ Creates voice using ElevenLabs
3. ✅ Generates video with MoviePy
4. ✅ Logs to Google Sheets
5. ✅ Sends Slack notification with caption
6. ✅ Saves video to `output/` directory

## Tomorrow (Monday, Dec 30)

If you run setup today, here's what will happen tomorrow:

- **7:00 AM** - Life Path Reel 1/3 auto-generates
- **2:00 PM** - Life Path Reel 2/3 auto-generates
- **7:00 PM** - Life Path Reel 3/3 auto-generates

You'll receive Slack notifications with Instagram captions for each.

## Manual Override

You can still generate reels manually without affecting the schedule:

```bash
# Generate all 3 reels at once
python3 src/main.py

# Generate specific reel
python3 src/main.py --reel-number 1
```

## Troubleshooting

### Check if jobs are loaded
```bash
launchctl list | grep the17project
```

### View error logs
```bash
cat logs/reel1_error.log
```

### Manually trigger a job
```bash
launchctl start com.the17project.reel1
```

## Next Steps

1. Run `./setup_scheduled_generation.sh` to activate
2. Run `./manage_schedule.sh status` to verify
3. Optional: Run `./manage_schedule.sh test 1` to test
4. Wait for tomorrow's scheduled runs OR continue working on other features

---

For full documentation, see [SCHEDULED_GENERATION.md](SCHEDULED_GENERATION.md)
