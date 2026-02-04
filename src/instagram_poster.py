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
        """Login to Instagram with session persistence and validation"""
        session_loaded = False

        # Try to load existing session first
        if os.path.exists(self.session_file):
            try:
                print("   Loading existing Instagram session...")
                self.client.load_settings(self.session_file)
                self.client.login(self.username, self.password)

                # Validate session by making a simple API call
                if self._validate_session():
                    print("   ✅ Instagram session loaded and validated")
                    session_loaded = True
                else:
                    print("   ⚠️  Session expired, refreshing...")
                    self._clear_session()

            except Exception as e:
                print(f"   ⚠️  Session load failed: {e}")
                self._clear_session()

        # Fresh login if no valid session
        if not session_loaded:
            self._fresh_login()

    def _validate_session(self):
        """Check if session is still valid by fetching account info"""
        try:
            # Simple API call to verify session works
            self.client.account_info()
            return True
        except Exception:
            return False

    def _clear_session(self):
        """Delete stale session file"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
                print("   🗑️  Cleared stale session")
        except Exception:
            pass
        # Reset client
        self.client = Client()

    def _fresh_login(self):
        """Perform fresh login and save session"""
        try:
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

    def post_carousel(self, image_paths, caption):
        """
        Post a carousel (album) to Instagram

        Args:
            image_paths: List of paths to image files (2-10 images)
            caption: Instagram caption with line breaks preserved

        Returns:
            dict: Posted media info or None if failed
        """
        try:
            if len(image_paths) < 2:
                print(f"   ❌ Carousel requires at least 2 images, got {len(image_paths)}")
                return None

            if len(image_paths) > 10:
                print(f"   ⚠️  Instagram allows max 10 images, truncating to 10")
                image_paths = image_paths[:10]

            print(f"   📤 Uploading carousel to Instagram...")
            print(f"      Images: {len(image_paths)}")
            print(f"      Caption length: {len(caption)} chars")

            # Upload carousel (instagrapi handles all Instagram requirements)
            media = self.client.album_upload(
                paths=image_paths,
                caption=caption
            )

            print(f"   ✅ Carousel posted successfully!")
            print(f"      Media ID: {media.id}")
            print(f"      URL: https://www.instagram.com/p/{media.code}/")

            return {
                'media_id': media.id,
                'code': media.code,
                'url': f"https://www.instagram.com/p/{media.code}/",
                'posted_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'image_count': len(image_paths)
            }

        except Exception as e:
            print(f"   ❌ Failed to post carousel: {e}")
            return None

    def verify_post(self, media_code):
        """Verify a post exists"""
        try:
            media = self.client.media_info_by_shortcode(media_code)
            return media is not None
        except:
            return False
