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
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

# PIL for image creation and text rendering
from PIL import Image, ImageDraw, ImageFont

# MoviePy for video composition
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    TextClip
)

# gTTS for text-to-speech
from gtts import gTTS

# NumPy for array operations
import numpy as np

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
        Generate voiceover audio from text using gTTS.

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file

        Returns:
            Path to generated audio file
        """
        try:
            tts = gTTS(
                text=text,
                lang=self.audio_settings["voice"]["language"],
                tld=self.audio_settings["voice"]["tld"],
                slow=self.audio_settings["voice"]["slow"]
            )
            tts.save(output_path)
            logger.info(f"Generated voiceover: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate voiceover: {e}")
            raise

    def generate_reel(
        self,
        content: Dict[str, Any],
        category: str,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate a complete 17-second Instagram Reel.

        Args:
            content: Dictionary containing video content with keys:
                - hook: Hook text (3 seconds)
                - meaning: Meaning text (5 seconds)
                - action: Action text (5 seconds)
                - cta: Call-to-action text (4 seconds)
            category: Content category (angel_numbers, productivity, etc.)
            output_filename: Optional custom filename

        Returns:
            Path to generated video file
        """
        try:
            logger.info("Starting 17-second Reel generation...")
            logger.info(f"Category: {category}")

            # Generate output filename if not provided
            if output_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"reel_{category}_{timestamp}.mp4"

            output_path = Path(self.video_settings["output_folder"]) / output_filename

            # Create scenes
            scenes = []
            audio_files = []

            for scene_type in ["hook", "meaning", "action", "cta"]:
                logger.info(f"Creating {scene_type} scene...")

                # Get text for this scene
                scene_text = content.get(scene_type, "")
                if not scene_text:
                    logger.warning(f"No text for {scene_type} scene, using placeholder")
                    scene_text = f"{scene_type.upper()}"

                # Create scene image
                scene_img = self._create_text_scene(
                    text=scene_text,
                    category=category,
                    scene_type=scene_type
                )

                # Save scene image temporarily
                temp_img_path = Path("output") / f"temp_{scene_type}.png"
                temp_img_path.parent.mkdir(exist_ok=True)
                scene_img.save(temp_img_path)

                # Create video clip from image
                duration = self.scene_timings[scene_type]
                clip = ImageClip(str(temp_img_path)).set_duration(duration)

                # Add fade transition
                fade_duration = self.animations["fade_duration"]
                clip = clip.fadein(fade_duration).fadeout(fade_duration)

                scenes.append(clip)

                # Generate voiceover for this scene
                audio_path = Path(self.audio_settings["output_folder"]) / f"temp_{scene_type}.mp3"
                self._generate_voiceover(scene_text, str(audio_path))
                audio_files.append(str(audio_path))

            # Concatenate all scenes
            logger.info("Compositing final video...")
            final_video = concatenate_videoclips(scenes, method="compose")

            # Load and concatenate audio
            audio_clips = []
            current_time = 0
            for i, audio_file in enumerate(audio_files):
                audio = AudioFileClip(audio_file)
                scene_duration = self.scene_timings[list(self.scene_timings.keys())[i]]

                # Trim or pad audio to match scene duration
                if audio.duration > scene_duration:
                    audio = audio.subclip(0, scene_duration)

                audio = audio.set_start(current_time)
                audio_clips.append(audio)
                current_time += scene_duration

            # Composite audio
            from moviepy.audio.AudioClip import CompositeAudioClip
            final_audio = CompositeAudioClip(audio_clips)
            final_video = final_video.set_audio(final_audio)

            # Export final video
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

            # Clean up temporary files
            for scene_type in ["hook", "meaning", "action", "cta"]:
                temp_img = Path("output") / f"temp_{scene_type}.png"
                if temp_img.exists():
                    temp_img.unlink()

                temp_audio = Path(self.audio_settings["output_folder"]) / f"temp_{scene_type}.mp3"
                if temp_audio.exists():
                    temp_audio.unlink()

            # Close clips
            for clip in scenes:
                clip.close()
            final_video.close()

            logger.info(f"Video generated successfully: {output_path}")
            logger.info(f"Duration: 17 seconds")
            logger.info(f"Resolution: {self.width}x{self.height}")

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
