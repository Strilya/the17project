"""
Instagram Poster - Dead Simple Session-Based Upload
====================================================

Loads pre-saved session and posts. No login. No fallback. No cleverness.

If session is missing or expired: FAIL FAST and exit.
Regenerate session manually with login_instagram.py when needed.
"""

from instagrapi import Client
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstagramPoster:
    def __init__(self):
        self.client = Client()
        self.session_file = 'config/instagram_session.json'

        # Load session or fail
        if not os.path.exists(self.session_file):
            raise Exception(f"❌ Session file not found: {self.session_file}")

        print("   📱 Loading Instagram session...")
        self.client.load_settings(self.session_file)
        print("   ✅ Session loaded")

    def post_reel(self, video_path, caption, thumbnail_path=None):
        """Post a reel to Instagram with retry logic and validation"""

        # Pre-upload validation
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file does not exist: {video_path}")
                raise Exception(f"Video not found: {video_path}")

            file_size_bytes = os.path.getsize(video_path)
            if file_size_bytes == 0:
                logger.error(f"Video file is empty: {video_path}")
                raise Exception(f"Video file is empty: {video_path}")

            # Check if file is readable
            with open(video_path, 'rb') as f:
                f.read(1)

            file_size_mb = file_size_bytes / (1024 * 1024)
            print(f"   📤 Uploading reel to Instagram...")
            print(f"      Video: {video_path}")
            print(f"      Size: {file_size_mb:.2f} MB ({file_size_bytes} bytes)")
            print(f"      Caption: {len(caption)} chars")
            logger.info(f"Pre-upload validation passed for {video_path}")

        except Exception as e:
            logger.error(f"Pre-upload validation failed: {repr(e)}")
            print(f"   ❌ Pre-upload validation failed: {e}")
            return None

        # Retry logic - max 3 attempts with 30 second delay
        max_attempts = 3
        retry_delay = 30

        for attempt in range(1, max_attempts + 1):
            try:
                print(f"   🔄 Upload attempt {attempt}/{max_attempts}...")
                logger.info(f"Starting upload attempt {attempt}/{max_attempts}")

                # Use video_upload instead of clip_upload
                media = self.client.video_upload(
                    path=video_path,
                    caption=caption
                )

                if media is None:
                    raise Exception("Upload returned None - no media object created")

                url = f"https://www.instagram.com/p/{media.code}/"
                print(f"   ✅ Reel posted successfully!")
                print(f"      URL: {url}")
                logger.info(f"Upload successful on attempt {attempt}: {url}")

                return {
                    'media_id': media.id,
                    'code': media.code,
                    'url': url,
                }

            except Exception as e:
                logger.error(f"Upload attempt {attempt}/{max_attempts} failed")
                logger.error(f"Full error: {repr(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                if hasattr(e, '__dict__'):
                    logger.error(f"Error attributes: {e.__dict__}")

                print(f"   ❌ Attempt {attempt}/{max_attempts} failed: {e}")

                # If this was the last attempt, give up
                if attempt >= max_attempts:
                    print(f"   ❌ All {max_attempts} attempts failed")
                    logger.error(f"All {max_attempts} upload attempts failed for {video_path}")
                    return None

                # Wait before retrying
                print(f"   ⏳ Waiting {retry_delay} seconds before retry...")
                logger.info(f"Waiting {retry_delay} seconds before attempt {attempt + 1}")
                time.sleep(retry_delay)

        return None

    def post_carousel(self, image_paths, caption):
        """Post a carousel to Instagram"""
        try:
            if len(image_paths) < 2:
                print(f"   ❌ Carousel requires at least 2 images, got {len(image_paths)}")
                return None

            if len(image_paths) > 10:
                print(f"   ⚠️  Instagram allows max 10 images, truncating to 10")
                image_paths = image_paths[:10]

            print(f"   📤 Uploading carousel to Instagram...")
            print(f"      Images: {len(image_paths)}")
            print(f"      Caption: {len(caption)} chars")

            for img_path in image_paths:
                if not os.path.exists(img_path):
                    raise Exception(f"Image not found: {img_path}")

            media = self.client.album_upload(
                paths=image_paths,
                caption=caption
            )

            url = f"https://www.instagram.com/p/{media.code}/"
            print(f"   ✅ Carousel posted successfully!")
            print(f"      URL: {url}")

            return {
                'media_id': media.id,
                'code': media.code,
                'url': url,
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
