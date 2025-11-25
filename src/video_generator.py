"""
Video Generator - FIXED FOR EXACT 17 SECONDS

Key features:
- ALWAYS 17 seconds (target duration)
- Clean 4K backgrounds (NO overlays)
- Text perfectly synced with voice
- Speech at max 1.3x speed
- Content fits naturally in 17 seconds
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
    """Generate perfect 17-second Instagram Reels."""

    TARGET_DURATION = 17.0  # FIXED target
    MAX_SPEED = 1.3  # Maximum speech speedup

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

        logger.info("VideoGenerator initialized (17s target)")

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

        # Draw centered
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
        """Create gradient (fallback only)."""
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
        """Create CLEAN 4K background (NO overlays)."""
        bg_video_path = self.background_manager.get_background_video(category)

        if bg_video_path and os.path.exists(bg_video_path):
            logger.info(f"Using 4K video: {bg_video_path}")

            try:
                video = VideoFileClip(bg_video_path)

                # Resize
                if video.h != self.height:
                    video = video.resized(height=self.height)

                # Crop width
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

                logger.info("✅ Clean 4K background (NO overlays)")
                return video

            except Exception as e:
                logger.error(f"Video failed: {e}")

        # Fallback
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
        Generate EXACTLY 17-second Instagram Reel.
        
        Flow:
        1. Generate audio segments
        2. Check if total > 17s, speed up if needed (max 1.3x)
        3. Pad with silence if < 17s
        4. Create video that matches EXACTLY 17s
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_filename is None:
            output_filename = f"reel_{category}_{timestamp}.mp4"

        output_path = Path("output/reels") / output_filename

        logger.info("\n" + "="*70)
        logger.info("GENERATING 17-SECOND INSTAGRAM REEL")
        logger.info("="*70)

        # Generate audio segments
        logger.info("STEP 1: Generating audio...")
        
        audio_segments = {}
        base_speed = 1.15  # Start with 1.15x
        
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
            
            logger.info(f"  {scene}: {duration:.2f}s")

        # Check total duration
        total_duration = sum(seg['duration'] for seg in audio_segments.values())
        logger.info(f"\nInitial total: {total_duration:.2f}s")

        # Adjust if needed
        if total_duration > self.TARGET_DURATION:
            # Need to speed up
            speedup_factor = total_duration / self.TARGET_DURATION
            
            if speedup_factor > self.MAX_SPEED / base_speed:
                logger.warning(f"Content too long! Would need {speedup_factor:.2f}x speed")
                logger.info(f"Limiting to max {self.MAX_SPEED}x speed")
                speedup_factor = self.MAX_SPEED / base_speed
            
            logger.info(f"Speeding up audio by {speedup_factor:.2f}x")
            
            # Speed up all segments
            for scene, seg in audio_segments.items():
                sped_up = seg['audio'].speedup(playback_speed=speedup_factor)
                seg['audio'] = sped_up
                seg['duration'] = len(sped_up) / 1000.0
                logger.info(f"  {scene}: {seg['duration']:.2f}s (sped up)")
            
            total_duration = sum(seg['duration'] for seg in audio_segments.values())

        # Concatenate audio
        logger.info("\nSTEP 2: Mixing audio...")
        combined = AudioSegment.empty()
        
        for scene in ["hook", "meaning", "action", "cta"]:
            combined += audio_segments[scene]['audio']

        # Pad to EXACTLY 17 seconds if short
        target_ms = int(self.TARGET_DURATION * 1000)
        if len(combined) < target_ms:
            silence_needed = target_ms - len(combined)
            combined = combined + AudioSegment.silent(duration=silence_needed)
            logger.info(f"Added {silence_needed/1000:.2f}s silence to reach 17s")
        elif len(combined) > target_ms:
            # Trim if slightly over
            combined = combined[:target_ms]
            logger.info(f"Trimmed to exactly 17s")

        # Export voiceover
        temp_voice = Path("output/audio") / f"temp_voice_{timestamp}.mp3"
        combined.export(str(temp_voice), format='mp3')
        
        final_duration = len(combined) / 1000.0
        logger.info(f"✅ Final audio duration: {final_duration:.2f}s")

        # Add music
        final_audio = Path("output/audio") / f"final_{timestamp}.mp3"
        self._add_music(temp_voice, final_audio, final_duration)
        temp_voice.unlink()

        # Create background
        logger.info("\nSTEP 3: Creating 4K background...")
        background = self._create_background_clip(category, self.TARGET_DURATION)

        # Create text overlays
        logger.info("\nSTEP 4: Creating text overlays...")
        
        text_clips = []
        current_time = 0.0

        for scene in ["hook", "meaning", "action", "cta"]:
            seg = audio_segments[scene]
            
            logger.info(f"  {scene}: {seg['duration']:.2f}s @ {current_time:.2f}s")
            
            text_img = self._create_text_overlay(
                text=seg['text'],
                category=category,
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
        final = final.with_duration(self.TARGET_DURATION)

        logger.info("\nSTEP 6: Exporting...")
        
        final.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            preset='medium',
            bitrate='8000k'  # Higher bitrate for better quality
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
        logger.info(f"Duration: EXACTLY {self.TARGET_DURATION}s")
        logger.info(f"Quality: 4K backgrounds, clean HD export")
        logger.info("="*70 + "\n")

        return str(output_path)

    def _add_music(self, voiceover_path: Path, output_path: Path, duration: float):
        """Add background music."""
        import shutil
        import random

        music_dir = Path("music")
        
        if not music_dir.exists() or not list(music_dir.glob("*.mp3")):
            logger.warning("No music - voiceover only")
            shutil.copy(voiceover_path, output_path)
            return

        music_files = list(music_dir.glob("*.mp3"))
        music_file = random.choice(music_files)
        logger.info(f"🎵 Music: {music_file.name}")

        try:
            voice = AudioSegment.from_file(str(voiceover_path))
            music = AudioSegment.from_file(str(music_file))

            # Reduce volume
            music = music - 14  # 20% volume
            
            # Match duration
            voice_ms = len(voice)
            
            if len(music) > voice_ms:
                music = music[:voice_ms]
            else:
                loops = (voice_ms // len(music)) + 1
                music = music * loops
                music = music[:voice_ms]

            # Mix
            mixed = music.overlay(voice)
            mixed.export(str(output_path), format='mp3', bitrate='192k')
            
            logger.info("✅ Mixed with music at 20%")

        except Exception as e:
            logger.error(f"Music failed: {e}")
            shutil.copy(voiceover_path, output_path)


def main():
    """Test generator."""
    generator = VideoGenerator()

    test_content = {
        "hook": "Seeing angel number 17 everywhere?",
        "meaning": "This powerful number signals new beginnings and spiritual awakening",
        "action": "Trust your intuition. The universe is guiding you toward your highest path",
        "cta": "Follow @the17project for daily spiritual guidance"
    }

    video = generator.generate_reel(
        content=test_content,
        category="angel_numbers"
    )

    print(f"\n✅ Generated: {video}")


if __name__ == "__main__":
    main()
