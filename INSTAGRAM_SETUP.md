# Instagram Session-Based Authentication Setup

## Problem
Instagram blocks automated logins from GitHub Actions IPs (Error 572). Solution: Login locally once, save session file, upload to GitHub Secrets.

## Local Setup

### 1. Add to your `.env` file:
```bash
# Instagram credentials
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
INSTAGRAM_AUTO_POST=true
```

### 2. Run the login script locally (ONE TIME):
```bash
python login_instagram.py
```

This will:
- Login to Instagram using your credentials
- Save session to `src/config/instagram_session.json`
- Output the **raw JSON** for GitHub Secrets
- Display next steps

### 3. Copy the raw JSON:
The script will output the raw JSON content. Copy the **entire JSON** (it will be a multi-line JSON object).

Copy the JSON file content exactly as shown in the script output.

## GitHub Secrets Setup

Go to: GitHub repo → Settings → Secrets and variables → Actions → New repository secret

### Create these secrets:

**INSTAGRAM_USERNAME**
- Value: `your_instagram_username`

**INSTAGRAM_PASSWORD**
- Value: `your_instagram_password`

**INSTAGRAM_SESSION** ⭐ CRITICAL
- Value: Paste the **raw JSON** from the login script output
- This is the entire JSON object (multi-line format is OK)
- DO NOT modify or format it - paste exactly as-is
- Paste the complete JSON content from the script output

## How It Works

### Local Development:
1. First run: Logs in with username/password, saves session
2. Subsequent runs: Uses saved session (no login needed)

### GitHub Actions:
1. Workflow restores session from `INSTAGRAM_SESSION` secret
2. Instagram poster uses existing session (no IP-blocking login attempt)
3. Posts video successfully

## Session Refresh (When Sessions Expire)

### How to Recognize Session Expiration

GitHub Actions workflow fails with one of these errors:
- `LoginRequired` - Session expired
- `ChallengeRequired` - Instagram security check triggered
- `401 Unauthorized` - Authentication failed
- Workflow logs show: "Instagram login failed"

### Session Lifetime

- **Typical duration:** ~90 days
- **Expiration triggers:**
  - Time (sessions auto-expire after ~90 days)
  - Password change on Instagram account
  - Instagram security checks (suspicious activity detection)
  - Device verification requirements
  - IP address changes (rare, but possible)

### Step-by-Step Refresh Commands

**1. Run the login script locally:**
```bash
python login_instagram.py
```

**2. Copy the raw JSON from output:**
The script will print the raw JSON content. Copy the entire JSON object.

**3. Update GitHub Secret:**
- Go to: **GitHub repo → Settings → Secrets and variables → Actions**
- Find `INSTAGRAM_SESSION` in the list
- Click **Update**
- Paste the raw JSON
- Click **Update secret**

**4. Verify the fix:**
- Go to **Actions** tab in GitHub
- Click **Re-run failed jobs** on the latest failed workflow
- OR wait for the next scheduled run (8 AM, 2 PM, or 7 PM EST)

### Quick Reference Commands

```bash
# Refresh session locally
python login_instagram.py

# Test the new session works locally
python src/main.py --test

# Check session file exists
ls -lh src/config/instagram_session.json
```

That's it. The workflow will use the new session on next run.

## Security Notes

- Never commit `src/config/instagram_session.json` to git (already in .gitignore)
- Never commit `.env` file to git (already in .gitignore)
- Session files contain authentication cookies - treat like passwords
- Disable Instagram 2FA temporarily if login fails

## Testing

### Test locally WITHOUT posting to Instagram:
```bash
python src/main.py --test
```

### Test locally WITH Instagram posting:
```bash
python src/main.py
```

This will generate 1 video and post it to Instagram.

## Troubleshooting

**Error: Two-factor authentication required**
- Temporarily disable 2FA on Instagram account
- Or handle verification code manually (not automated)

**Error: Instagram challenge required**
- Login manually through Instagram app first
- Wait 24 hours, try again

**Error: Login failed**
- Check credentials in `.env`
- Verify Instagram account is active

**GitHub Actions: Session not found**
- Ensure `INSTAGRAM_SESSION` secret exists
- Verify JSON is valid (use `python -m json.tool src/config/instagram_session.json`)
