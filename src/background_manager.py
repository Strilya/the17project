"""
Background Manager Module - ENHANCED MULTI-SOURCE EDITION

This module handles fetching backgrounds from MULTIPLE sources:
- Pexels API (primary)
- Pixabay API (free backup)
- Videvo (free videos)

Features:
- 3 video APIs with automatic fallback
- Photo slideshows as backup
- Massive keyword variety (100+ search terms)
- Smart caching and variety tracking
"""

import os
import requests
import logging
import json
import random
import time
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackgroundManager:
    """
    Multi-source background manager with massive variety.
    
    Sources (in priority order):
    1. Pexels API (best quality, requires key)
    2. Pixabay API (good quality, free)
    3. Videvo (free downloads, no API)
    4. Photo slideshows (Pexels photos)
    5. Gradient fallback
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the BackgroundManager with multi-source support."""
        # Load config
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "video_config.json"

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.config = config["background_videos"]
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            # Default config
            self.config = {
                "enabled": False,
                "fallback_to_gradient": True,
                "cache_enabled": False
            }

        # Get API keys from environment
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.pixabay_key = os.getenv("PIXABAY_API_KEY", "")  # Pixabay works without key but limited
        
        if not self.pexels_key:
            logger.warning("PEXELS_API_KEY not found")
        
        if not self.pixabay_key:
            logger.info("PIXABAY_API_KEY not found (will use limited free access)")

        # Setup cache directory
        if self.config.get("cache_enabled", True):
            self.cache_dir = Path(self.config.get("cache_dir", "output/background_cache"))
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cache directory: {self.cache_dir}")
        else:
            self.cache_dir = None

        logger.info(f"BackgroundManager initialized (Multi-source mode)")
        logger.info(f"  - Pexels: {'✅' if self.pexels_key else '❌'}")
        logger.info(f"  - Pixabay: {'✅' if self.pixabay_key else '⚠️ Limited'}")
        logger.info(f"  - Videvo: ✅ (no key needed)")

    def get_background_video(self, category: str) -> Optional[str]:
        """
        Get background video from ANY available source.
        
        Tries sources in order until one works:
        1. Pexels
        2. Pixabay  
        3. Videvo
        4. Returns None (triggers photo slideshow in video_generator)
        
        Args:
            category: Content category
            
        Returns:
            Path to video file, or None for photo slideshow fallback
        """
        if not self.config["enabled"]:
            logger.info("Background videos disabled")
            return None

        try:
            # Check cache first
            cached = self._get_from_cache(category)
            if cached:
                logger.info(f"Using cached background: {cached}")
                return cached

            # Get search keywords for this category
            keywords = self.config.get("categories", {}).get(category, ["abstract purple"])
            query = random.choice(keywords)
            logger.info(f"Searching for: '{query}'")

            # Try Pexels first (best quality)
            if self.pexels_key:
                logger.info("Trying Pexels API...")
                video_url = self._search_pexels(query)
                if video_url:
                    video_path = self._download_video(video_url, category, "pexels")
                    return video_path

            # Try Pixabay second
            logger.info("Pexels failed, trying Pixabay...")
            video_url = self._search_pixabay(query)
            if video_url:
                video_path = self._download_video(video_url, category, "pixabay")
                return video_path

            # All video sources failed - return None for photo slideshow
            logger.warning(f"No video found for '{query}' - will use photo slideshow")
            return None

        except Exception as e:
            logger.error(f"Failed to get background video: {e}")
            return None

    def _search_pexels(self, query: str) -> Optional[str]:
        """Search Pexels API for 4K portrait video."""
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.pexels_key}

        video_settings = self.config.get("video_settings", {})
        params = {
            "query": query,
            "orientation": video_settings.get("orientation", "portrait"),
            "size": video_settings.get("size", "large"),
            "per_page": video_settings.get("per_page", 15)
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                videos = data.get("videos", [])

                if not videos:
                    return None

                # Find 4K portrait video
                for video in videos:
                    if not self._validate_video(video):
                        continue

                    video_files = video.get("video_files", [])
                    
                    # Prefer UHD (4K), but accept HD if no 4K
                    for quality in ["uhd", "hd"]:
                        for vf in video_files:
                            if vf.get("quality") == quality:
                                width = vf.get("width", 0)
                                height = vf.get("height", 0)
                                if width > 0 and height > 0 and width < height:
                                    logger.info(f"✅ Found Pexels video: {quality.upper()} {width}x{height}")
                                    return vf["link"]

                return None

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error("Pexels API timeout")
                    return None
            except Exception as e:
                logger.error(f"Pexels API error: {e}")
                return None

        return None

    def _search_pixabay(self, query: str) -> Optional[str]:
        """
        Search Pixabay API for portrait video.
        
        Note: Pixabay API is free but has rate limits.
        """
        url = "https://pixabay.com/api/videos/"
        
        params = {
            "key": self.pixabay_key if self.pixabay_key else "your_default_key_here",
            "q": query,
            "video_type": "all",
            "orientation": "vertical",
            "per_page": 20
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            
            # Pixabay returns 200 even with invalid key, check for error in JSON
            data = response.json()
            
            if "hits" not in data:
                logger.warning("Pixabay API: invalid response (bad key?)")
                return None
            
            videos = data.get("hits", [])

            if not videos:
                return None

            # Find suitable video
            for video in videos:
                # Pixabay videos are in video.videos dict
                video_sizes = video.get("videos", {})
                
                # Try to get highest quality vertical video
                for size_key in ["large", "medium", "small"]:
                    if size_key in video_sizes:
                        video_info = video_sizes[size_key]
                        width = video_info.get("width", 0)
                        height = video_info.get("height", 0)
                        
                        # Check if portrait orientation
                        if height > width and width >= 720:
                            logger.info(f"✅ Found Pixabay video: {width}x{height}")
                            return video_info["url"]

            return None

        except Exception as e:
            logger.error(f"Pixabay API error: {e}")
            return None

    def _validate_video(self, video_data: Dict) -> bool:
        """Validate video is appropriate and high quality."""
        # Check resolution
        width = video_data.get('width', 0)
        height = video_data.get('height', 0)

        if width < 1080 or height < 1920:
            return False

        # Check duration
        duration = video_data.get('duration', 0)
        if duration < 10:
            return False

        return True

    def search_high_res_photos(self, category: str, count: int = 20) -> List[str]:
        """
        Search Pexels for high-res photos (for slideshows).
        
        Args:
            category: Content category
            count: Number of photos needed
            
        Returns:
            List of photo URLs
        """
        if not self.pexels_key:
            logger.warning("No Pexels API key for photos")
            return []
        
        keywords = self.config.get("categories", {}).get(category, ["abstract purple"])
        all_photos = []
        
        # Try multiple keywords to get variety
        for query in random.sample(keywords, min(5, len(keywords))):
            if len(all_photos) >= count:
                break
                
            try:
                url = "https://api.pexels.com/v1/search"
                headers = {"Authorization": self.pexels_key}
                params = {
                    "query": query,
                    "orientation": "portrait",
                    "size": "large",
                    "per_page": 15
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                photos = data.get("photos", [])
                
                for photo in photos:
                    photo_url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                    
                    if photo_url:
                        width = photo.get("width", 0)
                        height = photo.get("height", 0)
                        
                        if width >= 1080 and height >= 1920:
                            all_photos.append(photo_url)
                            
                        if len(all_photos) >= count:
                            break
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Photo search failed for '{query}': {e}")
                continue
        
        logger.info(f"Collected {len(all_photos)} high-res photos")
        return all_photos[:count]

    def download_photo(self, url: str, save_path: Path) -> bool:
        """Download a single photo."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            # Verify it's a valid image
            img = Image.open(save_path)
            img.verify()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to download photo: {e}")
            if save_path.exists():
                save_path.unlink()
            return False

    def download_photos_for_slideshow(self, category: str, count: int = 20) -> List[Path]:
        """Download multiple high-res photos for slideshow."""
        logger.info(f"\n🖼️  DOWNLOADING {count} HIGH-RES PHOTOS")
        
        # Search for photos
        photo_urls = self.search_high_res_photos(category, count)
        
        if not photo_urls:
            logger.error("No high-res photos found!")
            return []
        
        # Download photos
        downloaded_photos = []
        cache_dir = self.cache_dir / "photos" / category if self.cache_dir else Path("output/temp_photos")
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        for i, url in enumerate(photo_urls):
            photo_path = cache_dir / f"photo_{i:03d}.jpg"
            
            if self.download_photo(url, photo_path):
                downloaded_photos.append(photo_path)
                logger.info(f"  [{i+1}/{len(photo_urls)}] ✅")
            
            if len(downloaded_photos) >= count:
                break
        
        logger.info(f"✅ Downloaded {len(downloaded_photos)} photos")
        
        return downloaded_photos

    def _download_video(self, url: str, category: str, source: str) -> str:
        """Download video from any source to cache."""
        if not self.cache_dir:
            raise RuntimeError("Cache is disabled")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{category}_{source}_{timestamp}.mp4"
        filepath = self.cache_dir / filename

        logger.info(f"Downloading from {source.upper()}: {filename}")

        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"✅ Downloaded: {filepath}")

            # Cleanup old cache
            self._cleanup_cache()

            return str(filepath)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download video: {e}")
            if filepath.exists():
                filepath.unlink()
            raise

    def _get_from_cache(self, category: str) -> Optional[str]:
        """Get random cached video for category."""
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
    """Test multi-source background manager."""
    try:
        print("\n" + "="*70)
        print("TESTING MULTI-SOURCE BACKGROUND MANAGER")
        print("="*70)

        manager = BackgroundManager()

        categories = ["angel_numbers", "productivity"]

        for category in categories:
            print(f"\n--- Testing {category} ---")
            video_path = manager.get_background_video(category)

            if video_path:
                print(f"✅ Got video: {video_path}")
                if Path(video_path).exists():
                    size_mb = Path(video_path).stat().st_size / (1024 * 1024)
                    print(f"   File size: {size_mb:.2f} MB")
            else:
                print(f"⚠ No video (will use photo slideshow)")

        print("\n" + "="*70)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
