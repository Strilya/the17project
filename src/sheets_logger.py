"""
Google Sheets Logger - Track all generated reels
Logs: date, angel number, style, transcript, captions, hashtags, duration, sources
"""

import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials


class SheetsLogger:
    def __init__(self):
        """Initialize Google Sheets connection"""
        self.sheet = None
        self.enabled = False

        try:
            # Load credentials from environment
            creds_path = os.getenv('GOOGLE_SHEETS_CREDS')
            sheet_id = os.getenv('GOOGLE_SHEET_ID')

            if not creds_path:
                print("   ⚠️  Google Sheets not configured: GOOGLE_SHEETS_CREDS not set")
                return
            if not sheet_id:
                print("   ⚠️  Google Sheets not configured: GOOGLE_SHEET_ID not set")
                return

            # Resolve credentials path (use absolute path)
            if not os.path.isabs(creds_path):
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                creds_path = os.path.join(project_root, creds_path)

            if not os.path.exists(creds_path):
                print(f"   ⚠️  Credentials file not found: {creds_path}")
                return

            # Set up credentials
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
            client = gspread.authorize(creds)

            # Open the spreadsheet
            spreadsheet = client.open_by_key(sheet_id)

            # Get or create "The17Project_Reels" worksheet
            try:
                self.sheet = spreadsheet.worksheet("The17Project_Reels")
            except:
                # Create new worksheet with headers
                self.sheet = spreadsheet.add_worksheet(
                    title="The17Project_Reels",
                    rows=1000,
                    cols=10
                )

                # Add header row
                headers = [
                    "Date/Time",
                    "Angel Number",
                    "Style",
                    "Transcript",
                    "Caption Text",
                    "Hashtags",
                    "Video Filename",
                    "Duration (s)",
                    "Video Sources",
                    "Status"
                ]
                self.sheet.append_row(headers)

            self.enabled = True
            print("   ✅ Google Sheets connected")

        except Exception as e:
            print(f"   ⚠️  Google Sheets setup failed: {e}")
            self.enabled = False

    def generate_hashtags(self, angel_number, content):
        """Generate 15-20 relevant hashtags (lowercase)"""

        # Base hashtags (always included)
        base_tags = [
            "angelnumbers",
            "spirituality",
            "numerology",
            "manifestation",
            "divinity"
        ]

        # Angel number specific
        number_tags = [
            angel_number,
            f"angelnumber{angel_number}",
            "synchronicity"
        ]

        # Content-based tags (extract from content)
        content_keywords = {
            "breakthrough": ["awakening", "transformation", "growth"],
            "abundance": ["prosperity", "wealth", "success"],
            "love": ["soulmate", "twinflame", "relationships"],
            "job": ["career", "success", "opportunity"],
            "guides": ["angels", "angelmessages", "divineguidance"],
            "alignment": ["alignment", "purpose", "destiny"],
            "intuition": ["intuition", "innervoice", "guidance"]
        }

        content_tags = []
        full_text = f"{content.get('hook', '')} {content.get('meaning', '')} {content.get('action', '')}".lower()

        for keyword, tags in content_keywords.items():
            if keyword in full_text:
                content_tags.extend(tags)

        # Additional spiritual tags
        additional_tags = [
            "lawofattraction",
            "consciousness",
            "universe",
            "spiritualjourney",
            "lightworker",
            "energyhealing",
            "metaphysical",
            "higherself",
            "ascension"
        ]

        # Combine all tags
        all_tags = base_tags + number_tags + content_tags + additional_tags

        # Remove duplicates and take first 18-20
        unique_tags = list(dict.fromkeys(all_tags))[:20]

        # Format with # and ensure lowercase
        hashtags = [f"#{tag.lower()}" for tag in unique_tags]

        return " ".join(hashtags)

    def get_generated_content(self):
        """Get all previously generated angel numbers to avoid repeats"""
        if not self.enabled:
            return {'angel_numbers': [], 'styles': []}

        try:
            # Get all data from sheet
            all_data = self.sheet.get_all_values()

            generated = {
                'angel_numbers': [],
                'styles': []
            }

            # Skip header row
            for row in all_data[1:]:
                if len(row) >= 3 and row[1] != 'TEST':  # Skip test entries
                    generated['angel_numbers'].append(row[1])  # Column B: Angel Number
                    generated['styles'].append(row[2])         # Column C: Style

            return generated

        except Exception as e:
            print(f"   ⚠️  Failed to fetch generated content: {e}")
            return {'angel_numbers': [], 'styles': []}

    def log_reel(self, angel_number, style, content, transcript, video_path, duration, video_sources=None, custom_caption=None, instagram_url=None):
        """Log generated reel to Google Sheets

        Args:
            angel_number: Content identifier (e.g., "1111" or "LP7-identity")
            style: Content type (e.g., "angel_number" or "life_path")
            content: Content dict with hook, meaning, action, cta
            transcript: Full transcript text
            video_path: Path to video file
            duration: Video duration in seconds
            video_sources: List of video sources (default: None)
            custom_caption: Optional pre-generated caption/hashtags (for Life Path content)
            instagram_url: URL of posted Instagram reel (default: None)

        Returns:
            str: Hashtags or custom caption
        """

        # Use custom caption if provided, otherwise generate hashtags
        if custom_caption:
            hashtags = custom_caption
        else:
            hashtags = self.generate_hashtags(angel_number, content)

        if not self.enabled:
            return hashtags

        try:
            # Generate caption text (full transcript for Instagram caption)
            caption_parts = [
                content.get('hook', ''),
                content.get('meaning', ''),
                content.get('action', ''),
                content.get('cta', '')
            ]
            caption_text = '\n\n'.join([part for part in caption_parts if part])

            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Get video filename
            video_filename = os.path.basename(video_path)

            # Format video sources (if provided)
            sources_str = ", ".join(video_sources) if video_sources else "N/A"

            # Prepare row data
            row_data = [
                timestamp,
                angel_number,
                style,
                transcript,
                caption_text,
                hashtags,
                video_filename,
                f"{duration:.1f}",
                sources_str,
                instagram_url or "",  # Instagram URL (empty if not posted)
                "Generated"
            ]

            # Append to sheet
            self.sheet.append_row(row_data)

            print(f"   ✅ Logged to Google Sheets")

            return hashtags  # Return hashtags for use in Slack notification

        except Exception as e:
            print(f"   ⚠️  Failed to log to Google Sheets: {e}")
            return None

    def _get_or_create_carousel_sheet(self):
        """Get or create the carousels worksheet"""
        try:
            creds_path = os.getenv('GOOGLE_SHEETS_CREDS')
            sheet_id = os.getenv('GOOGLE_SHEET_ID')

            if not creds_path or not sheet_id:
                return None

            if not os.path.isabs(creds_path):
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                creds_path = os.path.join(project_root, creds_path)

            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
            client = gspread.authorize(creds)
            spreadsheet = client.open_by_key(sheet_id)

            try:
                return spreadsheet.worksheet("The17Project_Carousels")
            except:
                # Create new worksheet with headers
                carousel_sheet = spreadsheet.add_worksheet(
                    title="The17Project_Carousels",
                    rows=500,
                    cols=6
                )
                headers = [
                    "Date/Time",
                    "Carousel ID",
                    "Type",
                    "Instagram URL",
                    "Status"
                ]
                carousel_sheet.append_row(headers)
                return carousel_sheet

        except Exception as e:
            print(f"   ⚠️  Failed to get carousel sheet: {e}")
            return None

    def log_carousel(self, carousel_id, carousel_type, instagram_url=None):
        """Log generated carousel to Google Sheets

        Args:
            carousel_id: Unique carousel identifier (e.g., "LP1_breakdown")
            carousel_type: Type of carousel (e.g., "life_path_breakdown")
            instagram_url: URL of posted Instagram carousel (default: None)
        """
        carousel_sheet = self._get_or_create_carousel_sheet()
        if not carousel_sheet:
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            row_data = [
                timestamp,
                carousel_id,
                carousel_type,
                instagram_url or "",
                "Posted" if instagram_url else "Generated"
            ]

            carousel_sheet.append_row(row_data)
            print(f"   ✅ Carousel logged to Google Sheets")

        except Exception as e:
            print(f"   ⚠️  Failed to log carousel: {e}")

    def get_posted_carousels(self):
        """Get list of carousel IDs that have been posted"""
        carousel_sheet = self._get_or_create_carousel_sheet()
        if not carousel_sheet:
            return []

        try:
            all_data = carousel_sheet.get_all_values()
            carousel_ids = []

            # Skip header row
            for row in all_data[1:]:
                if len(row) >= 2:
                    carousel_ids.append(row[1])  # Column B: Carousel ID

            return carousel_ids

        except Exception as e:
            print(f"   ⚠️  Failed to fetch posted carousels: {e}")
            return []
