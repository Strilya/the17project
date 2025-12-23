# The17Project V2 - Setup and Run Commands

## 🔧 First Time Setup (Run Once)

### Step 1: Install Python Dependencies
```bash
cd /Users/ilyastr/Desktop/the17Project
pip3 install -r requirements.txt
```

**Note:** This will install:
- `anthropic` - Claude AI API
- `pydub` - Audio processing for videos
- `moviepy` - Video generation
- `Pillow` - Image processing
- `gspread` - Google Sheets integration
- `slack-sdk` - Slack notifications
- And other dependencies...

### Step 2: Verify Installation
```bash
cd /Users/ilyastr/Desktop/the17Project
python3 -c "import pydub; import anthropic; import moviepy; print('✅ All dependencies installed')"
```

---

## 🚀 Daily Usage Commands

### Generate V1 Content (Original)
```bash
cd /Users/ilyastr/Desktop/the17Project
python3 src/main.py
```

### Generate V2 Content (Improved - Controversial Hooks)
```bash
cd /Users/ilyastr/Desktop/the17Project
USE_V2_CONTENT=true python3 src/main_v2.py
```

### Run A/B Test (Generate Both V1 and V2)
```bash
cd /Users/ilyastr/Desktop/the17Project
./scripts/test_ab.sh
```

---

## 📊 After Testing (7+ days later)

### Analyze Performance Results
```bash
cd /Users/ilyastr/Desktop/the17Project
python3 scripts/compare_performance.py
```

---

## 🚨 Emergency Rollback

### If V2 Breaks Something
```bash
cd /Users/ilyastr/Desktop/the17Project
./scripts/rollback.sh
```

---

## 🧪 Test Specific Hook Styles

### Test All 5 Hook Styles (Python Interactive)
```bash
cd /Users/ilyastr/Desktop/the17Project/src
python3
```

Then in Python:
```python
from generate_content_v2 import ContentGeneratorV2

gen = ContentGeneratorV2()

# Test each hook style
styles = ['controversial', 'urgent', 'curiosity', 'personal', 'specific']

for style in styles:
    print(f"\n=== Testing {style.upper()} ===")
    content = gen.generate_content(
        topic={'value': '1111', 'type': 'angel_numbers'},
        force_hook_style=style
    )
    print(f"Hook: {content['video_scenes']['hook']}")
    print(f"CTA: {content['video_scenes']['cta']}")
```

---

## 📝 Quick Reference

| Task | Command |
|------|---------|
| Install dependencies | `pip3 install -r requirements.txt` |
| Generate V1 | `python3 src/main.py` |
| Generate V2 | `USE_V2_CONTENT=true python3 src/main_v2.py` |
| A/B Test | `./scripts/test_ab.sh` |
| Analyze Results | `python3 scripts/compare_performance.py` |
| Rollback | `./scripts/rollback.sh` |

---

## ✅ Success Checklist

Before running for the first time:
- [ ] Dependencies installed: `pip3 install -r requirements.txt`
- [ ] `.env` file configured with API keys (ANTHROPIC_API_KEY, etc.)
- [ ] `credentials.json` file exists for Google Sheets
- [ ] On feature branch: `git checkout feature/improved-content-hooks`

After setup:
- [ ] V1 generates successfully: `python3 src/main.py`
- [ ] V2 generates successfully: `USE_V2_CONTENT=true python3 src/main_v2.py`
- [ ] A/B test script runs: `./scripts/test_ab.sh`

---

## 🎯 What Each Command Does

### `python3 src/main.py`
- Uses **original** content generator (V1)
- Generic hooks: "Seeing 1111?"
- Standard CTAs: "Follow for more"
- Baseline for comparison

### `USE_V2_CONTENT=true python3 src/main_v2.py`
- Uses **improved** content generator (V2)
- Controversial hooks: "Seeing 1111 but nothing manifests? You're doing it wrong"
- Strong CTAs: "Follow @the17project for daily angel number truth. Drop your number below."
- 5 hook styles: controversial, urgent, curiosity, personal, specific

### `./scripts/test_ab.sh`
- Generates 1 video with V1
- Waits 5 seconds
- Generates 1 video with V2
- Both appear in Slack for manual posting to Instagram

### `python3 scripts/compare_performance.py`
- Reads performance data from Google Sheets
- Compares V1 vs V2 metrics
- Shows which hook styles perform best
- Provides decision recommendation

---

## 🎬 Getting Started (Copy-Paste These)

```bash
# 1. Install dependencies (first time only)
cd /Users/ilyastr/Desktop/the17Project
pip3 install -r requirements.txt

# 2. Test that it works
python3 src/main.py

# 3. Test V2 improved version
USE_V2_CONTENT=true python3 src/main_v2.py

# 4. Run full A/B test
./scripts/test_ab.sh
```

That's it! Both videos will appear in Slack. Post them to Instagram and track the results.
