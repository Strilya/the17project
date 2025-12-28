"""
Multi-source video fetcher - Pexels + Pixabay
Grabs 2-3 clips from each source for montage
"""

import os
import requests
import random

class VideoSourceManager:
    def __init__(self):
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        self.pixabay_key = os.getenv('PIXABAY_API_KEY')
        
    def fetch_multiple_videos(self, query, count=4):
        """Fetch multiple video URLs from different sources"""
        
        videos = []
        
        # Try Pexels (get 2)
        pexels_videos = self._fetch_pexels_multiple(query, 2)
        videos.extend(pexels_videos)
        
        # Try Pixabay (get 2)
        pixabay_videos = self._fetch_pixabay_multiple(query, 2)
        videos.extend(pixabay_videos)
        
        # Shuffle and return up to count
        random.shuffle(videos)
        return videos[:count]
    
    def _fetch_pexels_multiple(self, query, count):
        """Get multiple videos from Pexels with safe content filtering"""
        videos = []

        try:
            url = "https://api.pexels.com/videos/search"
            headers = {"Authorization": self.pexels_key}
            # Add safe content filtering
            params = {
                "query": query,
                "orientation": "portrait",
                "per_page": 20,
                "size": "large"  # Get high quality videos
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            results = response.json().get('videos', [])
            
            for video in results[:count]:
                for file in video.get('video_files', []):
                    if file.get('link'):
                        videos.append({
                            'url': file.get('link'),
                            'source': 'Pexels',
                            'id': video.get('id')
                        })
                        break
                
                if len(videos) >= count:
                    break
            
            if videos:
                print(f"   ✅ Pexels: {len(videos)} clips")
        except Exception as e:
            print(f"   ⚠️  Pexels failed: {e}")
        
        return videos
    
    def _fetch_pixabay_multiple(self, query, count):
        """Get multiple videos from Pixabay"""
        videos = []
        
        try:
            url = "https://pixabay.com/api/videos/"
            params = {
                "key": self.pixabay_key,
                "q": query,
                "video_type": "film",
                "orientation": "vertical",
                "per_page": 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            results = response.json().get('hits', [])
            
            for video in results[:count]:
                video_files = video.get('videos', {})
                # Try to get medium or large size
                for size in ['medium', 'large', 'small']:
                    if size in video_files and 'url' in video_files[size]:
                        videos.append({
                            'url': video_files[size]['url'],
                            'source': 'Pixabay',
                            'id': video.get('id')
                        })
                        break
                
                if len(videos) >= count:
                    break
            
            if videos:
                print(f"   ✅ Pixabay: {len(videos)} clips")
        except Exception as e:
            print(f"   ⚠️  Pixabay failed: {e}")
        
        return videos

