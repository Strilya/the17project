"""
Slack Notification Module

This module sends notifications to Slack when new Instagram content is generated.
Provides rich formatting with content preview and action buttons.

Main functionality:
- Sends formatted messages to Slack channels
- Includes content preview (caption snippet, hashtag count)
- Provides links to Google Sheets for full content
- Handles errors and provides fallback notifications
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class SlackNotifier:
    """
    Handles Slack notifications for content generation events.

    This class manages:
    1. Slack API authentication
    2. Message formatting with rich blocks
    3. Sending notifications to specified channels
    4. Error handling and retry logic
    """

    def __init__(self, bot_token: Optional[str] = None, channel_id: Optional[str] = None):
        """
        Initialize the SlackNotifier.

        Args:
            bot_token: Slack Bot OAuth token
            channel_id: Default channel ID for notifications
        """
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("Slack bot token not found. Set SLACK_BOT_TOKEN environment variable.")

        self.channel_id = channel_id or os.getenv("SLACK_CHANNEL_ID", "#content-automation")

        # Initialize Slack client
        self.client = WebClient(token=self.bot_token)

        # Verify connection
        self._verify_connection()

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
            Slack API response dictionary

        Raises:
            SlackApiError: If message sending fails
        """
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
            Slack API response dictionary
        """
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
            Slack API response dictionary
        """
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
