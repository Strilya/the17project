"""
Instagram Poster - Direct posting via Instagram Graph API
Handles automatic reel uploads with captions
"""

import os
import time
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, TwoFactorRequired


class InstagramPoster:
    def __init__(self):
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')

        if not self.username or not self.password:
            raise ValueError("Instagram credentials not found in environment variables")

        self.client = Client()
        self.session_file = 'config/instagram_session.json'
        self._login()

    def _login(self):
        """Login to Instagram with session persistence"""
        try:
            # Try to load existing session
            if os.path.exists(self.session_file):
                print("   Loading existing Instagram session...")
                self.client.load_settings(self.session_file)
                self.client.login(self.username, self.password)
                print("   ✅ Instagram session loaded successfully")
            else:
                # Fresh login
                print("   Fresh Instagram login...")
                self.client.login(self.username, self.password)

                # Create config directory if it doesn't exist
                os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
                self.client.dump_settings(self.session_file)
                print("   ✅ Instagram login successful, session saved")

        except TwoFactorRequired:
            print("   ❌ Two-factor authentication required. Please disable 2FA or provide code.")
            raise
        except ChallengeRequired:
            print("   ❌ Instagram challenge required. Please login manually first.")
            raise
        except LoginRequired:
            print("   ❌ Instagram login failed. Check credentials.")
            raise
        except Exception as e:
            print(f"   ❌ Instagram login error: {e}")
            raise

    def post_reel(self, video_path, caption, thumbnail_path=None):
        """
        Post a reel to Instagram

        Args:
            video_path: Path to video file (FULL QUALITY, no size limit)
            caption: Instagram caption with line breaks preserved
            thumbnail_path: Optional custom thumbnail

        Returns:
            dict: Posted media info or None if failed
        """
        try:
            print(f"   📤 Uploading reel to Instagram...")
            print(f"      Video: {video_path}")
            print(f"      Caption length: {len(caption)} chars")

            # Upload reel (instagrapi handles all Instagram requirements)
            media = self.client.clip_upload(
                path=video_path,
                caption=caption,
                thumbnail=thumbnail_path,
                extra_data={
                    "custom_accessibility_caption": "",
                    "like_and_view_counts_disabled": False,
                    "disable_comments": False,
                }
            )

            print(f"   ✅ Reel posted successfully!")
            print(f"      Media ID: {media.id}")
            print(f"      URL: https://www.instagram.com/p/{media.code}/")

            return {
                'media_id': media.id,
                'code': media.code,
                'url': f"https://www.instagram.com/p/{media.code}/",
                'posted_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            print(f"   ❌ Failed to post reel: {e}")
            return None

    def verify_post(self, media_code):
        """Verify a post exists"""
        try:
            media = self.client.media_info_by_shortcode(media_code)
            return media is not None
        except:
            return False
