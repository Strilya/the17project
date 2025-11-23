"""
Slack Notification Module

This module sends notifications to Slack when new Instagram content is generated.
Provides rich formatting with content preview and action buttons.

Main functionality:
- Sends formatted messages to Slack channels
- Includes content preview (caption snippet, hashtag count)
- Provides links to Google Sheets for full content
- Handles errors and provides fallback notifications
- Gracefully handles missing Slack configuration (optional integration)
"""

# Import os module to access environment variables
import os
# Import logging module to track execution and debug issues
import logging
# Import datetime to add timestamps to notifications
from datetime import datetime
# Import typing utilities for type hints
from typing import Dict, Any, Optional

# Import Slack WebClient for API communication
from slack_sdk import WebClient
# Import SlackApiError for error handling
from slack_sdk.errors import SlackApiError
# Import dotenv to load environment variables
from dotenv import load_dotenv

# Configure logging to output INFO level messages with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def is_slack_configured() -> bool:
    """
    Check if Slack integration is properly configured.

    Returns:
        True if SLACK_BOT_TOKEN is set, False otherwise
    """
    # Check if the bot token environment variable exists and is not empty
    token = os.getenv("SLACK_BOT_TOKEN")
    # Return True only if token exists and is not an empty string
    return bool(token and token.strip())


