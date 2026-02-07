"""
Instagram Poster - Session-Based (NO LOGIN)
============================================

Uses pre-saved session from login_instagram.py
NO API login calls - just loads saved session and posts

Session lasts ~90 days, refresh when it expires
"""

from instagrapi import Client
import os
from dotenv import load_dotenv

load_dotenv()


class InstagramPoster:
    """Instagram poster that uses pre-saved session - NO LOGIN"""

    def __init__(self):
        """Initialize with saved session - NO LOGIN"""
        self.client = Client()
        self.session_file = "config/instagram_session.json"
        self._load_session()

    def _load_session(self):
        """Load pre-saved session - DO NOT LOGIN"""
        if os.path.exists(self.session_file):
            print("   📱 Loading Instagram session...")
            self.client.load_settings(self.session_file)
            print("   ✅ Session loaded")
        else:
            raise Exception(f"❌ Session file not found: {self.session_file}")

    def post_reel(self, video_path, caption, thumbnail_path=None):
        """
        Post a reel to Instagram

        Args:
            video_path: Path to video file
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
