"""
Video Generator - FINAL FIXED VERSION

CRITICAL FIXES:
1. NO purple gradient overlay - clean HD video only
2. Duration = actual audio duration (NOT hardcoded 17s)
3. Text timing synced perfectly with audio
4. Background music integration working
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional
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
    """Generate Instagram Reels with clean HD backgrounds and perfect audio sync."""

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

        logger.info("VideoGenerator initialized")

    def _hex_to_rgb(self, hex_color: str):
        """Convert hex to RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _create_text_overlay(self, text: str, category: str, scene_type: str) -> Image.Image:
        """Create transparent text overlay."""
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        palette = self.color_palettes[category]

        # Load font
        try:
            font_path = Path(__file__).parent.parent / "fonts" / "DejaVuSans-Bold.ttf"
            font_size = self.fonts["primary"]["size"][scene_type]
            font = ImageFont.truetype(str(font_path), font_size)
        except:
            font = ImageFont.load_default()

        text_color = self._hex_to_rgb(palette["primary_text"]) + (255,)

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

        # Draw centered text
        line_height = font_size + 20
        total_height = len(lines) * line_height
        y_start = (self.height - total_height) // 2

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = y_start + (i * line_height)

            # Shadow
            draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 180))
            # Text
            draw.text((x, y), line, font=font, fill=text_color)

        return img

    def _create_gradient_background(self, category: str) -> Image.Image:
        """Create gradient background (fallback only)."""
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

    def _create_background_clip(self, category: str, duration: float):
        """
        Create clean HD video background (NO overlays).
        """
        bg_video_path = self.background_manager.get_background_video(category)

        if bg_video_path and os.path.exists(bg_video_path):
            logger.info(f"Using clean HD video: {bg_video_path}")

            try:
                video = VideoFileClip(bg_video_path)

                # Resize to height
                if video.h != self.height:
                    video = video.resized(height=self.height)

                # Crop width if needed
                if video.w > self.width:
                    x_center = video.w / 2
                    video = video.cropped(
                        x1=x_center - self.width/2,
                        x2=x_center + self.width/2
                    )

                # Loop if needed
                if video.duration < duration:
                    n = int(duration / video.duration) + 1
                    video = concatenate_videoclips([video] * n)

                # Trim to exact duration
                video = video.subclipped(0, duration)

                logger.info("✅ Clean HD background (NO overlays)")
                return video

            except Exception as e:
                logger.error(f"Video failed: {e}")

        # Fallback to gradient
        logger.info("Using gradient fallback")
        gradient = self._create_gradient_background(category)
        return ImageClip(np.array(gradient), duration=duration)

    def generate_reel(
        self,
        content: Dict[str, str],
        category: str = "angel_numbers",
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate Instagram Reel with perfect timing.
        
        Flow:
        1. Generate all 4 audio segments
        2. Measure actual duration of each
        3. Create video that matches EXACT audio duration
        4. Add background music
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_filename is None:
            output_filename = f"reel_{category}_{timestamp}.mp4"

        output_path = Path("output/reels") / output_filename

        logger.info("\n" + "="*70)
        logger.info("GENERATING INSTAGRAM REEL")
        logger.info("="*70)

        # ===================================================================
        # STEP 1: Generate all audio segments and measure durations
        # ===================================================================
        logger.info("STEP 1: Generating audio segments...")
        
        audio_segments = {}
        
        for scene in ["hook", "meaning", "action", "cta"]:
            text = content.get(scene, "")
            audio_path = Path("output/audio") / f"{scene}_{timestamp}.mp3"
            
            # Generate voiceover
            self.audio_generator.generate_voiceover(
                text=text,
                output_path=str(audio_path),
                speed_factor=1.15
            )
            
            # Measure ACTUAL duration
            audio = AudioSegment.from_file(str(audio_path))
            duration = len(audio) / 1000.0  # ms to seconds
            
            audio_segments[scene] = {
                'path': str(audio_path),
                'text': text,
                'duration': duration
            }
            
            logger.info(f"  {scene}: {duration:.2f}s - '{text[:30]}...'")

        # Calculate total duration
        total_duration = sum(seg['duration'] for seg in audio_segments.values())
        logger.info(f"\n✅ Total audio duration: {total_duration:.2f}s")

        # ===================================================================
        # STEP 2: Concatenate audio and add background music
        # ===================================================================
        logger.info("\nSTEP 2: Mixing audio...")
        
        # Concatenate voiceover segments
        combined = AudioSegment.empty()
        for scene in ["hook", "meaning", "action", "cta"]:
            segment = AudioSegment.from_file(audio_segments[scene]['path'])
            combined += segment
        
        temp_voice = Path("output/audio") / f"temp_voice_{timestamp}.mp3"
        combined.export(str(temp_voice), format='mp3')
        
        # Add background music
        final_audio = Path("output/audio") / f"final_{timestamp}.mp3"
        self._add_music(temp_voice, final_audio, total_duration)
        
        temp_voice.unlink()  # Clean up

        # ===================================================================
        # STEP 3: Create background video (matches audio duration)
        # ===================================================================
        logger.info("\nSTEP 3: Creating background...")
        background = self._create_background_clip(category, total_duration)

        # ===================================================================
        # STEP 4: Create text overlays (synced to audio)
        # ===================================================================
        logger.info("\nSTEP 4: Creating text overlays...")
        
        text_clips = []
        current_time = 0.0

        for scene in ["hook", "meaning", "action", "cta"]:
            seg = audio_segments[scene]
            
            logger.info(f"  {scene}: {seg['duration']:.2f}s @ {current_time:.2f}s")
            
            # Create text overlay
            text_img = self._create_text_overlay(
                text=seg['text'],
                category=category,
                scene_type=scene
            )
            
            # Save temporarily
            temp_img = Path("output") / f"temp_{scene}_{timestamp}.png"
            temp_img.parent.mkdir(exist_ok=True)
            text_img.save(temp_img)
            
            # Create clip
            clip = ImageClip(str(temp_img), duration=seg['duration'])
            clip = clip.with_start(current_time)
            text_clips.append(clip)
            
            current_time += seg['duration']

        # ===================================================================
        # STEP 5: Composite and export
        # ===================================================================
        logger.info("\nSTEP 5: Compositing...")
        
        final = CompositeVideoClip([background] + text_clips)
        final = final.with_audio(AudioFileClip(str(final_audio)))
        final = final.with_duration(total_duration)

        logger.info(f"\nSTEP 6: Exporting {total_duration:.2f}s video...")
        
        final.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            preset='medium'
        )

        # ===================================================================
        # STEP 7: Cleanup
        # ===================================================================
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
        logger.info(f"Duration: {total_duration:.2f}s (matches audio)")
        logger.info("="*70 + "\n")

        return str(output_path)

    def _add_music(self, voiceover_path: Path, output_path: Path, duration: float):
        """Add background music."""
        import shutil
        import random

        music_dir = Path("music")
        
        if not music_dir.exists() or not list(music_dir.glob("*.mp3")):
            logger.warning("No music - using voiceover only")
            shutil.copy(voiceover_path, output_path)
            return

        music_files = list(music_dir.glob("*.mp3"))
        music_file = random.choice(music_files)
        logger.info(f"🎵 Music: {music_file.name}")

        try:
            voice = AudioSegment.from_file(str(voiceover_path))
            music = AudioSegment.from_file(str(music_file))

            # Reduce volume
            music = music - 14  # -14dB ≈ 20%
            
            # Match voice duration
            voice_ms = len(voice)
            
            if len(music) > voice_ms:
                music = music[:voice_ms]
            else:
                loops = (voice_ms // len(music)) + 1
                music = music * loops
                music = music[:voice_ms]

            # Mix
            mixed = music.overlay(voice)
            mixed.export(str(output_path), format='mp3', bitrate='128k')
            
            logger.info("✅ Mixed with background music")

        except Exception as e:
            logger.error(f"Music failed: {e}")
            shutil.copy(voiceover_path, output_path)


def main():
    """Test the generator."""
    generator = VideoGenerator()

    test_content = {
        "hook": "See 717 everywhere?",
        "meaning": "Angel number 717 signals spiritual awakening",
        "action": "Trust your intuition today",
        "cta": "Follow @the17project"
    }

    video = generator.generate_reel(
        content=test_content,
        category="angel_numbers",
        output_filename="test_717.mp4"
    )

    print(f"\n✅ Video: {video}")


if __name__ == "__main__":
    main()
