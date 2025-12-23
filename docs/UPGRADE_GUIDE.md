# The17Project Content Upgrade Implementation Guide

## Quick Start

### 1. Initial Setup (5 minutes)
```bash
cd /Users/ilyastr/Desktop/the17Project

# Verify backup and feature branch exist
git tag | grep v1.0-stable  # Should show v1.0-stable
git branch | grep feature/improved-content-hooks  # Should show feature branch

# Switch to feature branch if not already on it
git checkout feature/improved-content-hooks
```

### 2. Generate Test Content (2 minutes each)
```bash
# Test V1 (original)
python3 src/main.py

# Test V2 (improved)
USE_V2_CONTENT=true python3 src/main_v2.py
```

### 3. A/B Test Both Versions (10 minutes)
```bash
# Run automated A/B test
cd /Users/ilyastr/Desktop/the17Project
./scripts/test_ab.sh
```

### 4. Post to Instagram & Track

Both videos will appear in Slack. Post both to Instagram and track:
- Views
- Likes
- Comments
- Followers gained

Add this data to your Google Sheet with columns:
- `content_version` (v1 or v2)
- `hook_style` (controversial, urgent, curiosity, personal, specific)
- `views`, `likes`, `comments`, `followers_gained`

### 5. Analyze Results (After 7 days)
```bash
cd /Users/ilyastr/Desktop/the17Project
python3 scripts/compare_performance.py
```

### 6. Rollout or Rollback

**If V2 is better:**
```bash
cd /Users/ilyastr/Desktop/the17Project
git checkout master
git merge feature/improved-content-hooks

# Update .env or set environment variable
echo "USE_V2_CONTENT=true" >> .env

git add .env
git commit -m "Switch to V2 content as default"
git push origin master
```

**If V2 isn't better:**
```bash
cd /Users/ilyastr/Desktop/the17Project
./scripts/rollback.sh
# Stick with original or revise approach
```

## Emergency Rollback

If anything breaks:
```bash
cd /Users/ilyastr/Desktop/the17Project
git checkout master
git reset --hard v1.0-stable
python3 src/main.py  # Should work exactly as before
```

## What Changed

### Improved in V2:
- **Hooks:** Controversial instead of generic
  - V1: "Seeing 1111?"
  - V2: "Seeing 1111 but nothing manifests? You're doing it wrong."

- **Scenarios:** Specific instead of vague
  - V1: "1111 means new beginnings"
  - V2: "Seeing 1111 at 3am? Your guides need you awake NOW"

- **CTAs:** Strong follow prompts
  - V1: "Follow for more"
  - V2: "Follow @the17project for daily angel number truth bombs"

- **Actions:** Concrete steps
  - V1: "Align your energy"
  - V2: "1. Write ONE desire. 2. Delete ONE distraction. 3. Take ONE action in 24hrs"

### Success Metrics

Current baseline (V1):
- 8 followers / 50 videos = 0.16% conversion
- Low engagement and return rate

Target (V2):
- 50%+ improvement = 0.24%+ conversion
- Would give 12+ followers from same 50 videos

## File Structure
```
the17Project/
├── config/
│   ├── prompts.json          # Original prompts (V1)
│   └── prompts_v2.json       # Improved prompts (V2) ← NEW
├── src/
│   ├── main.py               # Original main (V1)
│   ├── main_v2.py            # A/B testing main ← NEW
│   ├── generate_content.py  # Original generator (V1)
│   └── generate_content_v2.py # Improved generator (V2) ← NEW
├── scripts/
│   ├── test_ab.sh            # A/B testing script ← NEW
│   ├── rollback.sh           # Emergency rollback ← NEW
│   └── compare_performance.py # Results analysis ← NEW
└── docs/
    └── UPGRADE_GUIDE.md      # This file ← NEW
```

## Safety Features

✅ Original code untouched (main.py, generate_content.py, prompts.json)
✅ V2 files are additions, not replacements
✅ Environment variable controls which version runs
✅ Git tag v1.0-stable = instant rollback point
✅ One command rollback: `./scripts/rollback.sh`
✅ Can switch back anytime with zero risk

## Troubleshooting

### V2 Generation Fails
```bash
# Check prompts file exists
ls -la /Users/ilyastr/Desktop/the17Project/config/prompts_v2.json

# Test V2 import
cd /Users/ilyastr/Desktop/the17Project
python -c "from src.generate_content_v2 import ContentGeneratorV2; print('✅ V2 available')"

# Fall back to V1
export USE_V2_CONTENT=false
python src/main_v2.py
```

### Video Generation Fails
```bash
# Check video_scenes structure
cd /Users/ilyastr/Desktop/the17Project
python -c "
from src.generate_content_v2 import ContentGeneratorV2
gen = ContentGeneratorV2()
content = gen.generate_content({'value': '1111', 'type': 'angel_numbers'})
print('Scenes:', list(content['video_scenes'].keys()))
"
# Should output: ['hook', 'meaning', 'action', 'cta']
```

