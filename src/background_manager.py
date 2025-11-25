"""
Background Manager Module

This module handles fetching and caching video backgrounds from Pexels API
for Instagram Reels. It provides dynamic, engaging video backgrounds that
match each content category's theme.

Main functionality:
- Search Pexels API for category-specific video backgrounds
- Download and cache videos locally
- Manage cache size and cleanup
- Fallback to gradient backgrounds if API is unavailable
"""

import os
import requests
import logging
import json
import random
import time
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackgroundManager:
    """
    Manages video backgrounds from Pexels API with caching.

    This class handles:
    1. Searching Pexels for category-specific videos
    2. Downloading videos to local cache
    3. Managing cache size and cleanup
    4. Providing fallback to gradients if API fails
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the BackgroundManager.

        Args:
            config_path: Path to video_config.json file
        """
        # Load config
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "video_config.json"

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.config = config["background_videos"]
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # Default config with backgrounds disabled
            self.config = {
                "enabled": False,
                "fallback_to_gradient": True,
                "cache_enabled": False
            }

        # Get API key from environment
        self.api_key = os.getenv("PEXELS_API_KEY")

        if not self.api_key:
            logger.warning("PEXELS_API_KEY not found, will use gradient fallback")
            self.config["enabled"] = False

        # Setup cache directory
        if self.config.get("cache_enabled", True):
            self.cache_dir = Path(self.config.get("cache_dir", "output/background_cache"))
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cache directory: {self.cache_dir}")
        else:
            self.cache_dir = None

        logger.info(f"BackgroundManager initialized (enabled: {self.config['enabled']})")

    def get_background_video(self, category: str) -> Optional[str]:
        """
        Get background video for category, returns path or None.

        Args:
            category: Content category (angel_numbers, productivity, etc.)

        Returns:
            Path to video file, or None if fallback to gradient
        """
        if not self.config["enabled"]:
            logger.info("Background videos disabled, using gradient fallback")
            return None

        try:
            # Check cache first
            cached = self._get_from_cache(category)
            if cached:
                logger.info(f"Using cached background: {cached}")
                return cached

            # Search Pexels
            keywords = self.config.get("categories", {}).get(category, ["abstract purple"])
            query = random.choice(keywords)
            logger.info(f"Searching Pexels for: {query}")

            video_url = self._search_pexels(query)
            if not video_url:
                logger.warning(f"No video found for query: {query}")
                return None

            # Download video
            video_path = self._download_video(video_url, category)
            return video_path

        except Exception as e:
            logger.error(f"Failed to get background video: {e}")
            if self.config.get("fallback_to_gradient", True):
                logger.info("Falling back to gradient background")
                return None
            raise

    def _search_pexels(self, query: str) -> Optional[str]:
        """
        Search Pexels API for video with retry logic.

        Args:
            query: Search query string

        Returns:
            Direct URL to video file, or None if not found
        """
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.api_key}

        video_settings = self.config.get("video_settings", {})
        params = {
            "query": query,
            "orientation": video_settings.get("orientation", "portrait"),
            "size": video_settings.get("size", "large"),
            "per_page": video_settings.get("per_page", 10)
        }

        # Retry logic: 3 attempts with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Increased timeout from 10s to 30s to handle slow API responses
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                videos = data.get("videos", [])

                if not videos:
                    logger.warning(f"No videos found for query: {query}")
                    return None

                # Find first VALIDATED HD video (no people/activities)
                for video in videos:
                    if not self._validate_video(video):
                        logger.debug(f"Skipping video: failed validation")
                        continue

                    video_files = video.get("video_files", [])

                    # Find HD portrait video (width < height)
                    for vf in video_files:
                        if vf.get("quality") == "hd":
                            width = vf.get("width", 0)
                            height = vf.get("height", 0)
                            if width > 0 and height > 0 and width < height:
                                logger.info(f"✅ Found validated HD portrait video: {width}x{height}")
                                return vf["link"]

                    # Fallback to any portrait video for this validated result
                    for vf in video_files:
                        width = vf.get("width", 0)
                        height = vf.get("height", 0)
                        if width > 0 and height > 0 and width < height:
                            logger.info(f"Found validated portrait video: {width}x{height}")
                            return vf["link"]

                logger.warning("No validated portrait videos found")
                return None

            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"Pexels API timeout (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Pexels API timeout after {max_retries} attempts: {e}")
                    return None
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)
                    logger.warning(f"Pexels API request error (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Pexels API request error after {max_retries} attempts: {e}")
                    return None
            except Exception as e:
                logger.error(f"Pexels API error: {e}")
                return None

        return None

    def _validate_video(self, video_data: Dict) -> bool:
        """
        Validate video is appropriate for spiritual content (no people/activities).

        Args:
            video_data: Video metadata from Pexels API

        Returns:
            True if video is valid, False otherwise
        """
        # Check resolution - must be HD minimum
        width = video_data.get('width', 0)
        height = video_data.get('height', 0)

        if width < 1080 or height < 1920:
            logger.debug(f"Rejected: resolution too low ({width}x{height})")
            return False

        # Check duration - prefer longer clips (minimum 10s)
        duration = video_data.get('duration', 0)
        if duration < 10:
            logger.debug(f"Rejected: duration too short ({duration}s)")
            return False

        # Check tags for red flag keywords (people/activities)
        tags_str = ' '.join([tag.lower() for tag in video_data.get('tags', [])])
        url_str = video_data.get('url', '').lower()
        combined = f"{tags_str} {url_str}"

        # Reject if contains people-related keywords
        bad_keywords = [
            'person', 'man', 'woman', 'people', 'guy', 'girl', 'face', 'body',
            'human', 'hand', 'hands', 'portrait', 'selfie', 'model', 'male', 'female',
            'boy', 'child', 'adult', 'crowd', 'group', 'team', 'yoga', 'exercise',
            'workout', 'dance', 'running', 'walking', 'sitting', 'standing',
            'athlete', 'player', 'sport', 'fitness', 'gym', 'training', 'jogging',
            'hiking', 'climbing', 'cycling', 'swimming', 'surfing', 'skiing',
            'street', 'city', 'urban', 'tourist', 'travel', 'vacation', 'crowd',
            'festival', 'concert', 'party', 'celebration', 'wedding', 'event',
            'restaurant', 'cafe', 'bar', 'club', 'shopping', 'market', 'store'
        ]

        for keyword in bad_keywords:
            if keyword in combined:
                logger.debug(f"Rejected: contains keyword '{keyword}'")
                return False

        logger.debug("Video passed validation")
        return True

    def _download_video(self, url: str, category: str) -> str:
        """
        Download video to cache.

        Args:
            url: Direct URL to video file
            category: Content category for naming

        Returns:
            Path to downloaded video file
        """
        if not self.cache_dir:
            raise RuntimeError("Cache is disabled")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{category}_{timestamp}.mp4"
        filepath = self.cache_dir / filename

        logger.info(f"Downloading video from Pexels: {filename}")

        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Downloaded background video: {filepath}")

            # Cleanup old cache files
            self._cleanup_cache()

            return str(filepath)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download video: {e}")
            if filepath.exists():
                filepath.unlink()
            raise

    def _get_from_cache(self, category: str) -> Optional[str]:
        """
        Get random cached video for category.

        Args:
            category: Content category

        Returns:
            Path to cached video, or None if no cache available
        """
        if not self.config.get("cache_enabled", True) or not self.cache_dir:
            return None

        try:
            cached_files = list(self.cache_dir.glob(f"{category}_*.mp4"))
            if cached_files:
                selected = random.choice(cached_files)
                logger.info(f"Found {len(cached_files)} cached videos for {category}")
                return str(selected)
        except Exception as e:
            logger.error(f"Error accessing cache: {e}")

        return None

    def _cleanup_cache(self):
        """Remove old videos if cache is too large."""
        if not self.cache_dir:
            return

        try:
            max_size = self.config.get("max_cache_size", 50)
            cached_files = sorted(
                self.cache_dir.glob("*.mp4"),
                key=lambda x: x.stat().st_mtime
            )

            if len(cached_files) > max_size:
                files_to_remove = cached_files[:-max_size]
                for old_file in files_to_remove:
                    old_file.unlink()
                    logger.info(f"Removed old cache file: {old_file.name}")

                logger.info(f"Cache cleanup: removed {len(files_to_remove)} old files")

        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")


def main():
    """
    Main function for testing BackgroundManager locally.

    Usage:
        python src/background_manager.py
    """
    try:
        print("\n" + "="*70)
        print("TESTING BACKGROUND MANAGER")
        print("="*70)

        # Initialize manager
        manager = BackgroundManager()

        # Test each category
        categories = ["angel_numbers", "productivity", "manifestation", "spiritual_growth"]

        for category in categories:
            print(f"\n--- Testing {category} ---")
            video_path = manager.get_background_video(category)

            if video_path:
                print(f"✅ Got video: {video_path}")
                # Check file exists and has size
                if Path(video_path).exists():
                    size_mb = Path(video_path).stat().st_size / (1024 * 1024)
                    print(f"   File size: {size_mb:.2f} MB")
                else:
                    print(f"❌ File does not exist!")
            else:
                print(f"⚠ No video (using gradient fallback)")

        print("\n" + "="*70)
        print("BACKGROUND MANAGER TEST COMPLETE")
        print("="*70)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
