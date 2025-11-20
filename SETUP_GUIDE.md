# Quick Setup Guide for The17Project Automation

This guide will help you set up the Instagram content automation system step-by-step.

## 🚀 5-Minute Setup Checklist

### ✅ Step 1: Anthropic Claude API Key (2 minutes)

1. Go to https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Name it "The17Project Automation"
4. Copy the key (starts with `sk-ant-`)
5. Save it securely

**Cost estimate**: ~$0.02-0.03 per day (Claude 3.5 Sonnet is very efficient)

---

### ✅ Step 2: Google Sheets Setup (3 minutes)

#### A. Create Service Account

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create/Select Project**
   - Click project dropdown at top
   - Click "New Project"
   - Name: "The17Project Automation"
   - Click "Create"

3. **Enable Google Sheets API**
   - Search for "Google Sheets API" in search bar
   - Click "Enable"

4. **Create Service Account**
   - Go to: "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Name: `the17project-bot`
   - Click "Create and Continue"
   - Click "Done" (skip optional steps)

5. **Download JSON Key**
   - Click on the created service account email
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose "JSON"
   - **SAVE THIS FILE** - you'll need it!

#### B. Create Google Sheet

1. Create a new Google Sheet: https://sheets.google.com
2. Name it: **"The17Project_Content_Log"**
3. Copy the Sheet ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/[THIS_IS_YOUR_SHEET_ID]/edit
   ```
4. **Share the sheet** with the service account email (found in the JSON file)
   - Example: `the17project-bot@your-project.iam.gserviceaccount.com`
   - Give "Editor" access

---

### ✅ Step 3: Slack Bot Setup (2 minutes)

1. **Create Slack App**
   - Go to https://api.slack.com/apps
   - Click "Create New App" → "From scratch"
   - App Name: `The17Project Bot`
   - Select your workspace

2. **Add Permissions**
   - Go to "OAuth & Permissions"
   - Scroll to "Scopes" → "Bot Token Scopes"
   - Add these scopes:
     - `chat:write`
     - `chat:write.public`
     - `channels:read`

3. **Install to Workspace**
   - Click "Install to Workspace" at top
   - Click "Allow"
   - **Copy the Bot Token** (starts with `xoxb-`)

4. **Get Channel ID**
   - Open Slack desktop/web
   - Right-click your channel (e.g., `#content-automation`)
   - Click "View channel details"
   - Scroll down and copy the Channel ID (starts with `C`)

---

### ✅ Step 4: Configure GitHub Secrets (3 minutes)

1. **Push your code to GitHub** (if not already)
   ```bash
   git init
   git add .
   git commit -m "Initial commit: The17Project automation"
   git branch -M main
   git remote add origin https://github.com/yourusername/the17project-automation.git
   git push -u origin main
   ```

2. **Go to Repository Settings**
   - Navigate to: `Settings` → `Secrets and variables` → `Actions`

3. **Add these secrets** (click "New repository secret" for each):

   | Secret Name | Value | Where to find it |
   |-------------|-------|------------------|
   | `ANTHROPIC_API_KEY` | `sk-ant-xxxxx` | From Step 1 |
   | `SHEET_ID` | `1a2b3c4d5e...` | From Google Sheets URL |
   | `GOOGLE_SHEETS_CREDENTIALS` | `{"type":"service_account"...}` | Entire contents of downloaded JSON file |
   | `SLACK_BOT_TOKEN` | `xoxb-xxxxx` | From Slack app settings |
   | `SLACK_CHANNEL_ID` | `C01234567` | From Slack channel details |

   **Important for `GOOGLE_SHEETS_CREDENTIALS`**:
   - Open the downloaded JSON file in a text editor
   - Copy the ENTIRE contents (all the JSON)
   - Paste it as the secret value

---

### ✅ Step 5: Test the System (2 minutes)

#### Local Test (Optional but Recommended)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create config/.env file
cp config/.env.example config/.env

# Edit config/.env and add your credentials
# (Same values as GitHub Secrets)

# Test the workflow
python src/main.py
```

#### GitHub Actions Test

1. Go to your repository
2. Click "Actions" tab
3. Click "Daily Instagram Content Generation"
4. Click "Run workflow" dropdown
5. Click green "Run workflow" button
6. Wait ~30 seconds
7. Click on the running workflow to see logs

---

## 🎉 You're Done!

The system will now:
- ✅ Run automatically every day at 8:00 AM EST
- ✅ Generate Instagram content using AI
- ✅ Save to Google Sheets
- ✅ Send Slack notifications

---

## 🔧 Customization

### Change the Schedule

Edit `.github/workflows/daily-content.yml`:

```yaml
schedule:
  - cron: '0 13 * * *'  # Change this (UTC time)
```

**Time Conversion Examples**:
- 8 AM EST = `0 13 * * *` (winter) or `0 12 * * *` (summer)
- 9 AM EST = `0 14 * * *` (winter) or `0 13 * * *` (summer)
- 10 AM EST = `0 15 * * *` (winter) or `0 14 * * *` (summer)

### Customize Content Themes

Edit `config/prompts.json`:
- Change angel number themes
- Adjust brand voice
- Modify hashtag categories
- Update design guidelines

---

## 🆘 Common Issues

### "Claude AI API Error"
- ✅ Check `ANTHROPIC_API_KEY` is correct
- ✅ Verify billing is set up on Anthropic account
- ✅ Ensure API key has required permissions

### "Spreadsheet not found"
- ✅ Verify `SHEET_ID` is correct
- ✅ Share sheet with service account email
- ✅ Give "Editor" permissions
- ✅ Check Google Sheets API is enabled

### "Slack: channel_not_found"
- ✅ Verify `SLACK_CHANNEL_ID` is correct
- ✅ Invite bot to the channel: `/invite @The17Project Bot`
- ✅ Check bot has `chat:write` permission

### "GitHub Actions not running"
- ✅ Ensure workflow file is in `.github/workflows/`
- ✅ Check GitHub Actions is enabled (Settings → Actions)
- ✅ Verify all secrets are added correctly
- ✅ Wait up to 10 minutes for first scheduled run

---

## 📞 Need Help?

1. Check the main [README.md](README.md) for detailed documentation
2. Review workflow logs in GitHub Actions
3. Open an issue on GitHub
4. Email: your-email@example.com

---

**Happy Automating! 🚀✨**
