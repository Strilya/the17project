# The17Project - Automated Instagram Content Generation

> 🔮 Automated Instagram content generation system for The17Project spiritual productivity brand

This project automates the daily creation of Instagram content about angel numbers, manifestation, and spiritual productivity. It uses Anthropic's Claude 3.5 Sonnet model to generate captions, hashtags, and image descriptions, then logs everything to Google Sheets and sends Slack notifications.

## ✨ Features

- **Daily Automation**: Runs every day at 8:00 AM EST via GitHub Actions
- **AI-Powered Content**: Uses Anthropic Claude 3.5 Sonnet to generate engaging Instagram posts
- **Google Sheets Logging**: Automatically saves all content to a tracking spreadsheet
- **Slack Notifications**: Sends rich notifications with content previews
- **No External Hosting**: Runs entirely on GitHub Actions (free tier)
- **Brand-Aligned**: Generates content following The17Project brand voice and style

## 📁 Project Structure

```
the17project-automation/
├── .github/
│   └── workflows/
│       └── daily-content.yml        # GitHub Actions scheduler
├── src/
│   ├── __init__.py                  # Package initialization
│   ├── main.py                      # Main workflow orchestrator
│   ├── generate_content.py          # Claude AI content generation
│   ├── save_to_sheets.py            # Google Sheets integration
│   └── send_slack_notification.py   # Slack notifications
├── config/
│   ├── prompts.json                 # Content generation prompts
│   └── .env.example                 # Environment variables template
├── tests/
│   └── test_content_generation.py   # Unit tests
├── .gitignore                       # Git ignore rules
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package setup
└── README.md                        # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+** installed locally (for testing)
2. **GitHub account** (for GitHub Actions)
3. **Anthropic API key** ([Get one here](https://console.anthropic.com/settings/keys))
4. **Google Cloud account** (for Google Sheets API)
5. **Slack workspace** (for notifications)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/the17project-automation.git
cd the17project-automation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

```bash
# Copy the example environment file
cp config/.env.example config/.env

# Edit config/.env and add your credentials
```

Required environment variables:

```env
# Anthropic Claude AI API Configuration
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx

# Google Sheets Configuration
SHEET_ID=your_google_sheet_id_here
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account",...}

# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=C01234567890
```

### Step 3: Setup Google Sheets API

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Google Sheets API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it

3. **Create Service Account**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Give it a name (e.g., "the17project-automation")
   - Click "Create and Continue"
   - Skip optional steps and click "Done"

4. **Generate Service Account Key**
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Save the downloaded file

5. **Create Google Sheet**
   - Create a new Google Sheet named "The17Project_Content_Log"
   - Copy the Sheet ID from the URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
   - Share the sheet with the service account email (found in the JSON file)
   - Give it "Editor" permissions

### Step 4: Setup Slack Bot

1. **Create Slack App**
   - Go to [Slack API](https://api.slack.com/apps)
   - Click "Create New App" > "From scratch"
   - Name it "The17Project Bot" and select your workspace

2. **Configure Bot Permissions**
   - Go to "OAuth & Permissions"
   - Under "Scopes" > "Bot Token Scopes", add:
     - `chat:write`
     - `chat:write.public`
     - `channels:read`

3. **Install App to Workspace**
   - Click "Install to Workspace"
   - Copy the "Bot User OAuth Token" (starts with `xoxb-`)

4. **Get Channel ID**
   - Open Slack, right-click on your channel
   - Click "View channel details"
   - Scroll down to copy the Channel ID

### Step 5: Configure GitHub Secrets

1. **Go to Your GitHub Repository**
   - Navigate to Settings > Secrets and variables > Actions

2. **Add Repository Secrets**
   - Click "New repository secret" for each:
     - `ANTHROPIC_API_KEY`: Your Anthropic Claude API key
     - `GOOGLE_SHEETS_CREDENTIALS`: Entire content of service account JSON file
     - `SHEET_ID`: Google Sheet ID from URL
     - `SLACK_BOT_TOKEN`: Your Slack bot token
     - `SLACK_CHANNEL_ID`: Your Slack channel ID

## 🧪 Testing Locally

Before deploying to GitHub Actions, test the system locally:

```bash
# Test content generation only
python src/generate_content.py

# Test Google Sheets integration
python src/save_to_sheets.py

# Test Slack notifications
python src/send_slack_notification.py

# Test complete workflow
python src/main.py
```

## 🤖 GitHub Actions Workflow

The automation runs daily at 8:00 AM EST via GitHub Actions.

### Manual Trigger

You can manually trigger the workflow:

1. Go to "Actions" tab in your GitHub repository
2. Select "Daily Instagram Content Generation"
3. Click "Run workflow"
4. Click the green "Run workflow" button

### Schedule

The workflow is scheduled in [.github/workflows/daily-content.yml](.github/workflows/daily-content.yml):

```yaml
schedule:
  - cron: '0 13 * * *'  # 8:00 AM EST (1:00 PM UTC)
