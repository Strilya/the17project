"""
Slack Notification Module - MOBILE OPTIMIZED

Sends video file + formatted caption to Slack for easy mobile posting.

Mobile workflow:
1. Video uploaded to Slack (downloadable on phone)
2. Caption + hashtags formatted for copy/paste
3. Google Sheet link to track post
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


def is_slack_configured() -> bool:
    """Check if Slack integration is configured."""
    token = os.getenv("SLACK_BOT_TOKEN")
    return bool(token and token.strip())


class SlackNotifier:
    """Handles Slack notifications optimized for mobile Instagram posting."""

    def __init__(self, bot_token: Optional[str] = None, channel_id: Optional[str] = None):
        """Initialize SlackNotifier."""
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.channel_id = channel_id or os.getenv("SLACK_CHANNEL_ID", "#content-automation")
        
        self.enabled = bool(self.bot_token and self.bot_token.strip())
        
        if not self.enabled:
            logger.warning("Slack bot token not found. Notifications DISABLED.")
            self.client = None
            return
        
        self.client = WebClient(token=self.bot_token)
        self._verify_connection()
        logger.info("SlackNotifier initialized successfully")

    def _verify_connection(self) -> None:
        """Verify Slack API connection."""
        try:
            response = self.client.auth_test()
            logger.info(f"Connected to Slack: {response['team']}")
        except SlackApiError as e:
            logger.error(f"Slack authentication failed: {e.response['error']}")
            raise

    def send_mobile_post(
        self,
        content: Dict[str, Any],
        video_path: Optional[str] = None,
        sheet_url: Optional[str] = None,
        sheet_row: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send video + formatted content optimized for mobile posting.
        
        Args:
            content: Generated content dict
            video_path: Path to generated video file
            sheet_url: Google Sheets URL
            sheet_row: Row number in sheet
            
        Returns:
            Slack API response
        """
        if not self.enabled:
            logger.info("Slack disabled - skipping")
            return {"skipped": True}

        try:
            logger.info("📱 Sending mobile-optimized post to Slack...")

            # Extract content
            caption = content.get("caption", "")
            hashtags = content.get("hashtags", [])
            topic = content.get("topic", "")
            category = content.get("category", "")

            # Format hashtags for Instagram
            hashtags_text = " ".join(hashtags) if isinstance(hashtags, list) else hashtags

            # Create copy-paste ready caption
            full_caption = f"{caption}\n\n{hashtags_text}"

            # Upload video file first (if exists)
            file_info = None
            if video_path and Path(video_path).exists():
                logger.info(f"Uploading video: {video_path}")
                
                upload_response = self.client.files_upload_v2(
                    channel=self.channel_id,
                    file=video_path,
                    title=f"The17Project - {topic}",
                    initial_comment="📹 **NEW REEL READY TO POST!**"
                )
                
                file_info = upload_response.get("file", {})
                logger.info(f"✅ Video uploaded to Slack")

            # Send formatted message with caption
            message_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📱 Ready to Post: {topic}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Topic:*\n{topic}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Category:*\n{category}"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📝 *CAPTION (Copy & Paste to Instagram):*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{full_caption}```"
                    }
                }
            ]

            # Add Google Sheets button
            if sheet_url:
                # Create direct row link if row number provided
                if sheet_row:
                    row_url = f"{sheet_url}#gid=0&range=A{sheet_row}"
                else:
                    row_url = sheet_url
                
                message_blocks.append({
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📊 Open Google Sheet",
                                "emoji": True
                            },
                            "url": row_url,
                            "style": "primary"
                        }
                    ]
                })

            # Add instructions
            message_blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "📱 *Mobile Instructions:* Download video → Open Instagram → Upload → Paste caption → Post!"
                    }
                ]
            })

            # Send message (after video upload)
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=message_blocks,
                text=f"New content ready: {topic}"
            )

            logger.info(f"✅ Mobile post sent to {self.channel_id}")
            
            return {
                "success": True,
                "message_ts": response['ts'],
                "video_uploaded": file_info is not None
            }

        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            raise
        except Exception as e:
            logger.error(f"Failed to send mobile post: {e}")
            raise

    def send_error_notification(self, error_message: str) -> Dict[str, Any]:
        """Send error notification."""
        if not self.enabled:
            return {"skipped": True}

        try:
            self.client.chat_postMessage(
                channel=self.channel_id,
                text=f"⚠️ Content generation error:\n```{error_message}```"
            )
            return {"success": True}
        except Exception as e:
            logger.error(f"Failed to send error: {e}")
            raise
