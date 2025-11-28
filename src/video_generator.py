"""
Video Generator - EXTREME VARIETY EDITION

Features:
- 5 COMPLETELY DIFFERENT visual styles that rotate
- Smart history tracking (never repeats recent styles/backgrounds)
- Dynamic text positioning (top/center/bottom)
- Multiple font families (sans-serif, serif, bold)
- Diverse color palettes per style
- Smart contrast detection
- 50+ background video searches per category

NO MORE REPETITION!
"""

import os
import json
import logging
import random
import hashlib
from datetime import datetime
from typing import Dict, Optional, Tuple, List
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import numpy as np

try:
    from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, VideoFileClip, concatenate_videoclips
except ImportError:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, VideoFileClip, concatenate_videoclips

from pydub import AudioSegment
from background_manager import BackgroundManager
from audio_generator import AudioGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StyleHistory:
    """Track used styles and backgrounds to avoid repetition."""
    
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.load()
    
    def load(self):
        """Load history from file."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                self.recent_styles = data.get('recent_styles', [])
                self.recent_backgrounds = data.get('recent_backgrounds', [])
        else:
            self.recent_styles = []
            self.recent_backgrounds = []
    
    def save(self):
        """Save history to file."""
        with open(self.state_file, 'w') as f:
            json.dump({
                'recent_styles': self.recent_styles,
                'recent_backgrounds': self.recent_backgrounds
            }, f, indent=2)
    
    def add_style(self, style_name: str, max_history: int = 2):
        """Add style to history, keeping only last N."""
        if style_name in self.recent_styles:
            self.recent_styles.remove(style_name)
        self.recent_styles.insert(0, style_name)
        self.recent_styles = self.recent_styles[:max_history]
        self.save()
    
    def add_background(self, bg_hash: str, max_history: int = 5):
        """Add background to history, keeping only last N."""
        if bg_hash in self.recent_backgrounds:
            self.recent_backgrounds.remove(bg_hash)
        self.recent_backgrounds.insert(0, bg_hash)
        self.recent_backgrounds = self.recent_backgrounds[:max_history]
        self.save()
    
    def get_available_styles(self, all_styles: List[str]) -> List[str]:
        """Get styles that weren't recently used."""
        available = [s for s in all_styles if s not in self.recent_styles]
        return available if available else all_styles  # If all used, reset
    
    def should_avoid_background(self, bg_hash: str) -> bool:
        """Check if background was recently used."""
        return bg_hash in self.recent_backgrounds