```

**Note**: GitHub Actions uses UTC time. Adjust the cron schedule based on your timezone:
- EST (winter): UTC-5 → 8 AM EST = 1 PM UTC → `0 13 * * *`
- EDT (summer): UTC-4 → 8 AM EDT = 12 PM UTC → `0 12 * * *`

### Viewing Logs

1. Go to "Actions" tab
2. Click on the latest workflow run
3. Click on "Generate and Post Instagram Content"
4. Expand steps to view detailed logs
5. Download log artifacts if needed

## 📊 Content Format

The system generates three components for each Instagram post:

### 1. Caption (150-200 words)
- Engaging hook about angel numbers or spiritual productivity
- Personal story or relatable scenario
- Actionable tips or insights
- Call-to-action
- Emoji usage for visual appeal

### 2. Hashtags (20 tags)
- 5 broad hashtags (100k+ posts)
- 10 medium hashtags (10k-100k posts)
- 5 niche hashtags (1k-10k posts)
- Brand-specific tags (#the17project, #angelnumber17)

### 3. Image Description
- Detailed Canva design instructions
- Brand colors: Purple (#6B46C1), Gold (#FFD700)
- Text placement and layout
- Visual elements and style

## 🎨 Customizing Content

### Modify Prompts

Edit [config/prompts.json](config/prompts.json) to customize:

- Content themes and topics
- Brand voice and tone
- Hashtag categories
- Design guidelines

### Adjust Scheduling

Edit [.github/workflows/daily-content.yml](.github/workflows/daily-content.yml):

```yaml
schedule:
  - cron: '0 13 * * *'  # Change to your preferred time (UTC)
```

### Change Content Settings

Set environment variables:

```env
CONTENT_TEMPERATURE=0.8      # Claude AI temperature (0.0-1.0)
CONTENT_MAX_TOKENS=1000      # Max tokens for generation
```

## 📈 Google Sheets Structure

The automated spreadsheet contains these columns:

| Column | Description |
|--------|-------------|
| Timestamp | ISO format timestamp of generation |
| Date | Formatted date (YYYY-MM-DD) |
| Caption | Full Instagram caption |
| Hashtags | All hashtags (space-separated) |
| Image Description | Canva design instructions |
| Model | AI model used (claude-3-5-sonnet-20241022) |
| Tokens Used | API tokens consumed |
| Status | Content status (Generated/Posted/Archived) |
| Posted Date | Date when posted to Instagram |
| Notes | Additional notes or modifications |

## 🔔 Slack Notifications

Each successful generation sends a rich notification with:

- ✨ Header announcing new content
- 📅 Generation timestamp
- 📝 Caption preview (first 150 characters)
- #️⃣ Hashtag count
- 🎨 Image description snippet
- 📊 Link to Google Sheets
- 🤖 Model and token usage stats

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_content_generation.py::TestContentGenerator -v
```

### Code Quality

```bash
# Format code with Black
black src/ tests/

# Lint with Flake8
flake8 src/ tests/

# Type checking with MyPy
mypy src/
```

### Project Structure Explained

#### [src/generate_content.py](src/generate_content.py)
- Loads prompt configuration from `config/prompts.json`
- Calls Claude AI API with combined prompts
- Validates response structure
- Returns structured content dictionary

#### [src/save_to_sheets.py](src/save_to_sheets.py)
- Authenticates with Google Sheets API using service account
- Opens spreadsheet by ID
- Creates headers if needed
- Appends content as new rows

#### [src/send_slack_notification.py](src/send_slack_notification.py)
- Authenticates with Slack API
- Formats content into rich message blocks
- Sends notifications to specified channel
- Handles error notifications

#### [src/main.py](src/main.py)
- Orchestrates the complete workflow
- Coordinates all three modules
- Handles errors and logging
- Entry point for GitHub Actions

## 🔒 Security Best Practices

1. **Never commit sensitive data**
   - All credentials are in `.gitignore`
   - Use GitHub Secrets for CI/CD

2. **Rotate API keys regularly**
   - Anthropic API keys
   - Slack bot tokens
   - Service account keys

3. **Limit permissions**
   - Google service account has only Sheets access
   - Slack bot has minimal required scopes

4. **Review generated content**
   - Always review before posting
   - Content is saved to Sheets for approval

## 🐛 Troubleshooting

### Common Issues

**Claude AI API Error: "Invalid API Key"**
- Verify `ANTHROPIC_API_KEY` is correct
- Check if key has required permissions
- Ensure billing is set up on Anthropic account

**Google Sheets Error: "Spreadsheet not found"**
- Verify `SHEET_ID` is correct
- Check service account email has access to sheet
- Ensure Google Sheets API is enabled

**Slack Error: "Channel not found"**
- Verify `SLACK_CHANNEL_ID` is correct
- Ensure bot is added to the channel
- Check bot has `chat:write` permission

**GitHub Actions: "Workflow not running"**
- Check cron syntax is valid
- Ensure workflow file is in `.github/workflows/`
- Verify GitHub Actions is enabled in repository settings

### Debug Mode

Enable verbose logging:

```python
# In any module, change logging level
logging.basicConfig(level=logging.DEBUG)
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Email: your-email@example.com

## 🙏 Acknowledgments

- Anthropic for Claude 3.5 Sonnet API
- Google for Sheets API
- Slack for Bot API
- GitHub for Actions platform

---

**Made with 💜 for The17Project**

*Manifesting productive spirituality, one post at a time.* ✨
