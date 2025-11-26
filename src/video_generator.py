"""
Video Generator - DYNAMIC 17-19s + SMART COLOR CONTRAST

Features:
- Dynamic 17-19 second videos (natural pacing)
- Clean 4K backgrounds
- Smart text colors that CONTRAST with background
- Purple/Gold/White palette
- Flexible duration for comfortable speech
"""

import os
import json
import logging
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


class VideoGenerator:
    """Generate 17-19 second Reels with natural pacing and smart color contrast."""

    # ========================================================================
    # OPTION A: EXACT 17 SECONDS (WORKING - BACKUP)
    # Uses math to calculate exact speed needed to fit content in 17s
    # Result: Always 17s but may feel rushed if content is long
    # ========================================================================
    # TARGET_DURATION = 17.0  # FIXED target - always 17s
    # MAX_SPEED = 1.5  # Allow up to 1.5x for longer content

    # ========================================================================
    # OPTION B: DYNAMIC 17-19 SECONDS (ACTIVE)
    # Allows natural pacing with flexible duration
    # Result: More natural speech, better user experience
    # ========================================================================
    TARGET_DURATION_MIN = 17.0   # Minimum video length
    TARGET_DURATION_MAX = 19.0   # Maximum video length
    TARGET_DURATION_IDEAL = 18.0 # Target middle point
    MAX_SPEED = 1.3              # Max speedup (more conservative)

    # COLOR PALETTE - Purple/Gold/White
    TEXT_COLORS = {
        "bright_purple": "#9D4EDD",      # Bright purple - for dark backgrounds
        "deep_purple": "#5A189A",        # Deep purple - for light backgrounds  
        "gold": "#FFD700",                # Gold - for purple/blue backgrounds
        "white": "#FFFFFF",               # White - for very dark backgrounds
        "magenta": "#D946EF",             # Magenta - for green backgrounds
        "light_purple": "#E0AAFF"         # Light purple - for medium backgrounds
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize VideoGenerator."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "video_config.json"

        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.width = 1080
        self.height = 1920
        self.fps = 30

        self.color_palettes = self.config["color_palettes"]
        self.fonts = self.config["fonts"]
        
        Path("output/reels").mkdir(parents=True, exist_ok=True)
        Path("output/audio").mkdir(parents=True, exist_ok=True)

        self.background_manager = BackgroundManager()
        self.audio_generator = AudioGenerator()

        logger.info("VideoGenerator initialized (17s + smart colors)")

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex to RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _analyze_background_color(self, video_path: str) -> str:
        """
        Analyze video background to pick best contrasting text color.
        
        Returns color key from TEXT_COLORS dict.
        """
        try:
            # Sample middle frame
            video = VideoFileClip(video_path)
            middle_frame = video.get_frame(video.duration / 2)
            video.close()
            
            # Convert to PIL Image
            img = Image.fromarray(middle_frame)
            
            # Get dominant colors (sample center region)
            center_x = img.width // 2
            center_y = img.height // 2
            sample_size = 200
            
            crop = img.crop((
                center_x - sample_size,
                center_y - sample_size,
                center_x + sample_size,
                center_y + sample_size
            ))
            
            # Calculate average RGB
            np_img = np.array(crop)
            avg_r = np.mean(np_img[:, :, 0])
            avg_g = np.mean(np_img[:, :, 1])
            avg_b = np.mean(np_img[:, :, 2])
            
            # Calculate brightness
            brightness = (avg_r + avg_g + avg_b) / 3
            
            # Determine dominant hue
            max_channel = max(avg_r, avg_g, avg_b)
            
            logger.info(f"Background analysis: R={avg_r:.0f} G={avg_g:.0f} B={avg_b:.0f} Brightness={brightness:.0f}")
            
            # SMART COLOR SELECTION
            
            # Very dark background → White or bright purple
            if brightness < 60:
                logger.info("Dark background → Using WHITE text")
                return "white"
            
            # Dark background → Bright purple or gold
            elif brightness < 100:
                if avg_b > avg_r and avg_b > avg_g:  # Blue-ish
                    logger.info("Dark blue background → Using GOLD text")
                    return "gold"
                else:
                    logger.info("Dark background → Using BRIGHT PURPLE text")
                    return "bright_purple"
            
            # Medium brightness
            elif brightness < 150:
                # Yellow/Orange (sunset, fire)
                if avg_r > 150 and avg_g > 100 and avg_b < 100:
                    logger.info("Yellow/Orange background → Using DEEP PURPLE text")
                    return "deep_purple"
                
                # Green/Teal (nature, ocean)
                elif avg_g > avg_r and avg_g > avg_b:
                    logger.info("Green background → Using MAGENTA text")
                    return "magenta"
                
                # Purple/Blue (space, nebula)
                elif avg_b > avg_r:
                    logger.info("Blue/Purple background → Using GOLD text")
                    return "gold"
                
                else:
                    logger.info("Medium background → Using BRIGHT PURPLE text")
                    return "bright_purple"
            
            # Light background
            else:
                logger.info("Light background → Using DEEP PURPLE text")
                return "deep_purple"
                
        except Exception as e:
            logger.error(f"Color analysis failed: {e}")
            # Default fallback
            return "bright_purple"

    def _create_text_overlay(
        self, 
        text: str, 
        text_color_key: str,
        scene_type: str
    ) -> Image.Image:
        """Create text overlay with smart contrasting color."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Get color from palette
        text_color_hex = self.TEXT_COLORS[text_color_key]
        text_color = self._hex_to_rgb(text_color_hex) + (255,)

        # Load font
        try:
            font_path = Path(__file__).parent.parent / "fonts" / "DejaVuSans-Bold.ttf"
            font_sizes = {
                "hook": 82,    # 25% smaller
                "meaning": 64,  # 25% smaller
                "action": 64,   # 25% smaller
                "cta": 71       # 25% smaller
            }
            font_size = font_sizes.get(scene_type, 64)
            font = ImageFont.truetype(str(font_path), font_size)
        except:
            font = ImageFont.load_default()

        # Word wrap
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] < self.width - 100:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))

        # Draw centered with strong shadow
        line_height = font_size + 20
        total_height = len(lines) * line_height
        y_start = (self.height - total_height) // 2

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = y_start + (i * line_height)

            # Extra strong shadow with glow effect
            # Outer glow
            for offset in [(0, 6), (6, 0), (0, -6), (-6, 0), (6, 6), (-6, -6), (6, -6), (-6, 6)]:
                draw.text((x + offset[0], y + offset[1]), line, font=font, fill=(0, 0, 0, 180))
            # Inner shadow
            for offset in [(0, 3), (3, 0), (0, -3), (-3, 0), (3, 3), (-3, -3), (3, -3), (-3, 3)]:
                draw.text((x + offset[0], y + offset[1]), line, font=font, fill=(0, 0, 0, 240))

            # Main text
            draw.text((x, y), line, font=font, fill=text_color)

        return img

    def _create_gradient_background(self, category: str) -> Image.Image:
        """Gradient fallback."""
        palette = self.color_palettes[category]
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        start = tuple(int(palette["gradient_start"][i:i+2], 16) for i in (1, 3, 5))
        end = tuple(int(palette["gradient_end"][i:i+2], 16) for i in (1, 3, 5))

        for y in range(self.height):
            ratio = y / self.height
            r = int(start[0] * (1 - ratio) + end[0] * ratio)
            g = int(start[1] * (1 - ratio) + end[1] * ratio)
            b = int(start[2] * (1 - ratio) + end[2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        return img

    def _create_background_clip(self, category: str, duration: float) -> Tuple[object, str]:
        """
        Create 4K video background OR high-res photo slideshow.
        
        Returns: (video_clip, video_path_or_type)
        """
        # Try 4K video first
        bg_video_path = self.background_manager.get_background_video(category)

        if bg_video_path and os.path.exists(bg_video_path):
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
                logger.error(f"Video failed: {e}")

        # No 4K video found - create photo slideshow
        logger.info("🖼️  No 4K video - creating high-res photo slideshow")
        
        # Download photos
        photos = self.background_manager.download_photos_for_slideshow(
            category=category,
            count=int(duration * 2) + 5  # ~2 photos per second + buffer
        )
        
        if photos:
            slideshow_clip = self._create_photo_slideshow(photos, duration)
            logger.info("✅ High-res photo slideshow background")
            return (slideshow_clip, "photo_slideshow")
        
        # Final fallback: gradient
        logger.warning("Using gradient fallback")
        gradient = self._create_gradient_background(category)
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
                def zoom_effect(t):
                    scale = 1.0 + (t / photo_duration) * 0.1  # 1.0 → 1.1
                    return clip.resized(scale).set_position('center')
                
                clip = clip.time_transform(zoom_effect, apply_to=['mask'])
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

    def generate_reel(
        self,
        content: Dict[str, str],
        category: str = "angel_numbers",
        output_filename: Optional[str] = None
    ) -> str:
        """Generate EXACTLY 17-second Reel with smart colors."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_filename is None:
            output_filename = f"reel_{category}_{timestamp}.mp4"

        output_path = Path("output/reels") / output_filename

        logger.info("\n" + "="*70)
        logger.info("GENERATING 17-SECOND REEL (SMART COLORS)")
        logger.info("="*70)

        # Generate audio
        logger.info("STEP 1: Generating audio...")
        
        audio_segments = {}
        base_speed = 1.15
        
        for scene in ["hook", "meaning", "action", "cta"]:
            text = content.get(scene, "")
            audio_path = Path("output/audio") / f"{scene}_{timestamp}.mp3"
            
            self.audio_generator.generate_voiceover(
                text=text,
                output_path=str(audio_path),
                speed_factor=base_speed
            )
            
            audio = AudioSegment.from_file(str(audio_path))
            duration = len(audio) / 1000.0
            
            audio_segments[scene] = {
                'path': str(audio_path),
                'text': text,
                'duration': duration,
                'audio': audio
            }
            
            logger.info(f"  {scene}: {duration:.2f}s - '{text}'")

        # ========================================================================
        # DYNAMIC DURATION LOGIC (17-19s)
        #
        # Flow:
        # 1. Measure natural content duration at base speed (1.15x)
        # 2. If < 17s: Pad with silence to reach 17s minimum
        # 3. If 17-19s: Keep natural duration (PERFECT - no changes)
        # 4. If > 19s: Speed up to fit in 19s maximum (up to 1.3x total)
        #
        # This ensures natural pacing while staying Instagram-friendly
        # ========================================================================

        # STEP 1: Measure natural duration
        natural_duration = sum(seg['duration'] for seg in audio_segments.values())
        logger.info(f"\nNatural duration at 1.15x: {natural_duration:.2f}s")

        # STEP 2: Determine if adjustment needed
        if natural_duration < self.TARGET_DURATION_MIN:
            # Content is short - will pad to 17s minimum
            logger.info(f"✅ Content is short ({natural_duration:.2f}s)")
            logger.info(f"   Will pad with silence to reach {self.TARGET_DURATION_MIN}s")
            required_speed = 1.0  # No speed adjustment needed
            final_duration = self.TARGET_DURATION_MIN

        elif natural_duration <= self.TARGET_DURATION_MAX:
            # Content fits perfectly in 17-19s range - use natural duration
            logger.info(f"✅ Perfect! Content naturally fits in range ({natural_duration:.2f}s)")
            logger.info(f"   No speed adjustment needed - using natural pacing")
            required_speed = 1.0  # No speed adjustment needed
            final_duration = natural_duration

        else:
            # Content is too long - need to speed up to fit in 19s max
            # Calculate speed needed: if content is 22s, need 22/19 = 1.16x additional speed
            # Since base is already 1.15x, total would be 1.15 * 1.16 = 1.33x
            required_speed = natural_duration / self.TARGET_DURATION_MAX

            # Check if within acceptable range
            total_speed = 1.15 * required_speed  # Base speed * additional speed

            if total_speed > self.MAX_SPEED:
                logger.warning(f"⚠️  Content too long! Needs {total_speed:.2f}x total speed")
                logger.info(f"   Limiting to {self.MAX_SPEED}x maximum")
                required_speed = self.MAX_SPEED / 1.15
                final_duration = natural_duration / required_speed
                logger.info(f"   Will produce {final_duration:.2f}s video")
            else:
                logger.info(f"⚠️  Content long ({natural_duration:.2f}s), speeding up to {self.TARGET_DURATION_MAX}s")
                logger.info(f"   Additional speed factor: {required_speed:.3f}x (total: {total_speed:.2f}x)")
                final_duration = self.TARGET_DURATION_MAX

        # STEP 3: Apply speed adjustment if needed
        if required_speed != 1.0:
            logger.info(f"\nApplying {required_speed:.3f}x additional speed...")
            for scene, seg in audio_segments.items():
                original_duration = seg['duration']
                sped_up = seg['audio'].speedup(playback_speed=required_speed)
                seg['audio'] = sped_up
                seg['duration'] = len(sped_up) / 1000.0
                logger.info(f"  {scene}: {original_duration:.2f}s → {seg['duration']:.2f}s")

        # ========================================================================
        # CONCATENATE AND PAD (if needed)
        # ========================================================================

        # STEP 4: Concatenate all audio segments
        logger.info("\nSTEP 2: Concatenating audio...")
        combined = AudioSegment.empty()
        for scene in ["hook", "meaning", "action", "cta"]:
            combined += audio_segments[scene]['audio']

        actual_duration_ms = len(combined)
        actual_duration = actual_duration_ms / 1000.0

        logger.info(f"Combined audio duration: {actual_duration:.2f}s")

        # STEP 5: Pad ONLY if below minimum (17s)
        target_ms = int(final_duration * 1000)

        if actual_duration_ms < target_ms:
            silence_needed = target_ms - actual_duration_ms
            combined = combined + AudioSegment.silent(duration=silence_needed)
            logger.info(f"Added {silence_needed/1000:.2f}s silence to reach {final_duration:.2f}s")

        logger.info(f"✅ Final audio duration: {len(combined)/1000.0:.2f}s")

        # Debug output
        logger.info("\n" + "="*70)
        logger.info("FINAL VIDEO SPECS:")
        logger.info(f"  Target range: {self.TARGET_DURATION_MIN}s - {self.TARGET_DURATION_MAX}s")
        logger.info(f"  Actual: {final_duration:.2f}s")
        logger.info(f"  Additional speed: {required_speed:.3f}x")
        logger.info(f"  Total speed: {1.15 * required_speed:.2f}x")
        logger.info(f"  Audio length: {len(combined)/1000.0:.2f}s")
        logger.info("="*70)

        temp_voice = Path("output/audio") / f"temp_voice_{timestamp}.mp3"
        combined.export(str(temp_voice), format='mp3')

        final_audio = Path("output/audio") / f"final_{timestamp}.mp3"
        self._add_music(temp_voice, final_audio, final_duration)
        temp_voice.unlink()

        # Create background (use actual final duration)
        logger.info(f"\nSTEP 3: Creating 4K background ({final_duration:.2f}s)...")
        background, bg_path = self._create_background_clip(category, final_duration)

        # Analyze background and pick text color
        if bg_path:
            text_color_key = self._analyze_background_color(bg_path)
        else:
            text_color_key = "bright_purple"  # Fallback for gradient

        logger.info(f"✅ Text color: {text_color_key.upper()}")

        # Create text overlays
        logger.info("\nSTEP 4: Creating text overlays...")
        
        text_clips = []
        current_time = 0.0

        for scene in ["hook", "meaning", "action", "cta"]:
            seg = audio_segments[scene]
            
            text_img = self._create_text_overlay(
                text=seg['text'],
                text_color_key=text_color_key,
                scene_type=scene
            )
            
            temp_img = Path("output") / f"temp_{scene}_{timestamp}.png"
            temp_img.parent.mkdir(exist_ok=True)
            text_img.save(temp_img)
            
            clip = ImageClip(str(temp_img), duration=seg['duration'])
            clip = clip.with_start(current_time)
            text_clips.append(clip)
            
            current_time += seg['duration']

        # Composite
        logger.info("\nSTEP 5: Compositing...")

        final = CompositeVideoClip([background] + text_clips)
        final = final.with_audio(AudioFileClip(str(final_audio)))
        final = final.with_duration(final_duration)

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
        logger.info("✅ VIDEO COMPLETE")
        logger.info("="*70)
        logger.info(f"Output: {output_path}")
        logger.info(f"Duration: {final_duration:.2f}s (dynamic 17-19s range)")
        logger.info(f"Natural pacing: {1.15 * required_speed:.2f}x total speed")
        logger.info(f"Text color: {text_color_key.upper()} ({self.TEXT_COLORS[text_color_key]})")
        logger.info(f"Quality: 4K backgrounds, clean HD export")
        logger.info("="*70 + "\n")

        return str(output_path)

    def _add_music(self, voiceover_path: Path, output_path: Path, duration: float):
        """Add background music."""
        import shutil
        import random

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
    """Test."""
    generator = VideoGenerator()

    test_content = {
        "hook": "Seeing 717 everywhere?",
        "meaning": "Angel number 717 signals new spiritual beginnings approaching fast",
        "action": "Trust your intuition. The universe guides you forward",
        "cta": "Follow @the17project for guidance"
    }

    video = generator.generate_reel(
        content=test_content,
        category="angel_numbers"
    )

    print(f"\n✅ Generated: {video}")


if __name__ == "__main__":
    main()
