# GitHub Secrets Configuration

Go to: **Your Repo → Settings → Secrets and variables → Actions → New repository secret**

## Required Secrets

### 1. ANTHROPIC_API_KEY
- **Value**: Your Anthropic API key
- **Format**: `sk-ant-api03-...`
- **Used for**: Content generation with Claude

### 2. GOOGLE_CLOUD_CREDENTIALS
- **Value**: Entire JSON content of your Google Cloud service account credentials
- **Format**: JSON object starting with `{"type": "service_account",...}`
- **Used for**: Google Text-to-Speech and Google Sheets

### 3. PEXELS_API_KEY
- **Value**: Your Pexels API key
- **Used for**: Stock video footage

### 4. PIXABAY_API_KEY
- **Value**: Your Pixabay API key
- **Used for**: Stock video footage

### 5. GOOGLE_SHEET_ID
- **Value**: The ID from your Google Sheet URL
- **Format**: Long alphanumeric string from `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
- **Used for**: Logging generated reels

### 6. SLACK_BOT_TOKEN
- **Value**: Your Slack bot token
- **Format**: `xoxb-...`
- **Used for**: Slack notifications

### 7. SLACK_CHANNEL_ID
- **Value**: Your Slack channel ID
- **Format**: `C01234567890`
- **Used for**: Slack notifications

### 8. INSTAGRAM_USERNAME ⭐ NEW
- **Value**: Your Instagram username
- **Format**: Plain text username (no @ symbol)
- **Used for**: Instagram posting

### 9. INSTAGRAM_PASSWORD ⭐ NEW
- **Value**: Your Instagram password
- **Format**: Plain text password
- **Used for**: Instagram posting

### 10. INSTAGRAM_SESSION ⭐ CRITICAL
- **Value**: Entire JSON content of `config/instagram_session.json`
- **Format**: JSON object with cookies and device info
- **How to get**:
  1. Run locally: `python login_instagram.py`
  2. Copy output of: `cat config/instagram_session.json`
  3. Paste ENTIRE content as secret value
- **Used for**: Session-based auth to bypass GitHub Actions IP blocking

## Important Notes

- All secrets are encrypted by GitHub
- Never commit these values to your repository
- Instagram session expires eventually - refresh by re-running `login_instagram.py` and updating the secret
- The workflow is already configured to use these secrets
