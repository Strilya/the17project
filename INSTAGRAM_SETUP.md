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
- Save session to `config/instagram_session.json`
- Output a **base64-encoded** string for GitHub Secrets
- Display next steps

### 3. Copy the base64 string:
The script will output a base64-encoded string. Copy the **entire string** (it will be a long single line of random characters).

**DO NOT** copy the JSON file content directly - use the base64 string from the script output.

## GitHub Secrets Setup

Go to: GitHub repo → Settings → Secrets and variables → Actions → New repository secret

### Create these secrets:

**INSTAGRAM_USERNAME**
- Value: `your_instagram_username`

**INSTAGRAM_PASSWORD**
- Value: `your_instagram_password`

**INSTAGRAM_SESSION** ⭐ CRITICAL
- Value: Paste the **base64-encoded string** from the login script output
- This is a long single-line string (base64 encoded JSON)
- DO NOT modify or format it - paste exactly as-is
- DO NOT paste the JSON file content directly - use the base64 string

## How It Works

### Local Development:
1. First run: Logs in with username/password, saves session
2. Subsequent runs: Uses saved session (no login needed)

### GitHub Actions:
1. Workflow restores session from `INSTAGRAM_SESSION` secret
2. Instagram poster uses existing session (no IP-blocking login attempt)
3. Posts video successfully

## Session Maintenance

Instagram sessions expire eventually. If posting fails in GitHub Actions:

1. Run locally: `python login_instagram.py`
2. Copy the new **base64 string** from the script output
3. Update GitHub Secret `INSTAGRAM_SESSION` with the new base64 string

## Security Notes

- Never commit `config/instagram_session.json` to git (already in .gitignore)
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
- Verify JSON is valid (use `python -m json.tool config/instagram_session.json`)