class VideoGenerator:
    """Generate 17s Reels with EXTREME VARIETY."""

    TARGET_DURATION_MIN = 17.0
    TARGET_DURATION_MAX = 19.0
    TARGET_DURATION_IDEAL = 18.0
    MAX_SPEED = 1.3

    def __init__(self, config_path: Optional[str] = None):
        """Initialize VideoGenerator with variety system."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "video_config.json"

        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.width = 1080
        self.height = 1920
        self.fps = 30

        self.visual_styles = self.config["visual_styles"]
        self.fonts = self.config["fonts"]
        
        Path("output/reels").mkdir(parents=True, exist_ok=True)
        Path("output/audio").mkdir(parents=True, exist_ok=True)

        # Initialize history tracking
        state_file = Path("output/.style_history.json")
        self.style_history = StyleHistory(state_file)

        self.background_manager = BackgroundManager()
        self.audio_generator = AudioGenerator()

        logger.info("VideoGenerator initialized (EXTREME VARIETY MODE)")
        logger.info(f"Available styles: {len(self.visual_styles)}")

    def _select_style(self) -> Tuple[str, Dict]:
        """Select a visual style that hasn't been used recently."""
        all_style_names = list(self.visual_styles.keys())
        
        # Get styles that weren't recently used
        available_styles = self.style_history.get_available_styles(all_style_names)
        
        # Pick random from available
        selected_name = random.choice(available_styles)
        selected_style = self.visual_styles[selected_name]
        
        # Record usage
        self.style_history.add_style(selected_name)
        
        logger.info(f"\n🎨 STYLE SELECTED: {selected_style['name']}")
        logger.info(f"   Font: {selected_style['font_primary']}")
        logger.info(f"   Position: {selected_style['text_position']}")
        logger.info(f"   Colors: {list(selected_style['colors'].keys())}")
        
        return selected_name, selected_style

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex to RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _analyze_background_color(self, video_path: str, style_colors: Dict) -> str:
        """
        Analyze video background and pick best color from current style's palette.
        """
        try:
            video = VideoFileClip(video_path)
            middle_frame = video.get_frame(video.duration / 2)
            video.close()
            
            img = Image.fromarray(middle_frame)
            
            center_x = img.width // 2
            center_y = img.height // 2
            sample_size = 200
            
            crop = img.crop((
                center_x - sample_size,
                center_y - sample_size,
                center_x + sample_size,
                center_y + sample_size
            ))
            
            np_img = np.array(crop)
            avg_r = np.mean(np_img[:, :, 0])
            avg_g = np.mean(np_img[:, :, 1])
            avg_b = np.mean(np_img[:, :, 2])
            
            brightness = (avg_r + avg_g + avg_b) / 3
            
            logger.info(f"Background: R={avg_r:.0f} G={avg_g:.0f} B={avg_b:.0f} Brightness={brightness:.0f}")
            
            # Smart color selection based on brightness and style palette
            available_colors = list(style_colors.keys())
            
            # Very dark background
            if brightness < 60:
                # Prefer: white, cream, light colors
                preferred = [c for c in available_colors if any(x in c for x in ['white', 'cream', 'light', 'neon'])]
                return random.choice(preferred) if preferred else available_colors[0]
            
            # Dark background
            elif brightness < 100:
                # Prefer: bright colors, gold, neon
                preferred = [c for c in available_colors if any(x in c for x in ['gold', 'neon', 'bright', 'cyan', 'yellow'])]
                return random.choice(preferred) if preferred else available_colors[0]
            
            # Medium brightness
            elif brightness < 150:
                # Avoid very dark colors
                preferred = [c for c in available_colors if 'black' not in c]
                return random.choice(preferred) if preferred else available_colors[0]
            
            # Light background
            else:
                # Prefer: dark colors, deep tones
                preferred = [c for c in available_colors if any(x in c for x in ['black', 'deep', 'dark', 'burgundy'])]
                return random.choice(preferred) if preferred else available_colors[0]
                
        except Exception as e:
            logger.error(f"Color analysis failed: {e}")
            return list(style_colors.keys())[0]  # First color in palette

    def _create_text_overlay(
        self, 
        text: str, 
        style: Dict,
        text_color_key: str,
        scene_type: str
    ) -> Image.Image:
        """Create text overlay with style-specific formatting."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Get color from style palette
        text_color_hex = style['colors'][text_color_key]
        text_color = self._hex_to_rgb(text_color_hex) + (255,)

        # Load font based on style
        try:
            font_name = style['font_primary']
            font_config = self.fonts[font_name]
            font_path = Path(__file__).parent.parent / font_config['path']
            font_size = font_config['sizes'][scene_type]
            font = ImageFont.truetype(str(font_path), font_size)
        except Exception as e:
            logger.warning(f"Font load failed: {e}, using default")
            font = ImageFont.load_default()

        # Word wrapping
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] < self.width - 120:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))

        # Position based on style
        position = style['text_position']
        
        if position == "top_third":
            start_y = 300
        elif position == "bottom_third":
            start_y = 1300
        elif position == "center_lower":
            start_y = 1000  # Below center but not bottom
        else:  # center (default)
            start_y = 800

        line_height = font_size + 20
        total_height = len(lines) * line_height
        y = start_y - (total_height // 2)

        # Draw text with shadow for better visibility
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            
            # Shadow
            for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
                draw.text((x + offset[0], y + offset[1]), line, 
                         font=font, fill=(0, 0, 0, 180))
            
            # Main text
            draw.text((x, y), line, font=font, fill=text_color)
            y += line_height

        return img

    def _create_attribution_watermark(self, source: str, duration: float) -> ImageClip:
        """
        Create small attribution watermark for API compliance.
        
        Per Pexels/Pixabay terms: "show your users where the images and videos 
        are from, whenever search results are displayed."
        
        Args:
            source: Source name (Pexels, Pixabay, etc.)
            duration: Duration of the clip
            
        Returns:
            ImageClip with attribution text
        """
        # Create transparent image
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # VERY small attribution text
        attribution_text = f"via {source}"  # Shorter text
        
        try:
            font_path = Path(__file__).parent.parent / "fonts" / "DejaVuSans.ttf"
            font = ImageFont.truetype(str(font_path), 14)  # Smaller: 20 → 14
        except:
            font = ImageFont.load_default()
        
        # Position at bottom left with padding
        bbox = draw.textbbox((0, 0), attribution_text, font=font)
        text_width = bbox[2] - bbox[0]
        
        x = 15  # Left padding
        y = self.height - 40  # Bottom with padding
        
        # VERY transparent gray text (barely visible)
        text_color = (180, 180, 180, 60)  # Was 128 opacity, now 60 (much lighter)
        
        # Draw text
        draw.text((x, y), attribution_text, font=font, fill=text_color)
        
        # Save and create clip
        temp_path = Path("output") / "temp_attribution.png"
        img.save(temp_path)
        
        clip = ImageClip(str(temp_path), duration=duration)
        temp_path.unlink()
        
        logger.info(f"✅ Added subtle attribution: {source}")
        
        return clip

    def _create_background_clip(self, category: str, duration: float) -> Tuple[object, str]:
        """
        Create 4K video background OR high-res photo slideshow with variety tracking.
        
        Returns: (video_clip, video_path_or_type)
        """
        # Try 4K video first
        try:
            bg_video_path = self.background_manager.get_background_video(category)

            if bg_video_path and os.path.exists(bg_video_path):
                # Generate hash for variety tracking
                bg_hash = hashlib.md5(str(bg_video_path).encode()).hexdigest()[:8]
                
                # Check if recently used
                if self.style_history.should_avoid_background(bg_hash):
                    logger.info(f"⏭️  Skipping recently used video background")
                    bg_video_path = None  # Force photo slideshow
                else:
                    self.style_history.add_background(bg_hash)
                    logger.info(f"Using 4K video: {bg_video_path}")

                    try:
                        video = VideoFileClip(bg_video_path)

                        if video.h != self.height:
                            video = video.resized(height=self.height)

                        if video.w > self.width:
                            x_center = video.w / 2
                            video = video.cropped(
                                x1=x_center - self.width/2,
                                x2=x_center + self.width/2
                            )

                        if video.duration < duration:
                            n = int(duration / video.duration) + 1
                            video = concatenate_videoclips([video] * n)

                        video = video.subclipped(0, duration)

                        logger.info("✅ 4K video background")
                        return (video, bg_video_path)

                    except Exception as e:
                        logger.error(f"Video processing failed: {e}")
                        bg_video_path = None  # Force photo slideshow
        except Exception as e:
            logger.error(f"Video background failed: {e}")
            bg_video_path = None

        # No 4K video found - create photo slideshow
        logger.info("🖼️  No 4K video - creating high-res photo slideshow")
        
        try:
            # Download photos
            photos = self.background_manager.download_photos_for_slideshow(
                category=category,
                count=int(duration * 2) + 5  # ~2 photos per second + buffer
            )
            
            if photos:
                slideshow_clip = self._create_photo_slideshow(photos, duration)
                logger.info("✅ High-res photo slideshow background")
                return (slideshow_clip, "photo_slideshow")
        except Exception as e:
            logger.error(f"Photo slideshow failed: {e}")
        
        # Final fallback: gradient
        logger.warning("Using gradient fallback")
        gradient = self._create_gradient_background(duration)
        return (ImageClip(np.array(gradient), duration=duration), "gradient")
    
    def _create_photo_slideshow(self, photo_paths: List[Path], duration: float) -> object:
        """
        Create smooth photo slideshow with Ken Burns effect.
        
        Args:
            photo_paths: List of photo file paths
            duration: Total duration in seconds
            
        Returns:
            VideoClip of slideshow
        """
        if not photo_paths:
            raise ValueError("No photos provided for slideshow")
        
        logger.info(f"\n🎬 CREATING PHOTO SLIDESHOW")
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info(f"  Photos: {len(photo_paths)}")
        
        photo_duration = 0.5  # seconds per photo
        transition_duration = 0.2  # crossfade duration
        
        clips = []
        
        for i, photo_path in enumerate(photo_paths):
            try:
                # Load and resize photo
                img = Image.open(photo_path)
                
                # Ensure portrait orientation
                if img.width > img.height:
                    img = img.rotate(90, expand=True)
                
                # Resize to 1080x1920
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                
                # Convert to numpy array
                img_array = np.array(img)
                
                # Create clip with Ken Burns effect (slow zoom)
                clip = ImageClip(img_array, duration=photo_duration)
                
                # Apply slow zoom: 1.0x to 1.1x scale
                clip = clip.resized(lambda t: 1.0 + (t / photo_duration) * 0.1)
                
                # Add crossfade
                if i > 0:
                    clip = clip.crossfadein(transition_duration)
                
                clips.append(clip)
                
                # Stop when we have enough for duration
                total_time = len(clips) * photo_duration
                if total_time >= duration:
                    break
                    
            except Exception as e:
                logger.warning(f"Failed to load photo {photo_path}: {e}")
                continue
        
        if not clips:
            raise ValueError("No valid photos loaded for slideshow")
        
        # Concatenate all clips
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Trim to exact duration
        final_clip = final_clip.subclipped(0, min(duration, final_clip.duration))
        
        logger.info(f"✅ Slideshow created: {len(clips)} photos, {final_clip.duration:.2f}s")
        
        return final_clip

    def _create_gradient_background(self, duration: float) -> Image.Image:
        """Create gradient background as fallback."""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Random gradient colors
        colors = [
            ("#6B21A8", "#8B5CF6"),  # Purple
            ("#1E40AF", "#3B82F6"),  # Blue
            ("#BE123C", "#FB7185"),  # Pink
            ("#4338CA", "#6366F1"),  # Indigo
        ]
        start_color, end_color = random.choice(colors)
        
        start_rgb = self._hex_to_rgb(start_color)
        end_rgb = self._hex_to_rgb(end_color)
        
        for y in range(self.height):
            ratio = y / self.height
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        return img

    def generate_reel(self, content: Dict[str, str], category: str = "angel_numbers") -> str:
        """
        Generate a 17s Instagram Reel with EXTREME VARIETY.
        
        Each run will look completely different:
        - Different visual style
        - Different fonts
        - Different colors
        - Different text positions
        - Different backgrounds
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path("output/reels") / f"reel_{timestamp}.mp4"

        # STEP 1: SELECT VISUAL STYLE (never repeat recent)
        style_name, selected_style = self._select_style()

        # STEP 2: GENERATE AUDIO
        logger.info("\nSTEP 1: Generating audio...")
        
        audio_segments = {}
        base_speed = 1.15  # Base speed factor for natural pacing
        
        for scene in ["hook", "meaning", "action", "cta"]:
            text = content[scene]
            audio_path = Path("output/audio") / f"{scene}_{timestamp}.mp3"
            
            self.audio_generator.generate_voiceover(
                text=text,
                output_path=str(audio_path),
                speed_factor=base_speed
            )
            
            audio = AudioSegment.from_file(str(audio_path))
            # Audio is already sped up by generate_voiceover, no need to speed up again
            audio_sped = audio
            
            audio_segments[scene] = {
                'text': text,
                'audio': audio_sped,
                'duration': len(audio_sped) / 1000.0,
                'path': str(audio_path)
            }

        # Calculate duration
        natural_duration = sum(seg['duration'] for seg in audio_segments.values())
        required_speed = 1.0
        final_duration = self.TARGET_DURATION_IDEAL

        if natural_duration > self.TARGET_DURATION_MAX:
            required_speed = natural_duration / self.TARGET_DURATION_MAX
            total_speed = 1.15 * required_speed

            if total_speed > self.MAX_SPEED:
                required_speed = self.MAX_SPEED / 1.15
                final_duration = natural_duration / required_speed
            else:
                final_duration = self.TARGET_DURATION_MAX

        if required_speed != 1.0:
            for scene, seg in audio_segments.items():
                sped_up = seg['audio'].speedup(playback_speed=required_speed)
                seg['audio'] = sped_up
                seg['duration'] = len(sped_up) / 1000.0

        # Concatenate audio
        combined = AudioSegment.empty()
        for scene in ["hook", "meaning", "action", "cta"]:
            combined += audio_segments[scene]['audio']

        temp_voice = Path("output/audio") / f"temp_voice_{timestamp}.mp3"
        combined.export(str(temp_voice), format='mp3')

        final_audio = Path("output/audio") / f"final_{timestamp}.mp3"
        self._add_music(temp_voice, final_audio, final_duration)
        temp_voice.unlink()

        # STEP 3: CREATE BACKGROUND (avoid repeats)
        logger.info(f"\nSTEP 3: Creating background ({final_duration:.2f}s)...")
        background, bg_path = self._create_background_clip(category, final_duration)

        # STEP 4: ANALYZE AND PICK TEXT COLOR
        if bg_path and bg_path != "gradient" and bg_path != "photo_slideshow":
            # Real video file - analyze it
            text_color_key = self._analyze_background_color(bg_path, selected_style['colors'])
        else:
            # Gradient or photo slideshow - pick smart default based on style
            available_colors = list(selected_style['colors'].keys())
            
            # Prefer bright/light colors for gradients (they're usually dark)
            preferred = [c for c in available_colors if any(x in c for x in ['white', 'gold', 'light', 'neon', 'bright'])]
            
            if preferred:
                text_color_key = random.choice(preferred)
            else:
                text_color_key = available_colors[0]
            
            logger.info(f"Using default color for {bg_path}: {text_color_key}")

        logger.info(f"✅ Text color: {text_color_key.upper()}")

        # STEP 5: CREATE TEXT OVERLAYS
        logger.info("\nSTEP 4: Creating styled text overlays...")
        
        text_clips = []
        current_time = 0.0

        for scene in ["hook", "meaning", "action", "cta"]:
            seg = audio_segments[scene]
            
            text_img = self._create_text_overlay(
                text=seg['text'],
                style=selected_style,
                text_color_key=text_color_key,
                scene_type=scene
            )
            
            temp_img = Path("output") / f"temp_{scene}_{timestamp}.png"
            text_img.save(temp_img)
            
            clip = ImageClip(str(temp_img), duration=seg['duration'])
            clip = clip.set_start(current_time)  # set_start() not with_start()!
            text_clips.append(clip)
            
            logger.info(f"   {scene}: {current_time:.2f}s → {current_time + seg['duration']:.2f}s")
            current_time += seg['duration']

        # Add attribution watermark (required by Pexels/Pixabay API terms)
        # Only add if we used API content (not for gradients)
        if bg_path and bg_path != "gradient":
            attribution_source = "Pexels"  # Default
            if isinstance(bg_path, str):
                if "pixabay" in bg_path.lower():
                    attribution_source = "Pixabay"
                elif "photo_slideshow" in bg_path:
                    attribution_source = "Pexels Photos"
            
            attribution_clip = self._create_attribution_watermark(attribution_source, final_duration)
            text_clips.append(attribution_clip)
            logger.info(f"✅ Added attribution: {attribution_source}")
        else:
            logger.info("No API content used - no attribution needed")

        # STEP 6: COMPOSITE
        logger.info("\nSTEP 5: Compositing...")

        final = CompositeVideoClip([background] + text_clips)
        final = final.with_audio(AudioFileClip(str(final_audio)))
        final = final.with_duration(final_duration)

        # STEP 7: EXPORT
        logger.info("\nSTEP 6: Exporting...")
        
        final.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            preset='medium',
            bitrate='8000k'
        )

        # Cleanup
        for seg in audio_segments.values():
            Path(seg['path']).unlink(missing_ok=True)
        
        for scene in ["hook", "meaning", "action", "cta"]:
            Path(f"output/temp_{scene}_{timestamp}.png").unlink(missing_ok=True)
        
        final_audio.unlink(missing_ok=True)

        for clip in text_clips:
            clip.close()
        background.close()
        final.close()

        logger.info("\n" + "="*70)
        logger.info("✅ VIDEO COMPLETE - EXTREME VARIETY MODE")
        logger.info("="*70)
        logger.info(f"Output: {output_path}")
        logger.info(f"Style: {selected_style['name']}")
        logger.info(f"Font: {selected_style['font_primary']}")
        logger.info(f"Text Position: {selected_style['text_position']}")
        logger.info(f"Color: {text_color_key} ({selected_style['colors'][text_color_key]})")
        logger.info(f"Duration: {final_duration:.2f}s")
        logger.info("="*70 + "\n")

        return str(output_path)

    def _add_music(self, voiceover_path: Path, output_path: Path, duration: float):
        """Add background music."""
        import shutil

        music_dir = Path("music")
        
        if not music_dir.exists() or not list(music_dir.glob("*.mp3")):
            logger.warning("No music")
            shutil.copy(voiceover_path, output_path)
            return

        music_files = list(music_dir.glob("*.mp3"))
        music_file = random.choice(music_files)
        logger.info(f"🎵 Music: {music_file.name}")

        try:
            voice = AudioSegment.from_file(str(voiceover_path))
            music = AudioSegment.from_file(str(music_file))

            music = music - 14
            
            voice_ms = len(voice)
            
            if len(music) > voice_ms:
                music = music[:voice_ms]
            else:
                loops = (voice_ms // len(music)) + 1
                music = music * loops
                music = music[:voice_ms]

            mixed = music.overlay(voice)
            mixed.export(str(output_path), format='mp3', bitrate='192k')
            
            logger.info("✅ Mixed with music")

        except Exception as e:
            logger.error(f"Music failed: {e}")
            shutil.copy(voiceover_path, output_path)


def main():
    """Test extreme variety."""
    generator = VideoGenerator()

    test_content = {
        "hook": "Seeing 717 everywhere?",
        "meaning": "Angel number 717 signals new spiritual beginnings approaching fast",
        "action": "Trust your intuition. The universe guides you forward",
        "cta": "Follow @the17project for guidance"
    }

    # Generate 3 videos to show variety
    for i in range(3):
        logger.info(f"\n\n{'='*70}")
        logger.info(f"GENERATING VIDEO {i+1}/3")
        logger.info(f"{'='*70}\n")
        
        video = generator.generate_reel(
            content=test_content,
            category="angel_numbers"
        )
        
        logger.info(f"\n✅ Video {i+1} generated: {video}\n")


if __name__ == "__main__":
    main()
