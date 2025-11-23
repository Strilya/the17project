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
            "Date",
            "Caption",
            "Hashtags",
            "Image_description",
            "Status",
            "Posted_Date",
            "Engagement_notes"
        ]

        worksheet.append_row(headers)
        logger.info("Created header row in worksheet")

    def save_content(self, content: Dict[str, Any]) -> None:
        """
        Save generated content to Google Sheets.

        This method appends a new row to the worksheet with:
        - Timestamp of generation
        - Date (formatted)
        - Caption text
        - Hashtags (joined as string)
        - Image description
        - Model used
        - Tokens consumed
        - Status (defaults to "Generated")

        Args:
            content: Dictionary containing generated content
                Required keys: caption, hashtags, image_description
                Optional keys: generated_at, model, tokens_used
        """
        try:
            logger.info("Saving content to Google Sheets...")

            # DEBUG: Log the exact content structure being saved
            logger.info(f"Content structure received: {json.dumps(content, indent=2, default=str)}")
            logger.info(f"Caption type: {type(content.get('caption')).__name__}")
            logger.info(f"Hashtags type: {type(content.get('hashtags')).__name__}")
            logger.info(f"Image_description type: {type(content.get('image_description')).__name__}")

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

            # Prepare row data matching column structure:
            # A: Date, B: Caption, C: Hashtags, D: Image_description,
            # E: Status (empty), F: Posted_Date (empty), G: Engagement_notes (empty)
            row = [
                date_formatted,
                caption_formatted,
                hashtags_formatted,
                image_desc_formatted,
                "",  # Status (empty)
                "",  # Posted_Date (empty)
                ""   # Engagement_notes (empty)
            ]

            # DEBUG: Log the exact row being written
            logger.info(f"Row being written (7 columns expected):")
            logger.info(f"  [0] Date: {row[0]}")
            logger.info(f"  [1] Caption: {row[1][:50]}..." if len(row[1]) > 50 else f"  [1] Caption: {row[1]}")
            logger.info(f"  [2] Hashtags: {row[2][:50]}..." if len(row[2]) > 50 else f"  [2] Hashtags: {row[2]}")
            logger.info(f"  [3] Image_desc: {row[3][:50]}..." if len(row[3]) > 50 else f"  [3] Image_desc: {row[3]}")
            logger.info(f"  [4] Status: '{row[4]}'")
            logger.info(f"  [5] Posted_Date: '{row[5]}'")
            logger.info(f"  [6] Engagement_notes: '{row[6]}'")
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
            # Update status column (column E = 5)
            self.worksheet.update_cell(row_number, 5, status)

            # Update notes if provided (column G = 7)
            if notes:
                self.worksheet.update_cell(row_number, 7, notes)

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

        # Test Case 1: Hashtags as LIST (expected format)
        print("\n--- Test Case 1: Hashtags as LIST ---")
        test_content_list = {
            "caption": "Test caption for The17Project - testing list format",
            "hashtags": ["#test", "#the17project", "#angelnumbers", "#manifestation"],
            "image_description": "Purple background with gold text - test image",
            "generated_at": datetime.now().isoformat(),
            "model": "claude-3-haiku",
            "tokens_used": 250
        }

        print(f"Input hashtags type: {type(test_content_list['hashtags']).__name__}")
        print(f"Input hashtags value: {test_content_list['hashtags']}")

        # Test Case 2: Hashtags as STRING (fallback format)
        print("\n--- Test Case 2: Hashtags as STRING (defensive test) ---")
        test_content_string = {
            "caption": "Test caption - testing string format",
            "hashtags": "#test #the17project #angelnumbers #manifestation",
            "image_description": "Purple background with gold text - string test",
            "generated_at": datetime.now().isoformat(),
            "model": "claude-3-haiku",
            "tokens_used": 250
        }

        print(f"Input hashtags type: {type(test_content_string['hashtags']).__name__}")
        print(f"Input hashtags value: {test_content_string['hashtags']}")

        # Choose which test to run (use list format for actual test)
        print("\n--- Running actual save with LIST format ---")
        manager = SheetsManager()
        manager.save_content(test_content_list)

        print("\n" + "="*70)
        print("SUCCESS: Content saved to Google Sheets!")
        print(f"Sheet URL: https://docs.google.com/spreadsheets/d/{manager.sheet_id}")
        print("="*70)
        print("\nPlease verify in Google Sheets:")
        print("  - Column A (Date): Should have date formatted as YYYY-MM-DD")
        print("  - Column B (Caption): Should have caption text")
        print("  - Column C (Hashtags): Should have hashtags separated by spaces")
        print("  - Column D (Image_description): Should have image description")
        print("  - Columns E, F, G: Should be empty")
        print("="*70)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
