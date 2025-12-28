"""
Slack Notifier - Send reel notifications with ready-to-copy captions
Posts: preview, caption with hashtags, video file, quick stats
"""

import os
import subprocess
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackNotifier:
    def __init__(self):
        """Initialize Slack client"""
        self.client = None
        self.channel_id = None
        self.enabled = False

        try:
            # Load credentials from environment
            bot_token = os.getenv('SLACK_BOT_TOKEN')
            channel_id = os.getenv('SLACK_CHANNEL_ID')

            if not bot_token or not channel_id:
                print("   ⚠️  Slack not configured (missing token or channel)")
                return

            # Initialize Slack client
            self.client = WebClient(token=bot_token)
            self.channel_id = channel_id

            # Test connection
            self.client.auth_test()

            self.enabled = True
            print("   ✅ Slack connected")

        except Exception as e:
            print(f"   ⚠️  Slack setup failed: {e}")
            self.enabled = False

    def send_reel_notification(self, angel_number, style, content, hashtags, video_path, duration):
        """Send Slack notification with ready-to-copy caption"""

        if not self.enabled:
            return

        try:
            # Get current timestamp
            timestamp = datetime.now().strftime("%b %d, %Y %I:%M %p")

            # Prepare FULL caption text (all content)
            caption_parts = [
                content.get('hook', ''),
                content.get('meaning', ''),
                content.get('action', ''),
                content.get('cta', '')
            ]
            caption_text = ' '.join([part for part in caption_parts if part])

            # Format the Slack message
            message_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🎬 NEW REEL GENERATED!",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Angel Number:*\n{angel_number}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Style:*\n{style.title()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Duration:*\n{duration:.1f}s"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Created:*\n{timestamp}"
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
                        "text": "*📝 COPY THIS CAPTION:*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{caption_text}\n\n{hashtags}```"
                    }
                }
            ]

            # Send message with blocks
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=message_blocks,
                text=f"New reel generated: {angel_number} ({style})"  # Fallback text
            )

            # Upload video file - compress if over 10MB
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # Convert to MB
            upload_path = video_path

            if file_size >= 10:
                # Compress video for Slack upload
                print(f"   📦 Compressing video for Slack ({file_size:.1f}MB -> <10MB)...")
                compressed_path = video_path.replace('.mp4', '_slack.mp4')

                try:
                    # Use ffmpeg to compress: target ~6-8MB (under 10MB)
                    subprocess.run([
                        'ffmpeg', '-i', video_path,
                        '-vf', 'scale=1080:1920',  # Keep same resolution
                        '-c:v', 'libx264',
                        '-preset', 'medium',  # Balanced compression
                        '-b:v', '2500k',  # 2.5Mbps video bitrate = ~6-8MB for 20-25s
                        '-maxrate', '2800k',  # Max bitrate cap
                        '-bufsize', '5600k',  # Buffer size
                        '-b:a', '96k',  # Good audio quality for voice
                        '-y',  # Overwrite
                        compressed_path
                    ], check=True, capture_output=True)

                    compressed_size = os.path.getsize(compressed_path) / (1024 * 1024)
                    upload_path = compressed_path
                    print(f"   ✅ Compressed to {compressed_size:.1f}MB")
                except Exception as e:
                    print(f"   ⚠️  Compression failed: {e}, sending original if under limit")
                    upload_path = video_path if file_size < 10 else None

            if upload_path and os.path.exists(upload_path):
                final_size = os.path.getsize(upload_path) / (1024 * 1024)
                if final_size < 10:
                    # Upload the video
                    self.client.files_upload_v2(
                        channel=self.channel_id,
                        file=upload_path,
                        filename=os.path.basename(video_path),  # Use original filename
                        initial_comment="🎥 Video file attached",
                        thread_ts=response['ts']  # Reply in thread
                    )
                    print(f"   ✅ Slack notification sent (video attached, {final_size:.1f}MB)")

                    # Clean up compressed file
                    if upload_path != video_path and os.path.exists(upload_path):
                        os.remove(upload_path)
                else:
                    self.client.chat_postMessage(
                        channel=self.channel_id,
                        text=f"⚠️ Video still too large after compression ({final_size:.1f}MB) - check output folder: `{os.path.basename(video_path)}`",
                        thread_ts=response['ts']
                    )
                    print(f"   ⚠️  Slack notification sent (video too large even after compression)")
            else:
                self.client.chat_postMessage(
                    channel=self.channel_id,
                    text=f"⚠️ Could not compress video - check output folder: `{os.path.basename(video_path)}`",
                    thread_ts=response['ts']
                )
                print(f"   ⚠️  Could not upload video to Slack")

        except SlackApiError as e:
            print(f"   ⚠️  Slack notification failed: {e.response['error']}")
        except Exception as e:
            print(f"   ⚠️  Slack notification failed: {e}")
