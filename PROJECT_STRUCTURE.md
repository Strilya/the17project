# The17Project - Project Structure Overview

## 📁 Complete File Structure

```
the17project-automation/
│
├── .github/
│   └── workflows/
│       └── daily-content.yml         # GitHub Actions scheduler (runs daily at 8 AM EST)
│
├── src/                               # Main source code directory
│   ├── __init__.py                    # Package initialization
│   ├── main.py                        # Main workflow orchestrator (entry point)
│   ├── generate_content.py            # OpenAI API integration for content generation
│   ├── save_to_sheets.py              # Google Sheets API integration
│   └── send_slack_notification.py    # Slack API integration for notifications
│
├── config/                            # Configuration files
│   ├── prompts.json                   # Content generation prompts and brand guidelines
│   └── .env.example                   # Environment variables template
│
├── tests/                             # Unit tests
│   ├── __init__.py                    # Tests package initialization
│   └── test_content_generation.py    # Comprehensive test suite
│
├── .gitignore                         # Git ignore rules (Python, credentials, etc.)
├── requirements.txt                   # Python dependencies
├── setup.py                           # Package setup configuration
├── LICENSE                            # MIT License
├── README.md                          # Main documentation
├── SETUP_GUIDE.md                     # Quick setup instructions
└── PROJECT_STRUCTURE.md               # This file
```

---

## 🔍 File Descriptions

### Core Application Files

#### `.github/workflows/daily-content.yml`
**Purpose**: GitHub Actions workflow definition  
**What it does**:
- Schedules daily execution at 8:00 AM EST
- Sets up Python 3.11 environment
- Installs dependencies
- Runs the main.py script
- Uploads logs as artifacts
- Handles errors and notifications

**Key features**:
- Cron schedule: `0 13 * * *` (UTC → EST conversion)
- Manual trigger support via `workflow_dispatch`
- Automatic dependency caching
- Environment variable injection from GitHub Secrets

---

#### `src/main.py`
**Purpose**: Main workflow orchestrator  
**What it does**:
1. Initializes all three services (OpenAI, Sheets, Slack)
2. Coordinates the complete workflow:
   - Generate content → Save to sheets → Send notification
3. Handles errors and logging
4. Returns workflow status

**Key classes**:
- `ContentAutomation`: Main orchestrator class

**Entry point**: Called by GitHub Actions and can be run locally

---

#### `src/generate_content.py`
**Purpose**: OpenAI API integration  
**What it does**:
- Loads prompts from `config/prompts.json`
- Calls OpenAI API with gpt-4o-mini model
- Validates response structure (caption, hashtags, image_description)
- Adds metadata (timestamp, tokens used)

**Key classes**:
- `ContentGenerator`: Handles all OpenAI interactions

**Key methods**:
- `generate_content()`: Main method that returns structured content
- `_validate_content()`: Ensures response has required fields
- `_load_config()`: Loads prompt configuration

**API used**: OpenAI Chat Completions API (JSON mode)

---

#### `src/save_to_sheets.py`
**Purpose**: Google Sheets API integration  
**What it does**:
- Authenticates using service account credentials
- Opens spreadsheet by ID
- Creates headers if needed
- Appends content rows with 10 columns

**Key classes**:
- `SheetsManager`: Handles all Google Sheets operations

**Key methods**:
- `save_content()`: Appends new row with generated content
- `_authenticate()`: OAuth2 authentication
- `_get_worksheet()`: Gets or creates worksheet
- `get_recent_content()`: Retrieves latest entries
- `update_status()`: Updates row status (for tracking posted content)

**Spreadsheet columns**:
1. Timestamp
2. Date
3. Caption
4. Hashtags
5. Image Description
6. Model
7. Tokens Used
8. Status
9. Posted Date
10. Notes

---

#### `src/send_slack_notification.py`
**Purpose**: Slack API integration  
**What it does**:
- Authenticates with Slack Bot token
- Formats rich message blocks
- Sends notifications to specified channel
- Handles error notifications

**Key classes**:
- `SlackNotifier`: Handles all Slack interactions

**Key methods**:
- `send_content_notification()`: Sends rich formatted message
- `send_error_notification()`: Sends error alerts
- `send_simple_message()`: Sends plain text messages
- `_verify_connection()`: Tests API connection

**Message includes**:
- Header with emoji
- Timestamp and metadata
- Caption preview (first 150 chars)
- Hashtag count
- Image description snippet
- Button link to Google Sheets
- Token usage stats

---

### Configuration Files

#### `config/prompts.json`
**Purpose**: Content generation configuration  
**Contains**:
- `system_prompt`: AI system instructions
- `content_generation_prompt`: Main prompt template
- `hashtag_categories`: Broad, medium, niche tags
- `brand_voice`: Tone and style guidelines
- `design_guidelines`: Brand colors and layout types

**Angel number themes**:
- 111: New beginnings, manifestation
- 222: Balance, trust, alignment
- 333: Divine support, creativity
- 444: Foundation, stability
- 555: Change, transformation
- 777: Spiritual awakening
- 1111: Portal, consciousness

