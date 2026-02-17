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

    def send_reel_notification(self, angel_number, style, content, hashtags, video_path, duration, test_mode=False):
        """Send Slack notification with ready-to-copy caption

        Args:
            angel_number: Content identifier (e.g., "1111" or "LP7-identity")
            style: Content type (e.g., "angel_number" or "life_path")
            content: Content dict with hook, meaning, action, cta
            hashtags: Either hashtags string OR full Instagram caption (for Life Path)
            video_path: Path to video file
            duration: Video duration in seconds
            test_mode: If True, marks notification as TEST
        """

        if not self.enabled:
            return

        try:
            # Get current timestamp
            timestamp = datetime.now().strftime("%b %d, %Y %I:%M %p")

            # Determine if hashtags is a full caption (has newlines) or just hashtags
            if '\n' in hashtags and len(hashtags) > 100:
                # Full caption provided (Life Path content)
                full_caption = hashtags
                content_label = "Content ID"
            else:
                # Just hashtags (legacy Angel Number format)
                caption_parts = [
                    content.get('hook', ''),
                    content.get('meaning', ''),
                    content.get('action', ''),
                    content.get('cta', '')
                ]
                caption_text = ' '.join([part for part in caption_parts if part])
                full_caption = f"{caption_text}\n\n{hashtags}"
                content_label = "Angel Number"

            # Format the Slack message header with info
            header_text = "🧪 TEST REEL GENERATED!" if test_mode else "🎬 NEW REEL GENERATED!"
            message_blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": header_text,
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*{content_label}:*\n{angel_number}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Type:*\n{style.replace('_', ' ').title()}"
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
                }
            ]

            # Send header message with blocks
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=message_blocks,
                text=f"New reel generated: {angel_number} ({style})"  # Fallback text
            )

            # Send caption as pure plain text without markdown formatting
            # This preserves exact line breaks when copying to Instagram
            caption_header = "📝 INSTAGRAM CAPTION:"

            # Build the complete message with actual line breaks (not escape sequences)
            caption_message = f"""{caption_header}

{full_caption}"""

            self.client.chat_postMessage(
                channel=self.channel_id,
                text=caption_message,
                thread_ts=response['ts'],
                mrkdwn=False  # Disable markdown processing to preserve formatting
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

    def send_success_notification(self, content_type, content_identifier, instagram_url, caption, duration):
        """
        Send success notification after Instagram posting
        NO video attachment - just confirmation and link

        Args:
            content_type: 'life_path' or 'angel_number'
            content_identifier: Life Path number or Angel Number
            instagram_url: URL of posted Instagram reel
            caption: The caption that was posted
            duration: Video duration in seconds
        """
        if not self.enabled:
            return

        # Format content type for display
        if content_type == 'life_path':
            content_label = f"Life Path {content_identifier}"
        else:
            content_label = f"Angel Number {content_identifier}"

        # Build message with actual line breaks
        message = f"""✅ REEL POSTED TO INSTAGRAM

📱 Content: {content_label}
🔗 View: {instagram_url}
⏱️ Duration: {duration}s

📝 Caption:
{caption}

---
Posted via automation 🤖
"""

        try:
            self.client.chat_postMessage(
                channel=self.channel_id,
                text=message,
                mrkdwn=False  # Disable markdown to preserve caption formatting
            )
            print("   ✅ Slack success notification sent")
        except Exception as e:
            print(f"   ⚠️  Slack notification failed: {e}")

    def send_error_notification(self, content_type, content_identifier, error):
        """
        Send error notification if Instagram posting fails

        Args:
            content_type: 'life_path' or 'angel_number'
            content_identifier: Life Path number or Angel Number
            error: Error message
        """
        if not self.enabled:
            return

        message = f"""❌ INSTAGRAM POSTING FAILED

📱 Content: {content_type} - {content_identifier}
🚨 Error: {error}

Please check logs and post manually if needed.
"""

        try:
            self.client.chat_postMessage(
                channel=self.channel_id,
                text=message
            )
            print("   ✅ Slack error notification sent")
        except Exception as e:
            print(f"   ⚠️  Slack notification failed: {e}")

    def send_carousel_notification(self, carousel_id, carousel_type, instagram_url, slide_count):
        """
        Send notification when a carousel is posted

        Args:
            carousel_id: Unique carousel identifier (e.g., "LP1_breakdown")
            carousel_type: Type of carousel (e.g., "life_path_breakdown")
            instagram_url: URL of posted Instagram carousel
            slide_count: Number of slides in the carousel
        """
        if not self.enabled:
            return

        # Format carousel type for display
        type_labels = {
            'life_path_breakdown': '📊 Life Path Breakdown',
            'life_path_compatibility': '💕 Compatibility Guide',
            'life_path_career': '💼 Career Deep Dive',
            'life_path_love': '❤️ Love & Relationships',
            'angel_number': '🔮 Angel Number Guide'
        }
        type_label = type_labels.get(carousel_type, carousel_type)

        message = f"""✅ CAROUSEL POSTED TO INSTAGRAM

📱 Type: {type_label}
🆔 ID: {carousel_id}
📸 Slides: {slide_count}
🔗 View: {instagram_url}

---
Posted via automation 🤖
"""

        try:
            self.client.chat_postMessage(
                channel=self.channel_id,
                text=message
            )
            print("   ✅ Slack carousel notification sent")
        except Exception as e:
            print(f"   ⚠️  Slack notification failed: {e}")
