"""
Video Generator - Creates high-quality reels
"""

import os
import requests
try:
    import moviepy
    from moviepy import editor as mpy
    print(f"MoviePy version: {moviepy.__version__}")
except ImportError as e:
    print(f"MoviePy import error: {e}")
    mpy = None

from PIL import Image, ImageDraw, ImageFont

class VideoGenerator:
    def __init__(self):
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def fetch_background_video(self, query):
        """Fetch high-quality background video from Pexels"""
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.pexels_key}
        params = {
            "query": query,
            "orientation": "portrait",
            "size": "large",
            "per_page": 15
        }
        
        response = requests.get(url, headers=headers, params=params)
        videos = response.json().get('videos', [])
        
        if not videos:
            print(f"⚠️  No videos found for query: {query}")
            return None
        
        for video in videos:
            for file in video.get('video_files', []):
                if file.get('quality') == 'hd':
                    return file.get('link')
        
        return None
    
    def download_video(self, url, output_path):
        """Download video from URL"""
        response = requests.get(url, stream=True)
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Video downloaded: {output_path}")
        return output_path

