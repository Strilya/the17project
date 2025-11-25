"""
Video Generator Module - FIXED VERSION

Key fixes:
1. REMOVED purple color overlay (lines 544-553) - clean HD video only
2. Music integration working properly
3. Dynamic duration based on actual audio
"""

import os
import json
import logging
import random
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

# PIL for image creation and text rendering
from PIL import Image, ImageDraw, ImageFont

# MoviePy for video composition
try:
    from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, VideoFileClip, ColorClip
except ImportError:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, VideoFileClip, ColorClip

# NumPy for array operations
import numpy as np

# Our modules
from background_manager import BackgroundManager
from audio_generator import AudioGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoGenerator:
    """Generates Instagram Reels with clean HD backgrounds and dynamic audio timing."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the VideoGenerator."""
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "video_config.json"

        self.config = self._load_config(config_path)

        # Extract settings
        self.video_settings = self.config["video_settings"]
        self.scene_timings = self.config["scene_timings"]
        self.color_palettes = self.config["color_palettes"]
        self.fonts = self.config["fonts"]
        self.audio_settings = self.config["audio"]
        self.branding = self.config["branding"]

        # Resolution
        self.width = self.video_settings["resolution"][0]
        self.height = self.video_settings["resolution"][1]
        self.fps = self.video_settings["fps"]

        # Create output folders
        self._create_output_folders()

        # Initialize managers
        self.background_manager = BackgroundManager()
        self.audio_generator = AudioGenerator()

        logger.info("VideoGenerator initialized successfully")

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load video configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def _create_output_folders(self) -> None:
        """Create output folders."""
        video_folder = Path(self.video_settings["output_folder"])
        audio_folder = Path(self.audio_settings["output_folder"])
        video_folder.mkdir(parents=True, exist_ok=True)
        audio_folder.mkdir(parents=True, exist_ok=True)

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _create_background_clip(self, category: str, duration: float):
        """
        Create CLEAN background video clip (NO OVERLAYS).
        
        CRITICAL: No purple gradient or color overlays added.
        """
        # Try to get video background
        bg_video_path = self.background_manager.get_background_video(category)

        if bg_video_path and os.path.exists(bg_video_path):
            logger.info(f"Using CLEAN HD video background: {bg_video_path}")

            try:
                # Load background video
                background = VideoFileClip(bg_video_path)

                # Resize to fit dimensions (1080x1920)
                if background.h != self.height:
                    background = background.resized(height=self.height)

                if background.w > self.width:
                    # Crop to center if too wide
                    x_center = background.w / 2
                    background = background.cropped(
                        x1=x_center - self.width/2,
                        x2=x_center + self.width/2
                    )

                # Loop if shorter than duration
                if background.duration < duration:
                    n_loops = int(duration / background.duration) + 1
                    looped_clips = [background] * n_loops
                    background = concatenate_videoclips(looped_clips)

                # Trim to exact duration
                background = background.subclipped(0, duration)

                # ============================================
                # NO COLOR OVERLAY - RETURN CLEAN VIDEO ONLY
                # ============================================
                logger.info("✅ Clean HD video background created (NO overlays)")
                return background

            except Exception as e:
                logger.error(f"Failed to load video background: {e}")
                logger.info("Falling back to gradient")

        # Fallback to gradient ONLY if video fails
        logger.info("Using gradient fallback")
        gradient_img = self._create_gradient_background(category)
        return ImageClip(np.array(gradient_img), duration=duration)

    def _create_gradient_background(self, category: str) -> Image.Image:
        """Create gradient background (fallback only)."""
        palette = self.color_palettes[category]
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        start_color = tuple(int(palette["gradient_start"][i:i+2], 16) for i in (1, 3, 5))
        end_color = tuple(int(palette["gradient_end"][i:i+2], 16) for i in (1, 3, 5))

        for y in range(self.height):
            ratio = y / self.height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        return img

    def _create_transparent_text_overlay(
        self,
        text: str,
        category: str,
        scene_type: str
    ) -> Image.Image:
        """Create transparent text overlay."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        palette = self.color_palettes[category]

        # Load font
        try:
            font_path = Path(__file__).parent.parent / "fonts" / "DejaVuSans-Bold.ttf"
            primary_font = ImageFont.truetype(
                str(font_path),
                self.fonts["primary"]["size"][scene_type]
            )
        except:
            primary_font = ImageFont.load_default()

        # Text color
        primary_color = self._hex_to_rgb(palette["primary_text"])

        # Word wrap
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=primary_font)
            if bbox[2] - bbox[0] < self.width - 100:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Draw text centered
        line_height = self.fonts["primary"]["size"][scene_type] + 20
        total_height = len(lines) * line_height
        y_start = (self.height - total_height) // 2

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=primary_font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = y_start + (i * line_height)

            # Drop shadow
            draw.text((x + 3, y + 3), line, font=primary_font, fill=(0, 0, 0, 180))
            # Main text
            draw.text((x, y), line, font=primary_font, fill=primary_color + (255,))

        return img

    def _add_background_music(self, voiceover_path: Path, output_path: Path, target_duration: float) -> Path:
        """Mix voiceover with random background music."""
        import shutil
        from pydub import AudioSegment

        music_dir = Path("music")

        # Check for music files
        if not music_dir.exists() or not list(music_dir.glob("*.mp3")):
            logger.warning("No music files - using voiceover only")
            shutil.copy(voiceover_path, output_path)
            return output_path

        # Pick random music
        music_files = list(music_dir.glob("*.mp3"))
        music_file = random.choice(music_files)
        logger.info(f"🎵 Using background music: {music_file.name}")

        try:
            # Load audio
            voiceover = AudioSegment.from_file(str(voiceover_path))
            music = AudioSegment.from_file(str(music_file))

            # Reduce music volume to 20%
            music = music - 14
            logger.info("Reduced music volume to 20%")

            # Match duration
            target_ms = len(voiceover)  # Use voiceover length, not hardcoded

            if len(music) > target_ms:
                music = music[:target_ms]
            elif len(music) < target_ms:
                loops = (target_ms // len(music)) + 1
                music = music * loops
                music = music[:target_ms]

            # Mix
            mixed = music.overlay(voiceover)
            mixed.export(str(output_path), format='mp3', bitrate='128k')

            logger.info(f"✅ Mixed audio with background music at 20% volume")
            return output_path

        except Exception as e:
            logger.error(f"Music mixing failed: {e}")
            shutil.copy(voiceover_path, output_path)
            return output_path

    def generate_reel(
        self,
        content: Dict[str, str],
        category: str = "angel_numbers",
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate Instagram Reel with CLEAN HD background and dynamic audio timing.
        
        CRITICAL FIXES:
        - NO purple gradient overlays
        - Duration based on actual audio length
        - Background music from music/ folder
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if output_filename is None:
                output_filename = f"reel_{category}_{timestamp}.mp4"

            output_path = Path(self.video_settings["output_folder"]) / output_filename
            final_audio_path = Path(self.audio_settings["output_folder"]) / f"final_{timestamp}.mp3"

            logger.info("\n" + "="*70)
            logger.info("GENERATING INSTAGRAM REEL")
            logger.info("="*70)

            # Generate all audio segments first
            logger.info("STEP 1: Generating voiceover segments...")
            audio_segments = {}
            
            for scene_type in ["hook", "meaning", "action", "cta"]:
                text = content.get(scene_type, "")
                audio_path = Path(self.audio_settings["output_folder"]) / f"{scene_type}_{timestamp}.mp3"
                
                # Generate voiceover
                self.audio_generator.generate_voiceover(
                    text=text,
                    output_path=str(audio_path),
                    speed_factor=1.15
                )
                
                # Measure actual duration
                from pydub import AudioSegment
                audio = AudioSegment.from_file(str(audio_path))
                duration = len(audio) / 1000.0
                
                audio_segments[scene_type] = {
                    'path': str(audio_path),
                    'text': text,
                    'duration': duration
                }
                
                logger.info(f"  {scene_type}: {duration:.2f}s")

            # Calculate total duration
            total_duration = sum(seg['duration'] for seg in audio_segments.values())
            logger.info(f"Total audio duration: {total_duration:.2f}s")

            # Concatenate voiceover
            logger.info("STEP 2: Concatenating voiceover...")
            from pydub import AudioSegment
            combined_voice = AudioSegment.empty()
            
            for scene_type in ["hook", "meaning", "action", "cta"]:
                segment = AudioSegment.from_file(audio_segments[scene_type]['path'])
                combined_voice += segment

            temp_voiceover_path = Path(self.audio_settings["output_folder"]) / f"temp_voiceover_{timestamp}.mp3"
            combined_voice.export(str(temp_voiceover_path), format='mp3')

            # Add background music
            logger.info("STEP 3: Adding background music...")
            final_audio_path = self._add_background_music(
                temp_voiceover_path,
                final_audio_path,
                total_duration
            )

            # Clean up temp voiceover
            if temp_voiceover_path.exists():
                temp_voiceover_path.unlink()

            # Create background video
            logger.info("STEP 4: Creating CLEAN HD background...")
            background_clip = self._create_background_clip(category, total_duration)

            # Create text overlays
            logger.info("STEP 5: Creating text overlays...")
            text_overlays = []
            current_time = 0.0

            for scene_type in ["hook", "meaning", "action", "cta"]:
                segment_info = audio_segments[scene_type]
                duration = segment_info['duration']
                
                logger.info(f"  {scene_type}: {duration:.2f}s @ {current_time:.2f}s")

                text_img = self._create_transparent_text_overlay(
                    text=segment_info['text'],
                    category=category,
                    scene_type=scene_type
                )

                temp_img_path = Path("output") / f"temp_{scene_type}_{timestamp}.png"
                temp_img_path.parent.mkdir(exist_ok=True)
                text_img.save(temp_img_path)

                text_clip = ImageClip(str(temp_img_path), duration=duration)
                text_clip = text_clip.with_start(current_time)
                text_overlays.append(text_clip)
                
                current_time += duration

            # Composite final video
            logger.info("STEP 6: Compositing final video...")
            all_clips = [background_clip] + text_overlays
            final_video = CompositeVideoClip(all_clips)

            # Add audio
            final_audio_clip = AudioFileClip(str(final_audio_path))
            final_video = final_video.with_audio(final_audio_clip)
            final_video = final_video.with_duration(total_duration)

            # Export
            logger.info("STEP 7: Exporting...")
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                preset='medium'
            )

            # Cleanup
            for segment_info in audio_segments.values():
                Path(segment_info['path']).unlink(missing_ok=True)
            
            for scene_type in ["hook", "meaning", "action", "cta"]:
                Path(f"output/temp_{scene_type}_{timestamp}.png").unlink(missing_ok=True)
            
            final_audio_path.unlink(missing_ok=True)

            # Close clips
            for clip in text_overlays:
                clip.close()
            background_clip.close()
            final_video.close()
            final_audio_clip.close()

            logger.info("\n" + "="*70)
            logger.info("✅ VIDEO GENERATION COMPLETE")
            logger.info("="*70)
            logger.info(f"Output: {output_path}")
            logger.info(f"Duration: {total_duration:.2f}s")
            logger.info(f"Quality: CLEAN HD (no overlays)")
            logger.info("="*70 + "\n")

            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate video: {e}")
            raise


def main():
    """Test the VideoGenerator."""
    try:
        print("\n" + "="*70)
        print("TESTING VIDEO GENERATOR")
        print("="*70)

        generator = VideoGenerator()

        test_content = {
            "hook": "See 717 everywhere?",
            "meaning": "Angel number 717 signals spiritual awakening and divine guidance",
            "action": "Trust your intuition. The universe is speaking to you",
            "cta": "Follow @the17project for daily angel numbers"
        }

        video_path = generator.generate_reel(
            content=test_content,
            category="angel_numbers",
            output_filename="test_reel_717.mp4"
        )

        print(f"\n✅ Video generated: {video_path}")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
