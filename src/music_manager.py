"""
Music Manager Module

This module handles background music for Instagram Reels.
It manages spiritual/ambient music tracks and mixes them with voiceovers.

Main functionality:
- Manage bundled royalty-free spiritual music tracks
- Mix background music with voiceovers at appropriate volume levels
- Loop and trim music to match video duration
- Support for 432Hz, ambient, and meditation music styles
"""

import os
import logging
import random
from pathlib import Path
from typing import Optional, List
from pydub import AudioSegment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MusicManager:
    """
    Manages background music for Instagram Reels.

    Features:
    - Bundled royalty-free spiritual music
    - Audio mixing with volume control
    - Music looping and trimming
    - Multiple music styles (432Hz, ambient, meditation)
    """

    def __init__(self, music_dir: str = "music", cache_dir: str = "output/music_cache"):
        """
        Initialize the MusicManager.

        Args:
            music_dir: Directory containing bundled music files
            cache_dir: Directory for cached/processed music files
        """
        self.music_dir = Path(music_dir)
        self.cache_dir = Path(cache_dir)

        # Create directories if they don't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"MusicManager initialized")
        logger.info(f"Music directory: {self.music_dir}")
        logger.info(f"Cache directory: {self.cache_dir}")

    def get_background_music(
        self,
        duration: float = 17.0,
        style: Optional[str] = None
    ) -> Optional[str]:
        """
        Get background music file path, selecting randomly from available tracks.

        Args:
            duration: Target duration in seconds
            style: Music style preference (meditation, 432hz, ambient_space, spiritual_healing)

        Returns:
            Path to music file, or None if no music available
        """
        try:
            # Check if music directory exists
            if not self.music_dir.exists():
                logger.warning(f"Music directory not found: {self.music_dir}")
                logger.info("Creating music directory - add .mp3 files to enable background music")
                self.music_dir.mkdir(parents=True, exist_ok=True)
                return None

            # Find all MP3 files in music directory
            music_files = list(self.music_dir.glob("*.mp3"))

            if not music_files:
                logger.warning("No music files found in music directory")
                return None

            # Filter by style if provided (look for style in filename)
            if style:
                style_files = [f for f in music_files if style.lower() in f.name.lower()]
                if style_files:
                    music_files = style_files
                else:
                    logger.info(f"No music files found for style '{style}', using any available")

            # Randomly select a music file
            selected_file = random.choice(music_files)
            logger.info(f"Selected background music: {selected_file.name}")

            return str(selected_file)

        except Exception as e:
            logger.error(f"Failed to get background music: {e}")
            return None

    def mix_audio(
        self,
        voiceover_path: str,
        music_path: Optional[str],
        output_path: str,
        music_volume: float = 0.25
    ) -> str:
        """
        Mix voiceover with background music at specified volume.

        Args:
            voiceover_path: Path to voiceover audio file
            music_path: Path to background music file (None to skip mixing)
            output_path: Path to save mixed audio
            music_volume: Background music volume (0.0 to 1.0, default 0.25 = 25%)

        Returns:
            Path to mixed audio file
        """
        try:
            # If no music, just copy voiceover
            if not music_path or not os.path.exists(music_path):
                logger.info("No background music, using voiceover only")
                voice = AudioSegment.from_file(voiceover_path)
                voice.export(output_path, format='mp3', bitrate='128k')
                return output_path

            # Load both audio files
            logger.info(f"Mixing voiceover with background music...")
            voice = AudioSegment.from_file(voiceover_path)
            music = AudioSegment.from_file(music_path)

            # Calculate volume reduction in dB
            # 0.25 volume = -12dB, 0.30 volume = -10.5dB
            db_reduction = -1 * (20 * (1 - music_volume) * 2)  # Approximation
            music = music + db_reduction

            logger.info(f"Music volume: {music_volume * 100:.0f}% ({db_reduction:.1f}dB)")

            # Loop music if shorter than voice
            voice_duration = len(voice)
            if len(music) < voice_duration:
                loops_needed = (voice_duration // len(music)) + 1
                logger.info(f"Looping music {loops_needed} times to match voiceover duration")
                music = music * loops_needed

            # Trim music to match voice duration exactly
            music = music[:voice_duration]

            # Overlay voice on top of music (voice at full volume, music at background)
            mixed = music.overlay(voice)

            # Export with high quality
            mixed.export(
                output_path,
                format='mp3',
                bitrate='128k',
                parameters=["-q:a", "2"]  # High quality
            )

            logger.info(f"Mixed audio created: {output_path}")
            logger.info(f"Duration: {len(mixed) / 1000.0:.2f} seconds")

            return output_path

        except Exception as e:
            logger.error(f"Failed to mix audio: {e}")
            logger.warning("Falling back to voiceover only")
            # Fallback: just use voiceover
            voice = AudioSegment.from_file(voiceover_path)
            voice.export(output_path, format='mp3', bitrate='128k')
            return output_path

    def concatenate_and_mix(
        self,
        audio_segments: List[str],
        music_path: Optional[str],
        output_path: str,
        music_volume: float = 0.25
    ) -> str:
        """
        Concatenate multiple audio segments, then mix with background music.

        Args:
            audio_segments: List of paths to audio files to concatenate
            music_path: Path to background music file
            output_path: Path to save final mixed audio
            music_volume: Background music volume (0.0 to 1.0)

        Returns:
            Path to final mixed audio file
        """
        try:
            # Concatenate all voiceover segments
            logger.info(f"Concatenating {len(audio_segments)} audio segments...")
            combined_voice = AudioSegment.empty()

            for i, segment_path in enumerate(audio_segments):
                segment = AudioSegment.from_file(segment_path)
                combined_voice += segment
                logger.debug(f"Added segment {i+1}: {segment_path} ({len(segment)/1000.0:.2f}s)")

            # Save concatenated voiceover temporarily
            temp_voice_path = str(Path(output_path).parent / "temp_concatenated_voice.mp3")
            combined_voice.export(temp_voice_path, format='mp3')

            logger.info(f"Total voiceover duration: {len(combined_voice) / 1000.0:.2f} seconds")

            # Mix with background music
            result = self.mix_audio(
                voiceover_path=temp_voice_path,
                music_path=music_path,
                output_path=output_path,
                music_volume=music_volume
            )

            # Clean up temp file
            if os.path.exists(temp_voice_path):
                os.remove(temp_voice_path)

            return result

        except Exception as e:
            logger.error(f"Failed to concatenate and mix audio: {e}")
            raise


def main():
    """
    Main function for testing MusicManager locally.

    Usage:
        python src/music_manager.py
    """
    try:
        print("\n" + "="*70)
        print("TESTING MUSIC MANAGER")
        print("="*70)

        # Initialize manager
        manager = MusicManager()

        # Test 1: Get background music
        print("\nTest 1: Getting background music...")
        music_path = manager.get_background_music(duration=17.0, style="meditation")
        if music_path:
            print(f"✅ Found music: {music_path}")
        else:
            print("⚠️  No music files found - add .mp3 files to music/ directory")

        # Test 2: Create test voiceover
        print("\nTest 2: Creating test voiceover...")
        from gtts import gTTS
        test_text = "This is a test voiceover for background music mixing."
        test_voice_path = "output/audio/test_voice.mp3"
        os.makedirs("output/audio", exist_ok=True)
        tts = gTTS(text=test_text, lang='en', slow=False)
        tts.save(test_voice_path)
        print(f"✅ Created test voiceover: {test_voice_path}")

        # Test 3: Mix audio (if music available)
        if music_path:
            print("\nTest 3: Mixing voiceover with music...")
            output_path = "output/audio/test_mixed.mp3"
            result = manager.mix_audio(
                voiceover_path=test_voice_path,
                music_path=music_path,
                output_path=output_path,
                music_volume=0.25
            )
            print(f"✅ Mixed audio created: {result}")

            # Check file size
            if Path(result).exists():
                size_kb = Path(result).stat().st_size / 1024
                print(f"   File size: {size_kb:.2f} KB")

        print("\n" + "="*70)
        print("MUSIC MANAGER TEST COMPLETE")
        print("="*70)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