**Brand colors**:
- Primary: Purple (#6B46C1)
- Accent: Gold (#FFD700)

---

#### `config/.env.example`
**Purpose**: Environment variables template  
**Variables**:
- `OPENAI_API_KEY`: OpenAI API key
- `SHEET_ID`: Google Sheet ID from URL
- `GOOGLE_SHEETS_CREDENTIALS`: Service account JSON
- `SLACK_BOT_TOKEN`: Slack bot OAuth token
- `SLACK_CHANNEL_ID`: Target Slack channel
- `TIMEZONE`: Default America/New_York
- `CONTENT_TEMPERATURE`: 0.8 (creativity level)
- `CONTENT_MAX_TOKENS`: 800 (response length)

---

### Testing Files

#### `tests/test_content_generation.py`
**Purpose**: Comprehensive test suite  
**Test coverage**:
- `TestContentGenerator`: OpenAI integration tests
  - Initialization
  - Content generation
  - Validation
  - Error handling
- `TestSheetsManager`: Google Sheets tests
  - Authentication
  - Row appending
  - Status updates
- `TestSlackNotifier`: Slack API tests
  - Message sending
  - Rich formatting
  - Error notifications
- `TestIntegration`: End-to-end workflow tests

**Run tests**:
```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

---

### Project Setup Files

#### `requirements.txt`
**Purpose**: Python dependencies  
**Main dependencies**:
- `openai>=1.12.0`: OpenAI API client
- `gspread>=5.12.0`: Google Sheets client
- `oauth2client>=4.1.3`: Google OAuth2
- `slack-sdk>=3.26.0`: Slack API client
- `python-dotenv>=1.0.0`: Environment variables
- `pytz>=2024.1`: Timezone handling

**Dev dependencies**:
- `pytest`: Testing framework
- `black`: Code formatting
- `flake8`: Linting
- `mypy`: Type checking

---

#### `setup.py`
**Purpose**: Package configuration  
**What it does**:
- Defines package metadata
- Lists dependencies
- Creates console scripts entry point
- Enables installation via pip

**Install package**:
```bash
pip install -e .
```

---

#### `.gitignore`
**Purpose**: Git ignore rules  
**Excludes**:
- Python artifacts (`__pycache__`, `*.pyc`)
- Virtual environments (`venv/`, `env/`)
- Environment files (`.env`, credentials)
- IDE files (`.vscode/`, `.idea/`)
- Log files (`*.log`)
- Test artifacts (`.pytest_cache/`, `.coverage`)

---

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              GitHub Actions (Cron: 8 AM EST)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │   main.py     │ ◄── Entry Point
              └───────┬───────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌─────────────┐
│ generate_    │ │ save_to_ │ │ send_slack_ │
│ content.py   │ │ sheets.py│ │ notification│
└──────┬───────┘ └────┬─────┘ └──────┬──────┘
       │              │               │
       ▼              ▼               ▼
┌──────────┐   ┌────────────┐  ┌──────────┐
│ OpenAI   │   │  Google    │  │  Slack   │
│   API    │   │  Sheets    │  │   API    │
└──────────┘   └────────────┘  └──────────┘
       │              │               │
       │              │               │
       └──────────────┴───────────────┘
                      │
                      ▼
              📧 Notification
                  Sent!
```

---

## 📊 Data Flow

1. **GitHub Actions** triggers at 8:00 AM EST
2. **main.py** initializes all services
3. **generate_content.py**:
   - Loads prompts from `config/prompts.json`
   - Calls OpenAI API
   - Returns: `{caption, hashtags, image_description, metadata}`
4. **save_to_sheets.py**:
   - Authenticates with service account
   - Appends row to Google Sheet
   - Returns: Sheet URL
5. **send_slack_notification.py**:
   - Formats rich message blocks
   - Sends to Slack channel
   - Returns: Message timestamp
6. **main.py** logs success and exits

---

## 🎯 Quick Commands Reference

### Local Development
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp config/.env.example config/.env

# Test individual modules
python src/generate_content.py
python src/save_to_sheets.py
python src/send_slack_notification.py

# Run full workflow
python src/main.py

# Run tests
pytest tests/ -v
pytest tests/ --cov=src

# Code quality
black src/ tests/
flake8 src/ tests/
mypy src/
```

### GitHub Actions
```bash
# Push to trigger CI
git add .
git commit -m "Update automation"
git push

# View logs
# Go to Actions tab → Select workflow → View logs
```

---

## 🔐 Security Notes

**Sensitive files (never commit)**:
- `config/.env`
- `config/credentials.json`
- Any files with API keys or tokens

**Protected by `.gitignore`**:
- All credential files
- Environment files
- Service account JSON files

**Stored in GitHub Secrets**:
- `OPENAI_API_KEY`
- `GOOGLE_SHEETS_CREDENTIALS`
- `SHEET_ID`
- `SLACK_BOT_TOKEN`
- `SLACK_CHANNEL_ID`

---

## 📈 Cost Estimates

**OpenAI API** (gpt-4o-mini):
- ~$0.01-0.02 per generation
- ~$0.30-0.60 per month (daily)

**Google Sheets API**:
- Free (within quota limits)
- 500 requests per 100 seconds

**Slack API**:
- Free (standard plan)

**GitHub Actions**:
- Free for public repos
- 2,000 minutes/month for private repos

**Total monthly cost**: ~$0.50-1.00 💰

---

**Built with 💜 for The17Project**
