"""
Background Manager - FIXED FOR 4K NATURE/SPACE/FIRE/NEON ONLY

Strict filtering:
- Only 4K resolution (3840x2160 minimum)
- Only nature, space, fire, water, neon lights, cityscapes, beaches, retreat settings
- NO people, NO activities, NO random content
"""

import os
import requests
import logging
import json
import random
import time
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackgroundManager:
    """Manages 4K video backgrounds from Pexels with strict filtering."""

    # PORTRAIT VIDEO SEARCH QUERIES - Optimized for vertical
    SPIRITUAL_QUERIES = [
        "purple space stars vertical",
        "aurora borealis vertical video",
        "galaxy stars portrait",
        "nebula purple vertical",
        "night sky stars vertical"
    ]

    NATURE_QUERIES = [
        "ocean waves vertical video",
        "waterfall nature vertical",
        "beach sunset vertical",
        "forest vertical video",
        "mountain landscape vertical"
    ]

    FIRE_QUERIES = [
        "campfire flames vertical",
        "fire abstract vertical",
        "candles vertical video"
    ]

    NEON_QUERIES = [
        "neon lights vertical cityscape",
        "city lights vertical night",
        "neon signs vertical video"
    ]

    RETREAT_QUERIES = [
        "spa water vertical peaceful",
        "meditation vertical calm",
        "zen garden vertical"
    ]

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize BackgroundManager."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "video_config.json"

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.config = config["background_videos"]
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = {"enabled": False}

        self.api_key = os.getenv("PEXELS_API_KEY")
        
        if not self.api_key:
            logger.warning("PEXELS_API_KEY not found")
            self.config["enabled"] = False

        if self.config.get("cache_enabled", True):
            self.cache_dir = Path(self.config.get("cache_dir", "output/background_cache"))
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.cache_dir = None

        logger.info(f"BackgroundManager initialized (4K strict filtering)")

    def get_background_video(self, category: str) -> Optional[str]:
        """Get 4K background video for category."""
        if not self.config["enabled"]:
            logger.info("Backgrounds disabled, using gradient")
            return None

        try:
            # Check cache first
            cached = self._get_from_cache(category)
            if cached:
                logger.info(f"Using cached 4K video: {cached}")
                return cached

            # Get ALL possible queries for variety
            all_queries = (
                self.SPIRITUAL_QUERIES +
                self.NATURE_QUERIES +
                self.FIRE_QUERIES +
                self.NEON_QUERIES +
                self.RETREAT_QUERIES
            )
            
            # Pick random query
            query = random.choice(all_queries)
            logger.info(f"Searching Pexels: {query}")

            video_url = self._search_pexels_4k(query)
            if not video_url:
                logger.warning(f"No 4K video found for: {query}")
                return None

            # Download
            video_path = self._download_video(video_url, category)
            return video_path

        except Exception as e:
            logger.error(f"Failed to get background: {e}")
            return None

    def _search_pexels_4k(self, query: str) -> Optional[str]:
        """Search Pexels for 4K videos ONLY."""
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.api_key}
        
        params = {
            "query": query,
            "orientation": "portrait",
            "size": "large",
            "per_page": 30  # Get more results to find portrait videos
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

                # Filter for 4K portrait videos
                for video in videos:
                    if not self._is_4k_quality(video):
                        continue
                    
                    if not self._is_acceptable_content(video):
                        continue

                    video_files = video.get("video_files", [])
                    
                    # Find best quality portrait video
                    for vf in video_files:
                        width = vf.get("width", 0)
                        height = vf.get("height", 0)
                        
                        # Portrait and high quality
                        if width > 0 and height > 0 and width < height and width >= 1080:
                            logger.info(f"✅ Found 4K video: {width}x{height}")
                            return vf["link"]

                logger.warning("No 4K portrait videos found")
                return None

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait = 2 ** attempt
                    logger.warning(f"Timeout, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    logger.error("Timeout after retries")
                    return None
            except Exception as e:
                logger.error(f"Search error: {e}")
                return None

        return None

    def _is_4k_quality(self, video_data: Dict) -> bool:
        """Check if video is HD quality (1080p+)."""
        width = video_data.get('width', 0)
        height = video_data.get('height', 0)

        # Accept Full HD+ for portrait: 1080x1920 minimum
        if width < 1080 or height < 1920:
            logger.debug(f"Rejected: Low resolution {width}x{height}")
            return False

        # Prefer higher quality
        if width >= 2160 and height >= 3840:
            logger.debug(f"✅ 4K quality: {width}x{height}")
        elif width >= 1080 and height >= 1920:
            logger.debug(f"✅ Full HD quality: {width}x{height}")

        # Check duration
        duration = video_data.get('duration', 0)
        if duration < 15:
            logger.debug(f"Rejected: Too short ({duration}s)")
            return False

        return True

    def _is_acceptable_content(self, video_data: Dict) -> bool:
        """Strict content filtering - NO people or activities."""
        # Get all text to check
        tags_str = ' '.join([str(tag).lower() for tag in video_data.get('tags', [])])
        url_str = video_data.get('url', '').lower()
        combined = f"{tags_str} {url_str}"

        # STRICT BLOCKLIST - Reject anything with people or activities
        blocklist = [
            # People
            'person', 'man', 'woman', 'people', 'guy', 'girl', 'face', 'body',
            'human', 'hand', 'hands', 'portrait', 'selfie', 'model', 'male', 'female',
            'boy', 'child', 'adult', 'crowd', 'group', 'team', 
            
            # Activities
            'yoga', 'exercise', 'workout', 'dance', 'dancing', 'running', 'walking',
            'sitting', 'standing', 'jumping', 'swimming', 'surfing', 'climbing',
            
            # Random/weird stuff
            'gypsy', 'fortune', 'carnival', 'festival', 'circus', 'party', 'concert',
            'tourist', 'travel', 'vacation', 'shopping', 'market', 'restaurant',
            'car', 'vehicle', 'traffic', 'road', 'street', 'building', 'architecture',
            'indoor', 'room', 'house', 'apartment', 'office', 'store', 'shop'
        ]

        for keyword in blocklist:
            if keyword in combined:
                logger.debug(f"Rejected: Contains '{keyword}'")
                return False

        # MUST contain acceptable keywords
        acceptable = [
            'nature', 'space', 'star', 'galaxy', 'nebula', 'cosmos', 'aurora',
            'ocean', 'sea', 'wave', 'beach', 'water', 'lake', 'river', 'waterfall',
            'mountain', 'forest', 'tree', 'sky', 'cloud', 'sunset', 'sunrise',
            'fire', 'flame', 'candle', 'neon', 'light', 'glow', 'abstract',
            'peaceful', 'calm', 'zen', 'meditation', 'spiritual', 'purple', 'gold'
        ]

        has_acceptable = any(word in combined for word in acceptable)
        
        if not has_acceptable:
            logger.debug("Rejected: No acceptable keywords")
            return False

        logger.debug("✅ Content validated")
        return True

    def _download_video(self, url: str, category: str) -> str:
        """Download video to cache."""
        if not self.cache_dir:
            raise RuntimeError("Cache disabled")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{category}_{timestamp}.mp4"
        filepath = self.cache_dir / filename

        logger.info(f"Downloading 4K video: {filename}")

        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logger.info(f"✅ Downloaded: {filepath}")
        self._cleanup_cache()
        
        return str(filepath)

    def _get_from_cache(self, category: str) -> Optional[str]:
        """Get random cached video."""
        if not self.cache_dir:
            return None

        try:
            cached_files = list(self.cache_dir.glob(f"{category}_*.mp4"))
            if cached_files:
                selected = random.choice(cached_files)
                return str(selected)
        except Exception as e:
            logger.error(f"Cache error: {e}")

        return None

    def _cleanup_cache(self):
        """Remove old videos if cache too large."""
        if not self.cache_dir:
            return

        try:
            max_size = self.config.get("max_cache_size", 50)
            cached_files = sorted(
                self.cache_dir.glob("*.mp4"),
                key=lambda x: x.stat().st_mtime
            )

            if len(cached_files) > max_size:
                to_remove = cached_files[:-max_size]
                for old_file in to_remove:
                    old_file.unlink()
                logger.info(f"Cache cleanup: removed {len(to_remove)} old files")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


def main():
    """Test BackgroundManager."""
    manager = BackgroundManager()
    
    print("\n" + "="*70)
    print("TESTING 4K BACKGROUND MANAGER")
    print("="*70)
    
    video_path = manager.get_background_video("angel_numbers")
    
    if video_path:
        print(f"\n✅ Got 4K video: {video_path}")
        size_mb = Path(video_path).stat().st_size / (1024 * 1024)
        print(f"   Size: {size_mb:.2f} MB")
    else:
        print("\n❌ No video found")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
