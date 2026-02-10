"""
Instagram Poster - Dead Simple Session-Based Upload
====================================================

Loads pre-saved session and posts. No login. No fallback. No cleverness.

If session is missing or expired: FAIL FAST and exit.
Regenerate session manually with login_instagram.py when needed.
"""

from instagrapi import Client
import os


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
        """Post a reel to Instagram"""
        try:
            if not os.path.exists(video_path):
                raise Exception(f"Video not found: {video_path}")

            file_size = os.path.getsize(video_path) / (1024 * 1024)
            print(f"   📤 Uploading reel to Instagram...")
            print(f"      Video: {video_path}")
            print(f"      Size: {file_size:.2f} MB")
            print(f"      Caption: {len(caption)} chars")

            media = self.client.clip_upload(
                path=video_path,
                caption=caption,
                thumbnail=thumbnail_path
            )

            url = f"https://www.instagram.com/p/{media.code}/"
            print(f"   ✅ Reel posted successfully!")
            print(f"      URL: {url}")

            return {
                'media_id': media.id,
                'code': media.code,
                'url': url,
            }

        except Exception as e:
            print(f"   ❌ Failed to post reel: {e}")
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
