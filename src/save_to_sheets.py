"""
Google Sheets Integration Module

This module handles saving generated Instagram content to Google Sheets
for tracking, analytics, and content calendar management.

Main functionality:
- Authenticates with Google Sheets API using service account
- Appends new content rows to The17Project_Content_Log sheet
- Handles credential loading from environment variables or JSON files
- Provides error handling and retry logic
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class SheetsManager:
    """
    Manages Google Sheets operations for content logging.

    This class handles:
    1. Authentication with Google Sheets API
    2. Sheet access and initialization
    3. Appending content rows
    4. Data formatting and validation
    """

    def __init__(self, sheet_id: Optional[str] = None, credentials: Optional[Dict] = None):
        """
        Initialize the SheetsManager.

        Args:
            sheet_id: Google Sheet ID (from URL)
            credentials: Google Service Account credentials dictionary
        """
        self.sheet_id = sheet_id or os.getenv("SHEET_ID")
        if not self.sheet_id:
            raise ValueError("Sheet ID not found. Set SHEET_ID environment variable.")

        # Load credentials
        self.credentials = credentials or self._load_credentials()

        # Authenticate and get client
        self.client = self._authenticate()

        # Get worksheet
        self.worksheet = self._get_worksheet()

        logger.info("SheetsManager initialized successfully")

    def _load_credentials(self) -> Dict[str, Any]:
        """
        Load Google Service Account credentials from environment.

        The credentials can be provided as:
        1. GOOGLE_SHEETS_CREDENTIALS env var (JSON string)
        2. Path to credentials.json file

        Returns:
            Dictionary containing service account credentials
        """
        creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")

        if creds_json:
            try:
                # Try to parse as JSON string
                credentials = json.loads(creds_json)
                logger.info("Loaded credentials from GOOGLE_SHEETS_CREDENTIALS environment variable")
                return credentials
            except json.JSONDecodeError:
                logger.error("GOOGLE_SHEETS_CREDENTIALS is not valid JSON")
                raise ValueError("Invalid GOOGLE_SHEETS_CREDENTIALS format")
        else:
            # Try to load from file
            creds_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "config",
                "credentials.json"
            )
            try:
                with open(creds_path, 'r') as f:
                    credentials = json.load(f)
                logger.info(f"Loaded credentials from {creds_path}")
                return credentials
            except FileNotFoundError:
                logger.error("No credentials found. Set GOOGLE_SHEETS_CREDENTIALS or create config/credentials.json")
                raise ValueError("Google Sheets credentials not found")

    def _authenticate(self) -> gspread.Client:
        """
        Authenticate with Google Sheets API.

        Uses OAuth2 service account credentials to authenticate.

        Returns:
            Authorized gspread client
        """
        try:
            # Define the scope for Google Sheets and Drive access
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]

            # Create credentials object
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                self.credentials,
                scope
            )

            # Authorize and create client
            client = gspread.authorize(creds)

            logger.info("Successfully authenticated with Google Sheets API")
            return client

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    def _get_worksheet(self) -> gspread.Worksheet:
        """
        Get or create the worksheet for content logging.

        Opens the spreadsheet and gets the first worksheet.
        If headers don't exist, creates them.

        Returns:
            gspread Worksheet object
        """
        try:
            # Open the spreadsheet by ID
            spreadsheet = self.client.open_by_key(self.sheet_id)

            # Get the first worksheet (or create if needed)
            try:
                worksheet = spreadsheet.get_worksheet(0)
            except IndexError:
                # Create first worksheet if it doesn't exist
                worksheet = spreadsheet.add_worksheet(
                    title="Content Log",
                    rows=1000,
                    cols=10
                )

            # Check if headers exist, if not create them
            if worksheet.row_values(1) == []:
                self._create_headers(worksheet)

            logger.info(f"Accessed worksheet: {worksheet.title}")
            return worksheet

        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Spreadsheet not found with ID: {self.sheet_id}")
            raise ValueError(f"Spreadsheet not found. Check SHEET_ID: {self.sheet_id}")
        except Exception as e:
            logger.error(f"Failed to access worksheet: {e}")
            raise

    def _create_headers(self, worksheet: gspread.Worksheet) -> None:
        """
        Create header row in the worksheet.

        Args:
            worksheet: gspread Worksheet object
        """
        headers = [
            "Date",              # A
            "Caption",           # B
            "Hashtags",          # C
            "Image_description", # D
            "Topic",             # E - NEW: The specific topic used
            "Category",          # F - NEW: Topic category (angel_numbers, productivity, etc.)
            "Status",            # G
            "Posted_Date",       # H
            "Likes",             # I - NEW: For manual tracking
            "Comments",          # J - NEW: For manual tracking
            "Saves",             # K - NEW: For manual tracking
            "Engagement_notes"   # L
        ]

        worksheet.append_row(headers)
        logger.info("Created header row in worksheet (12 columns)")

    def save_content(self, content: Dict[str, Any], topic: str = "", category: str = "") -> None:
        """
        Save generated content to Google Sheets.

        This method appends a new row to the worksheet with:
        - Date (formatted)
        - Caption text
        - Hashtags (joined as string)
        - Image description
        - Topic (the specific topic used for generation)
        - Category (topic category: angel_numbers, productivity, etc.)
        - Status, Posted_Date, Likes, Comments, Saves, Engagement_notes (empty for now)

        Args:
            content: Dictionary containing generated content
                Required keys: caption, hashtags, image_description
                Optional keys: generated_at, model, tokens_used, topic, category
            topic: The specific topic used (e.g., "717", "17-minute deep work")
            category: The topic category (e.g., "angel_numbers", "productivity")
        """
        try:
            logger.info("Saving content to Google Sheets...")

            # DEBUG: Log the exact content structure being saved
            logger.info(f"Content structure received: {json.dumps(content, indent=2, default=str)}")
            logger.info(f"Topic: {topic}, Category: {category}")

            # Extract and format data
            timestamp = content.get("generated_at", datetime.now().isoformat())
            date_formatted = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d")

            # DEFENSIVE: Handle hashtags whether it's a list OR a string
            hashtags_raw = content.get("hashtags", [])
            if isinstance(hashtags_raw, list):
                # Expected case: join list items with spaces
                hashtags_formatted = " ".join(str(tag) for tag in hashtags_raw)
            elif isinstance(hashtags_raw, str):
                # Fallback: already a string, use as-is
                hashtags_formatted = hashtags_raw
            else:
                # Unexpected type: convert to string representation
                logger.warning(f"Unexpected hashtags type: {type(hashtags_raw)}, converting to string")
                hashtags_formatted = str(hashtags_raw)

            # DEFENSIVE: Ensure caption and image_description are strings
            caption_formatted = str(content.get("caption", ""))
            image_desc_formatted = str(content.get("image_description", ""))

            # Get topic info from content if not provided as parameters
            topic_value = topic or content.get("topic", "")
            category_value = category or content.get("category", "")

            # Prepare row data matching column structure (12 columns):
            # A: Date, B: Caption, C: Hashtags, D: Image_description,
            # E: Topic, F: Category, G: Status, H: Posted_Date,
            # I: Likes, J: Comments, K: Saves, L: Engagement_notes
            row = [
                date_formatted,        # A: Date
                caption_formatted,     # B: Caption
                hashtags_formatted,    # C: Hashtags
                image_desc_formatted,  # D: Image_description
                topic_value,           # E: Topic (NEW)
                category_value,        # F: Category (NEW)
                "",                    # G: Status (empty)
                "",                    # H: Posted_Date (empty)
                "",                    # I: Likes (empty, manual entry)
                "",                    # J: Comments (empty, manual entry)
                "",                    # K: Saves (empty, manual entry)
                ""                     # L: Engagement_notes (empty)
            ]

            # DEBUG: Log the exact row being written
            logger.info(f"Row being written (12 columns):")
            logger.info(f"  [0] Date: {row[0]}")
            logger.info(f"  [1] Caption: {row[1][:50]}..." if len(row[1]) > 50 else f"  [1] Caption: {row[1]}")
            logger.info(f"  [2] Hashtags: {row[2][:50]}..." if len(row[2]) > 50 else f"  [2] Hashtags: {row[2]}")
            logger.info(f"  [3] Image_desc: {row[3][:50]}..." if len(row[3]) > 50 else f"  [3] Image_desc: {row[3]}")
            logger.info(f"  [4] Topic: '{row[4]}'")
            logger.info(f"  [5] Category: '{row[5]}'")
            logger.info(f"  [6] Status: '{row[6]}'")
            logger.info(f"  [7-11] Empty analytics columns")
            logger.info(f"Row length: {len(row)} columns")

            # Append row to worksheet
            self.worksheet.append_row(row, value_input_option='RAW')

            logger.info(f"Content saved successfully to row {self.worksheet.row_count}")
            logger.info(f"Sheet URL: https://docs.google.com/spreadsheets/d/{self.sheet_id}")

        except KeyError as e:
            logger.error(f"Missing required field in content: {e}")
            raise ValueError(f"Content missing required field: {e}")
        except Exception as e:
            logger.error(f"Failed to save content to Google Sheets: {e}")
            raise

    def get_recent_content(self, num_rows: int = 10) -> List[List[str]]:
        """
        Retrieve the most recent content entries.

        Args:
            num_rows: Number of recent rows to retrieve

        Returns:
            List of rows (each row is a list of cell values)
        """
        try:
            all_rows = self.worksheet.get_all_values()

            # Return last N rows (excluding header)
            if len(all_rows) > 1:
                return all_rows[-num_rows:]
            else:
                return []

        except Exception as e:
            logger.error(f"Failed to retrieve recent content: {e}")
            raise

    def update_status(self, row_number: int, status: str, notes: str = "") -> None:
        """
        Update the status of a content entry.

        Args:
            row_number: Row number to update (1-indexed, including header)
            status: New status (e.g., "Posted", "Scheduled", "Archived")
            notes: Optional notes to add
        """
        try:
            # Update status column (column G = 7, was E = 5 before new columns)
            self.worksheet.update_cell(row_number, 7, status)

            # Update notes if provided (column L = 12, was G = 7 before)
            if notes:
                self.worksheet.update_cell(row_number, 12, notes)

            logger.info(f"Updated row {row_number} status to: {status}")

        except Exception as e:
            logger.error(f"Failed to update status: {e}")
            raise


def main():
    """
    Main function for testing Google Sheets integration locally.

    Usage:
        python src/save_to_sheets.py
    """
    try:
        print("\n" + "="*70)
        print("TESTING GOOGLE SHEETS INTEGRATION")
        print("="*70)

        # Test content with topic tracking
        print("\n--- Test: Content with Topic Tracking ---")
        test_content = {
            "caption": "Test caption for The17Project - testing topic tracking",
            "hashtags": ["#test", "#the17project", "#angelnumbers", "#manifestation"],
            "image_description": "Purple background with gold text - test image",
            "generated_at": datetime.now().isoformat(),
            "model": "claude-3-haiku",
            "tokens_used": 250,
            "topic": "717",
            "category": "angel_numbers"
        }

        print(f"Topic: {test_content['topic']}")
        print(f"Category: {test_content['category']}")
        print(f"Hashtags type: {type(test_content['hashtags']).__name__}")

        # Run the save test
        print("\n--- Running save with topic tracking ---")
        manager = SheetsManager()
        manager.save_content(
            content=test_content,
            topic=test_content["topic"],
            category=test_content["category"]
        )

        print("\n" + "="*70)
        print("SUCCESS: Content saved to Google Sheets!")
        print(f"Sheet URL: https://docs.google.com/spreadsheets/d/{manager.sheet_id}")
        print("="*70)
        print("\nPlease verify in Google Sheets (12 columns):")
        print("  - Column A (Date): YYYY-MM-DD")
        print("  - Column B (Caption): Caption text")
        print("  - Column C (Hashtags): Hashtags separated by spaces")
        print("  - Column D (Image_description): Image description")
        print("  - Column E (Topic): '717'")
        print("  - Column F (Category): 'angel_numbers'")
        print("  - Columns G-L: Empty (Status, Posted_Date, Likes, Comments, Saves, Notes)")
        print("="*70)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