### Slack Upload Fails
```bash
# V2 uses same Slack integration as V1
# If failing, check Slack credentials
cd /Users/ilyastr/Desktop/the17Project
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Bot token:', 'SET' if os.getenv('SLACK_BOT_TOKEN') else 'MISSING')
print('Channel ID:', 'SET' if os.getenv('SLACK_CHANNEL_ID') else 'MISSING')
"
```

### Import Errors
```bash
# Make sure you're in the project directory
cd /Users/ilyastr/Desktop/the17Project

# Check Python can find modules
python -c "import sys; print('\\n'.join(sys.path))"

# Run with explicit path
PYTHONPATH=/Users/ilyastr/Desktop/the17Project/src python src/main_v2.py
```

## Testing Checklist

After implementation, verify:

**Git Safety:**
- [ ] v1.0-stable tag exists: `git tag | grep v1.0-stable`
- [ ] On feature/improved-content-hooks branch: `git branch --show-current`
- [ ] Original files unchanged: `git diff v1.0-stable -- src/main.py src/generate_content.py config/prompts.json`

**Files Created:**
- [ ] config/prompts_v2.json exists
- [ ] src/generate_content_v2.py exists
- [ ] src/main_v2.py exists
- [ ] scripts/test_ab.sh exists and is executable
- [ ] scripts/rollback.sh exists and is executable
- [ ] scripts/compare_performance.py exists

**Functionality:**
- [ ] V1 still works: `python src/main.py`
- [ ] V2 imports: `python -c "from src.generate_content_v2 import ContentGeneratorV2"`
- [ ] V2 generates: `USE_V2_CONTENT=true python src/main_v2.py`

**Content Quality (manual review):**
- [ ] V2 hooks are more controversial/specific than V1
- [ ] V2 scenarios are concrete (not generic)
- [ ] V2 CTAs include engagement hooks
- [ ] V2 actions are numbered and concrete

## Usage Examples

### Generate with V1 (Original):
```bash
cd /Users/ilyastr/Desktop/the17Project
python3 src/main.py
```

### Generate with V2 (Improved):
```bash
cd /Users/ilyastr/Desktop/the17Project
USE_V2_CONTENT=true python3 src/main_v2.py
```

### Test specific hook style:
```python
from src.generate_content_v2 import ContentGeneratorV2

gen = ContentGeneratorV2()

# Force specific hook style for testing
content = gen.generate_content(
    topic={'value': '1111', 'type': 'angel_numbers'},
    force_hook_style='controversial'  # or 'urgent', 'curiosity', 'personal', 'specific'
)

print(content['video_scenes']['hook'])
print(f"Hook style used: {content['hook_style_used']}")
```

### Compare outputs side by side:
```bash
cd /Users/ilyastr/Desktop/the17Project

echo "=== V1 Output ==="
USE_V2_CONTENT=false python3 src/main_v2.py | grep -A 4 "HOOK:"

sleep 5

echo "=== V2 Output ==="
USE_V2_CONTENT=true python3 src/main_v2.py | grep -A 4 "HOOK:"
```

## Next Steps

1. **Complete Implementation** (Done!)
   - All files created
   - Git safety in place
   - Scripts ready to use

2. **Generate Test Videos** (1-2 weeks)
   - Generate 7 videos with V1: `python3 src/main.py`
   - Generate 7 videos with V2: `USE_V2_CONTENT=true python3 src/main_v2.py`
   - OR use automated test: `./scripts/test_ab.sh`

3. **Track Performance** (Ongoing)
   - Post all videos to Instagram
   - Add performance data to Google Sheets
   - Required columns: content_version, hook_style, views, likes, comments, followers_gained

4. **Analyze Results** (After 7 days)
   - Run: `python3 scripts/compare_performance.py`
   - Review metrics comparison
   - Check hook style performance

5. **Make Decision**
   - If V2 > 50% better: Merge to master, make default
   - If V2 20-50% better: Continue testing 1 more week
   - If V2 < 20% better: Analyze best hook styles, revise
   - If V2 worse: Rollback, stick with V1

## Support

**Logs:** Check `content_generation.log` for detailed execution info

**Rollback:** `./scripts/rollback.sh` or `git reset --hard v1.0-stable`

**Questions:** Review this guide or check the original prompt specification

## Success Criteria

V2 is successful if it achieves:
- **50%+ improvement in follower conversion rate**
  - Current: 0.16% → Target: 0.24%+
  - Would mean 12+ followers instead of 8 from same 50 videos

Track these metrics:
- Views per video
- Engagement rate (likes + comments / views)
- Follower conversion (new followers / views)
- Return rate (follower views / total views)

The data will tell you which version wins. Trust the metrics!
