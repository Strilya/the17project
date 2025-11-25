"""
Video Generator Module

This module handles the creation of 17-second Instagram Reels for The17Project.
It generates videos with topic-based color palettes, voiceovers, and 4-scene structure.

Main functionality:
- Generate 4 scenes: hook (3s), meaning (5s), action (5s), cta (4s)
- Apply topic-based color palettes (angel_numbers, productivity, manifestation, spiritual_growth)
- Create voiceovers using Google Text-to-Speech
- Add animations (fade, slide, zoom)
- Apply branding/watermarks
- Export as Instagram-ready MP4 files
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

# MoviePy for video composition (version 2.x)
try:
    # Try moviepy 2.x imports
    from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, VideoFileClip, ColorClip
except ImportError:
    # Fallback to moviepy 1.x imports
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, VideoFileClip, ColorClip

# gTTS for text-to-speech
from gtts import gTTS

# NumPy for array operations
import numpy as np

# BackgroundManager for Pexels video backgrounds
from background_manager import BackgroundManager

# AudioGenerator for optimized voiceovers
from audio_generator import AudioGenerator

# MusicManager for background music
from music_manager import MusicManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoGenerator:
    """
    Generates 17-second Instagram Reels with topic-based styling.

    This class handles the entire video creation workflow:
    1. Load video configuration and color palettes
    2. Create 4 scenes (hook, meaning, action, cta) with text and backgrounds
    3. Generate voiceovers for each scene
    4. Apply animations and transitions
    5. Composite final video with audio
    6. Export as Instagram-ready MP4
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the VideoGenerator.

        Args:
            config_path: Path to video_config.json file
        """
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "video_config.json"

        self.config = self._load_config(config_path)

        # Extract settings for easy access
        self.video_settings = self.config["video_settings"]
        self.scene_timings = self.config["scene_timings"]
        self.color_palettes = self.config["color_palettes"]
        self.fonts = self.config["fonts"]
        self.animations = self.config["animations"]
        self.audio_settings = self.config["audio"]
        self.branding = self.config["branding"]

        # Resolution
        self.width = self.video_settings["resolution"][0]
        self.height = self.video_settings["resolution"][1]
        self.fps = self.video_settings["fps"]

        # Create output folders
        self._create_output_folders()

        # Initialize background manager for Pexels video backgrounds
        self.background_manager = BackgroundManager()

        # Initialize audio generator for optimized voiceovers
        self.audio_generator = AudioGenerator()

        # Initialize music manager for background music
        music_dir = self.audio_settings.get("background_music", {}).get("music_dir", "music")
        self.music_manager = MusicManager(music_dir=music_dir)

        logger.info("VideoGenerator initialized successfully")
        logger.info(f"Resolution: {self.width}x{self.height} @ {self.fps}fps")

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """
        Load video configuration from JSON file.

        Args:
            config_path: Path to video_config.json

        Returns:
            Dictionary containing video configuration
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise

    def _create_output_folders(self) -> None:
        """Create output folders for videos and audio if they don't exist."""
        video_folder = Path(self.video_settings["output_folder"])
        audio_folder = Path(self.audio_settings["output_folder"])

        video_folder.mkdir(parents=True, exist_ok=True)
        audio_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"Output folders ready: {video_folder}, {audio_folder}")

    def _create_gradient_background(self, category: str) -> Image.Image:
        """
        Create a vertical gradient background for a given category.

        Args:
            category: Content category (angel_numbers, productivity, etc.)

        Returns:
            PIL Image with gradient background
        """
        palette = self.color_palettes[category]

        # Create image
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        # Convert hex colors to RGB
        start_color = tuple(int(palette["gradient_start"][i:i+2], 16) for i in (1, 3, 5))
        end_color = tuple(int(palette["gradient_end"][i:i+2], 16) for i in (1, 3, 5))

        # Draw gradient from top to bottom
        for y in range(self.height):
            # Calculate color at this y position
            ratio = y / self.height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)

            # Draw horizontal line
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        return img

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB tuple.

        Args:
            hex_color: Hex color string (e.g., "#FFD700")

        Returns:
            RGB tuple (r, g, b)
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _create_text_scene(
        self,
        text: str,
        category: str,
        scene_type: str,
        subtitle: Optional[str] = None
    ) -> Image.Image:
        """
        Create a scene with text on gradient background.

        Args:
            text: Main text to display
            category: Content category for color palette
            scene_type: Type of scene (hook, meaning, action, cta)
            subtitle: Optional subtitle text

        Returns:
            PIL Image with text on gradient background
        """
        # Create gradient background
        img = self._create_gradient_background(category)
        draw = ImageDraw.Draw(img)

        palette = self.color_palettes[category]

        # Load fonts (use default if custom fonts not available)
        try:
            primary_font = ImageFont.truetype(
                "/System/Library/Fonts/Helvetica.ttc",
                self.fonts["primary"]["size"][scene_type]
            )
            secondary_font = ImageFont.truetype(
                "/System/Library/Fonts/Helvetica.ttc",
                self.fonts["secondary"]["size"][scene_type]
            )
        except:
            # Fallback to default font
            primary_font = ImageFont.load_default()
            secondary_font = ImageFont.load_default()
            logger.warning("Using default fonts (custom fonts not found)")

        # Text colors
        primary_color = self._hex_to_rgb(palette["primary_text"])
        secondary_color = self._hex_to_rgb(palette["secondary_text"])

        # Calculate text position (centered)
        # Word wrap for long text
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=primary_font)
            if bbox[2] - bbox[0] < self.width - 100:  # 50px margin on each side
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        # Calculate total text height
        line_height = self.fonts["primary"]["size"][scene_type] + 20
        total_height = len(lines) * line_height

        # Starting Y position (centered vertically)
        start_y = (self.height - total_height) // 2

        # Draw each line centered
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=primary_font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = start_y + (i * line_height)

            # Draw text with outline for better readability
            outline_color = (0, 0, 0)
            for offset_x, offset_y in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                draw.text((x + offset_x, y + offset_y), line, font=primary_font, fill=outline_color)
            draw.text((x, y), line, font=primary_font, fill=primary_color)

        # Draw subtitle if provided
        if subtitle:
            bbox = draw.textbbox((0, 0), subtitle, font=secondary_font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = start_y + total_height + 40

            # Draw with outline
            for offset_x, offset_y in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                draw.text((x + offset_x, y + offset_y), subtitle, font=secondary_font, fill=(0, 0, 0))
            draw.text((x, y), subtitle, font=secondary_font, fill=secondary_color)

        # Add watermark
        self._add_watermark(draw, palette)

        return img

    def _add_watermark(self, draw: ImageDraw.ImageDraw, palette: Dict[str, str]) -> None:
        """
        Add watermark to the image.

        Args:
            draw: ImageDraw object
            palette: Color palette for the category
        """
        watermark_text = self.branding["watermark_text"]
        watermark_size = self.branding["watermark_size"]

        try:
            watermark_font = ImageFont.truetype(
                "/System/Library/Fonts/Helvetica.ttc",
                watermark_size
            )
        except:
            watermark_font = ImageFont.load_default()

        # Calculate position (bottom right)
        bbox = draw.textbbox((0, 0), watermark_text, font=watermark_font)
        text_width = bbox[2] - bbox[0]
        x = self.width - text_width - 30
        y = self.height - watermark_size - 30

        # Draw with semi-transparency effect (using white with outline)
        color = self._hex_to_rgb(palette["secondary_text"])
        draw.text((x, y), watermark_text, font=watermark_font, fill=color)

    def _generate_voiceover(self, text: str, output_path: str) -> str:
        """
        Generate optimized voiceover audio with 15% speed increase.

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file

        Returns:
            Path to generated audio file
        """
        try:
            # Use AudioGenerator for optimized voiceover with speed adjustment
            return self.audio_generator.generate_voiceover(
                text=text,
                output_path=output_path,
                speed_factor=1.15  # 15% faster for better pacing
            )
        except Exception as e:
            logger.error(f"Failed to generate voiceover: {e}")
            raise

    def _generate_all_audio(
        self,
        content: Dict[str, Any],
        timestamp: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate all audio segments first and measure their actual durations.

        This enables dynamic timing where text overlays match actual audio length
        instead of using fixed timings.

        Args:
            content: Content dictionary with scene text (hook, meaning, action, cta)
            timestamp: Timestamp string for unique filenames

        Returns:
            Dictionary mapping scene types to their audio info:
            {
                'hook': {'path': '...', 'duration': 2.3, 'text': '...'},
                'meaning': {'path': '...', 'duration': 5.1, 'text': '...'},
                ...
            }
        """
        audio_segments = {}
        total_duration = 0.0

        logger.info("Generating all audio segments with dynamic timing...")

        for scene_type in ["hook", "meaning", "action", "cta"]:
            # Get text for this scene
            scene_text = content.get(scene_type, "")
            if not scene_text:
                logger.warning(f"No text for {scene_type} scene, using placeholder")
                scene_text = f"{scene_type.upper()}"

            # Generate audio file
            audio_path = Path(self.audio_settings["output_folder"]) / f"{scene_type}_{timestamp}.mp3"
            audio_path.parent.mkdir(parents=True, exist_ok=True)

            self._generate_voiceover(scene_text, str(audio_path))

            # Measure actual duration using pydub
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(audio_path))
            duration = len(audio) / 1000.0  # Convert ms to seconds

            audio_segments[scene_type] = {
                'path': str(audio_path),
                'duration': duration,
                'text': scene_text
            }

            total_duration += duration
            logger.info(f"  {scene_type}: {duration:.2f}s - {scene_text[:50]}...")

        logger.info(f"Total audio duration: {total_duration:.2f} seconds")

        return audio_segments

    def _validate_total_duration(
        self,
        audio_segments: Dict[str, Dict[str, Any]],
        target_duration: float = 17.0,
        max_duration: float = 17.5
    ) -> tuple[bool, float]:
        """
        Validate if total audio duration fits within target range.

        Args:
            audio_segments: Dictionary of audio segment info from _generate_all_audio
            target_duration: Target duration in seconds (default 17.0)
            max_duration: Maximum acceptable duration (default 17.5)

        Returns:
            Tuple of (is_valid, total_duration)
            - is_valid: True if duration is acceptable, False if too long
            - total_duration: Actual total duration in seconds
        """
        total_duration = sum(seg['duration'] for seg in audio_segments.values())

        if total_duration > max_duration:
            logger.warning(f"Total audio duration ({total_duration:.2f}s) exceeds max ({max_duration:.2f}s)")
            return False, total_duration
        elif total_duration < target_duration * 0.8:  # Less than 80% of target
            logger.warning(f"Total audio duration ({total_duration:.2f}s) is much shorter than target ({target_duration:.2f}s)")
            logger.info("This is acceptable - video will be shorter than target")

        logger.info(f"Audio duration validation: {total_duration:.2f}s (target: {target_duration:.2f}s) ✓")
        return True, total_duration

    def _create_background_clip(self, category: str, duration: float):
        """
        Create background video clip or gradient fallback.

        Args:
            category: Content category for color/video selection
            duration: Duration in seconds

        Returns:
            MoviePy clip for background
        """
        palette = self.color_palettes[category]

        # Try to get video background
        bg_video_path = self.background_manager.get_background_video(category)

        if bg_video_path and os.path.exists(bg_video_path):
            logger.info(f"Using video background: {bg_video_path}")

            try:
                # Load background video
                background = VideoFileClip(bg_video_path)

                # Resize to fit our dimensions (1080x1920)
                if background.h != self.height:
                    background = background.resized(height=self.height)

                if background.w > self.width:
                    # Crop to center if too wide
                    x_center = background.w / 2
                    background = background.cropped(x1=x_center - self.width/2, x2=x_center + self.width/2)

                # Loop if shorter than duration
                if background.duration < duration:
                    # Calculate how many loops needed
                    n_loops = int(duration / background.duration) + 1
                    background = background.looped(n_loops)

                # Trim to exact duration
                background = background.subclipped(0, duration)

                # Add semi-transparent color overlay to maintain brand colors
                overlay_color = self._hex_to_rgb(palette["gradient_start"])
                overlay = ColorClip(
                    size=(self.width, self.height),
                    color=overlay_color,
                    duration=duration
                ).with_opacity(0.4)

                # Composite background + overlay
                base_clip = CompositeVideoClip([background, overlay])

                logger.info("Video background created with color overlay")
                return base_clip

            except Exception as e:
                logger.error(f"Failed to load video background: {e}")
                logger.info("Falling back to gradient")

        # Fallback to gradient
        logger.info("Using gradient background")
        gradient_img = self._create_gradient_background(category)
        return ImageClip(np.array(gradient_img), duration=duration)

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _create_transparent_text_overlay(
        self,
        text: str,
        category: str,
        scene_type: str
    ) -> Image.Image:
        """
        Create transparent text overlay (RGBA with transparent background).

        Args:
            text: Text to display
            category: Content category for color palette
            scene_type: Type of scene (hook, meaning, action, cta)

        Returns:
            PIL Image (RGBA) with transparent background and text
        """
        # Create transparent RGBA image
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        palette = self.color_palettes[category]

        # Load fonts - try bundled font first, then fallback to default
        try:
            # Try bundled DejaVu Sans Bold font (cross-platform)
            font_path = Path(__file__).parent.parent / "fonts" / "DejaVuSans-Bold.ttf"
            primary_font = ImageFont.truetype(
                str(font_path),
                self.fonts["primary"]["size"][scene_type]
            )
            logger.debug(f"Loaded bundled font: {font_path}")
        except Exception as e:
            # Fallback to default font if bundled font not found
            primary_font = ImageFont.load_default()
            logger.warning(f"Could not load bundled font, using default: {e}")

        # Text colors
        primary_color = self._hex_to_rgb(palette["primary_text"])

        # Word wrap for long text
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

        # Calculate total text height
        line_height = self.fonts["primary"]["size"][scene_type] + 20
        total_height = len(lines) * line_height

        # Starting Y position (centered vertically)
        start_y = (self.height - total_height) // 2

        # Draw each line centered with outline for readability
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=primary_font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = start_y + (i * line_height)

            # Draw text with black outline for better readability
            outline_color = (0, 0, 0, 255)
            for offset_x, offset_y in [(-3, -3), (-3, 3), (3, -3), (3, 3)]:
                draw.text((x + offset_x, y + offset_y), line, font=primary_font, fill=outline_color)

            # Draw main text
            primary_color_rgba = primary_color + (255,)  # Add alpha channel
            draw.text((x, y), line, font=primary_font, fill=primary_color_rgba)

        return img

    def generate_reel(
        self,
        content: Dict[str, Any],
        category: str,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate a complete Instagram Reel with dynamic timing and background music.

        NEW FEATURES:
        - Dynamic timing: Text overlays match actual audio duration (not fixed)
        - Background music: Spiritual ambient music mixed with voiceover

        Args:
            content: Dictionary containing video content with keys:
                - hook: Hook text
                - meaning: Meaning text
                - action: Action text
                - cta: Call-to-action text
            category: Content category (angel_numbers, productivity, etc.)
            output_filename: Optional custom filename

        Returns:
            Path to generated video file
        """
        try:
            logger.info("Starting Instagram Reel generation with dynamic timing...")
            logger.info(f"Category: {category}")

            # Generate timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Generate output filename if not provided
            if output_filename is None:
                output_filename = f"reel_{category}_{timestamp}.mp4"

            output_path = Path(self.video_settings["output_folder"]) / output_filename

            # ========================================================================
            # STEP 1: Generate all audio segments first and measure actual durations
            # ========================================================================
            logger.info("\n" + "="*70)
            logger.info("STEP 1: Generating audio with dynamic timing")
            logger.info("="*70)

            audio_segments = self._generate_all_audio(content, timestamp)

            # ========================================================================
            # STEP 2: Validate total audio duration
            # ========================================================================
            logger.info("\n" + "="*70)
            logger.info("STEP 2: Validating total audio duration")
            logger.info("="*70)

            dynamic_timing_config = self.audio_settings.get("dynamic_timing", {})
            target_duration = dynamic_timing_config.get("target_duration", 17.0)
            max_duration = dynamic_timing_config.get("max_duration", 17.5)

            is_valid, total_audio_duration = self._validate_total_duration(
                audio_segments,
                target_duration=target_duration,
                max_duration=max_duration
            )

            if not is_valid:
                logger.warning(f"Audio duration ({total_audio_duration:.2f}s) exceeds maximum ({max_duration:.2f}s)")
                logger.info("Continuing anyway - video will be slightly longer")

            # ========================================================================
            # STEP 3: Get background music and mix with voiceover
            # ========================================================================
            logger.info("\n" + "="*70)
            logger.info("STEP 3: Adding background music")
            logger.info("="*70)

            music_config = self.audio_settings.get("background_music", {})
            music_enabled = music_config.get("enabled", False)
            music_volume = music_config.get("volume", 0.25)

            # Collect all audio segment paths
            audio_file_paths = [seg['path'] for seg in audio_segments.values()]

            # Path for final mixed audio (voiceover + background music)
            final_audio_path = Path(self.audio_settings["output_folder"]) / f"final_mixed_{timestamp}.mp3"

            if music_enabled:
                # Get background music
                music_styles = music_config.get("styles", ["meditation"])
                music_style = random.choice(music_styles)
                music_path = self.music_manager.get_background_music(
                    duration=total_audio_duration,
                    style=music_style
                )

                # Mix voiceover with background music
                self.music_manager.concatenate_and_mix(
                    audio_segments=audio_file_paths,
                    music_path=music_path,
                    output_path=str(final_audio_path),
                    music_volume=music_volume
                )
                logger.info(f"✅ Mixed audio with background music at {music_volume*100:.0f}% volume")
            else:
                # No background music - just concatenate voiceovers
                logger.info("Background music disabled - using voiceover only")
                from pydub import AudioSegment
                combined = AudioSegment.empty()
                for audio_path in audio_file_paths:
                    combined += AudioSegment.from_file(audio_path)
                combined.export(str(final_audio_path), format='mp3')

            # ========================================================================
            # STEP 4: Create background video clip
            # ========================================================================
            logger.info("\n" + "="*70)
            logger.info("STEP 4: Creating background video")
            logger.info("="*70)

            background_clip = self._create_background_clip(category, total_audio_duration)

            # ========================================================================
            # STEP 5: Create text overlays using ACTUAL audio durations
            # ========================================================================
            logger.info("\n" + "="*70)
            logger.info("STEP 5: Creating text overlays with dynamic timing")
            logger.info("="*70)

            text_overlays = []
            current_time = 0.0

            for scene_type in ["hook", "meaning", "action", "cta"]:
                segment_info = audio_segments[scene_type]
                scene_text = segment_info['text']
                # Use ACTUAL audio duration (not fixed timing)
                duration = segment_info['duration']

                logger.info(f"  {scene_type}: {duration:.2f}s @ {current_time:.2f}s")

                # Create transparent text overlay
                text_img = self._create_transparent_text_overlay(
                    text=scene_text,
                    category=category,
                    scene_type=scene_type
                )

                # Save temporarily
                temp_img_path = Path("output") / f"temp_{scene_type}_{timestamp}_transparent.png"
                temp_img_path.parent.mkdir(exist_ok=True)
                text_img.save(temp_img_path)

                # Create clip with DYNAMIC timing (actual audio duration)
                text_clip = ImageClip(str(temp_img_path), duration=duration, is_mask=False)
                text_clip = text_clip.with_start(current_time)

                text_overlays.append(text_clip)
                current_time += duration

            # ========================================================================
            # STEP 6: Composite video and add mixed audio
            # ========================================================================
            logger.info("\n" + "="*70)
            logger.info("STEP 6: Compositing final video")
            logger.info("="*70)

            all_clips = [background_clip] + text_overlays
            final_video = CompositeVideoClip(all_clips)

            # Add the mixed audio (voiceover + background music)
            final_audio_clip = AudioFileClip(str(final_audio_path))
            final_video = final_video.with_audio(final_audio_clip) if hasattr(final_video, 'with_audio') else final_video

            # ========================================================================
            # STEP 7: Export final video
            # ========================================================================
            logger.info("\n" + "="*70)
            logger.info("STEP 7: Exporting final video")
            logger.info("="*70)

            logger.info(f"Exporting video to {output_path}...")
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                preset='medium'
            )

            # ========================================================================
            # STEP 8: Clean up temporary files
            # ========================================================================
            logger.info("Cleaning up temporary files...")

            # Clean up audio segment files
            for segment_info in audio_segments.values():
                audio_path = Path(segment_info['path'])
                if audio_path.exists():
                    audio_path.unlink()

            # Clean up text overlay images
            for scene_type in ["hook", "meaning", "action", "cta"]:
                temp_img = Path("output") / f"temp_{scene_type}_{timestamp}_transparent.png"
                if temp_img.exists():
                    temp_img.unlink()

            # Clean up mixed audio file
            if final_audio_path.exists():
                final_audio_path.unlink()

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
            logger.info(f"Duration: {total_audio_duration:.2f} seconds")
            logger.info(f"Resolution: {self.width}x{self.height}")
            logger.info(f"Background music: {'enabled' if music_enabled else 'disabled'}")
            logger.info(f"Dynamic timing: enabled")
            logger.info("="*70 + "\n")

            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate video: {e}")
            raise


def main():
    """
    Main function for testing VideoGenerator locally.

    Usage:
        python src/video_generator.py
    """
    try:
        print("\n" + "="*70)
        print("TESTING VIDEO GENERATOR")
        print("="*70)

        # Initialize generator
        generator = VideoGenerator()

        # Test content for angel_numbers category
        test_content = {
            "hook": "See 717 everywhere?",
            "meaning": "Angel number 717 signals spiritual awakening and divine guidance",
            "action": "Trust your intuition. The universe is speaking to you",
            "cta": "Follow @the17project for daily angel numbers"
        }

        # Generate video
        print("\n--- Generating Test Video (angel_numbers) ---")
        video_path = generator.generate_reel(
            content=test_content,
            category="angel_numbers",
            output_filename="test_reel_717.mp4"
        )

        print("\n" + "="*70)
        print("SUCCESS: Video generated!")
        print(f"Location: {video_path}")
        print("="*70)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