class SlackNotifier:
    """
    Handles Slack notifications for content generation events.

    This class manages:
    1. Slack API authentication
    2. Message formatting with rich blocks
    3. Sending notifications to specified channels
    4. Error handling and retry logic
    5. Graceful handling when Slack is not configured (optional integration)
    """

    def __init__(self, bot_token: Optional[str] = None, channel_id: Optional[str] = None):
        """
        Initialize the SlackNotifier.

        Args:
            bot_token: Slack Bot OAuth token (optional - if not provided, Slack is disabled)
            channel_id: Default channel ID for notifications

        Note:
            If bot_token is not provided and SLACK_BOT_TOKEN env var is not set,
            the notifier will be initialized in disabled mode and all send methods
            will return success without actually sending messages.
        """
        # Get bot token from parameter or environment variable
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        # Get channel ID from parameter or environment variable
        self.channel_id = channel_id or os.getenv("SLACK_CHANNEL_ID", "#content-automation")

        # Track whether Slack is enabled (token is available)
        self.enabled = bool(self.bot_token and self.bot_token.strip())

        # If Slack is not configured, log warning and return early
        if not self.enabled:
            logger.warning("Slack bot token not found. Slack notifications are DISABLED.")
            logger.warning("Set SLACK_BOT_TOKEN environment variable to enable Slack notifications.")
            self.client = None
            return

        # Initialize Slack client with the bot token
        self.client = WebClient(token=self.bot_token)

        # Verify connection to Slack API
        self._verify_connection()

        # Log successful initialization
        logger.info("SlackNotifier initialized successfully")

    def _verify_connection(self) -> None:
        """
        Verify Slack API connection and bot permissions.

        Raises:
            SlackApiError: If authentication fails
        """
        try:
            response = self.client.auth_test()
            logger.info(f"Connected to Slack workspace: {response['team']}")
            logger.info(f"Bot user: {response['user']}")
        except SlackApiError as e:
            logger.error(f"Slack authentication failed: {e.response['error']}")
            raise

    def send_content_notification(
        self,
        content: Dict[str, Any],
        sheet_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a notification about newly generated content.

        Creates a rich Slack message with:
        - Header announcing new content
        - Preview of caption (first 150 chars)
        - Hashtag count
        - Image description snippet
        - Link to Google Sheets
        - Metadata (model, tokens, timestamp)

        Args:
            content: Dictionary containing generated content
                Required keys: caption, hashtags, image_description
                Optional keys: generated_at, model, tokens_used
            sheet_url: URL to Google Sheets (optional)

        Returns:
            Slack API response dictionary, or empty dict with 'skipped' key if disabled

        Raises:
            SlackApiError: If message sending fails (only when Slack is enabled)
        """
        # If Slack is not enabled, return early with a "skipped" response
        if not self.enabled:
            logger.info("Slack notification skipped (Slack not configured)")
            return {"skipped": True, "reason": "Slack not configured"}

        try:
            logger.info("Sending Slack notification...")

            # Extract content data
            caption = content.get("caption", "")
            hashtags = content.get("hashtags", [])
            image_desc = content.get("image_description", "")
            generated_at = content.get("generated_at", datetime.now().isoformat())
            model = content.get("model", "gpt-4o-mini")
            tokens = content.get("tokens_used", "N/A")

            # Format timestamp
            try:
                dt = datetime.fromisoformat(generated_at)
                timestamp_formatted = dt.strftime("%B %d, %Y at %I:%M %p")
            except:
                timestamp_formatted = generated_at

            # Create caption preview (first 150 characters)
            caption_preview = caption[:150] + "..." if len(caption) > 150 else caption

            # Create blocks for rich formatting
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "✨ New Instagram Content Generated!",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*The17Project* daily content is ready for review."
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Generated:*\n{timestamp_formatted}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Hashtags:*\n{len(hashtags)} tags"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Model:*\n{model}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Tokens:*\n{tokens}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Caption Preview:*\n```{caption_preview}```"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Image Design:*\n_{image_desc[:100]}..._"
                    }
                }
            ]

            # Add Google Sheets link if provided
            if sheet_url:
                blocks.append({
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📊 View in Google Sheets",
                                "emoji": True
                            },
                            "url": sheet_url,
                            "style": "primary"
                        }
                    ]
                })

            blocks.append({"type": "divider"})

            # Send message
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                text="New Instagram content generated for The17Project"  # Fallback text
            )

            logger.info(f"Notification sent successfully to {self.channel_id}")
            logger.info(f"Message timestamp: {response['ts']}")

            return response

        except SlackApiError as e:
            logger.error(f"Failed to send Slack notification: {e.response['error']}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending notification: {e}")
            raise

    def send_error_notification(self, error_message: str) -> Dict[str, Any]:
        """
        Send an error notification to Slack.

        Args:
            error_message: Description of the error

        Returns:
            Slack API response dictionary, or empty dict with 'skipped' key if disabled
        """
        # If Slack is not enabled, return early with a "skipped" response
        if not self.enabled:
            logger.info("Slack error notification skipped (Slack not configured)")
            return {"skipped": True, "reason": "Slack not configured"}

        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⚠️ Content Generation Error",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Error:*\n```{error_message}```"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                }
            ]

            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                text=f"Error: {error_message}"
            )

            logger.info("Error notification sent to Slack")
            return response

        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
            raise

    def send_simple_message(self, message: str) -> Dict[str, Any]:
        """
        Send a simple text message to Slack.

        Args:
            message: Message text

        Returns:
            Slack API response dictionary, or empty dict with 'skipped' key if disabled
        """
        # If Slack is not enabled, return early with a "skipped" response
        if not self.enabled:
            logger.info("Slack message skipped (Slack not configured)")
            return {"skipped": True, "reason": "Slack not configured"}

        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=message
            )
            logger.info(f"Simple message sent to {self.channel_id}")
            return response
        except SlackApiError as e:
            logger.error(f"Failed to send message: {e.response['error']}")
            raise


def main():
    """
    Main function for testing Slack notifications locally.

    Usage:
        python src/send_slack_notification.py
    """
    try:
        # Sample content for testing
        test_content = {
            "caption": "🔮 Seeing 17:17 everywhere? This isn't a coincidence.\n\nAngel number 17 is a powerful message about manifesting your dreams through aligned action. When this number appears, the universe is confirming you're on the right path.\n\nWhat to do when you see 17:\n✨ Trust your intuition\n✨ Take inspired action\n✨ Stay focused on your goals\n\nYour spiritual team is supporting every step. Keep going! 💫",
            "hashtags": [
                "#angelnumbers", "#manifestation", "#spirituality",
                "#the17project", "#angelnumber17", "#divinetiming"
            ],
            "image_description": "Purple gradient background (#6B46C1) with bold gold text displaying '17:17'. Centered layout with minimalist design. Gold accent line at bottom.",
            "generated_at": datetime.now().isoformat(),
            "model": "gpt-4o-mini",
            "tokens_used": 325
        }

        # Initialize notifier
        notifier = SlackNotifier()

        # Send notification
        sheet_url = f"https://docs.google.com/spreadsheets/d/{os.getenv('SHEET_ID', 'YOUR_SHEET_ID')}"
        response = notifier.send_content_notification(test_content, sheet_url)

        print("\n✅ Slack notification sent successfully!")
        print(f"Channel: {notifier.channel_id}")
        print(f"Message timestamp: {response['ts']}")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
