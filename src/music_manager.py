"""
Music Manager Module - SIMPLIFIED

This module handles background music for Instagram Reels with a simple approach:
- User manually adds MP3 files to music/ folder
- System randomly selects one and mixes with voiceover
- Music is ALWAYS cut to exactly 17 seconds (never extends video)
- If no music files, gracefully fallback to voiceover only
"""

import os
import logging
import random
import shutil
from pathlib import Path
from typing import Optional
from pydub import AudioSegment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MusicManager:
    """
    Simple music manager for Instagram Reels.

    Features:
    - Manual music file setup (user adds MP3s to music/ folder)
    - Random selection from available tracks
    - FIXED 17-second duration (music cut/looped to fit)
    - Graceful fallback if no music available
    """

    def __init__(self, music_dir: str = "music"):
        """
        Initialize the MusicManager.

        Args:
            music_dir: Directory containing music MP3 files
        """
        self.music_dir = Path(music_dir)
        logger.info(f"MusicManager initialized with music directory: {self.music_dir}")

    def get_random_music_path(self) -> Optional[str]:
        """
        Get a random music file from music/ directory.

        Returns:
            Path to music file, or None if no music available
        """
        try:
            # Check if music directory exists
            if not self.music_dir.exists():
                logger.warning(f"Music directory not found: {self.music_dir}")
                return None

            # Find all MP3 files
            music_files = list(self.music_dir.glob("*.mp3"))

            if not music_files:
                logger.warning("No MP3 files found in music directory")
                return None

            # Randomly select one
            selected_file = random.choice(music_files)
            logger.info(f"Selected background music: {selected_file.name}")

            return str(selected_file)

        except Exception as e:
            logger.error(f"Failed to get music file: {e}")
            return None

    def mix_with_music(
        self,
        voiceover_path: str,
        output_path: str,
        target_duration: float = 17.0,
        music_volume: float = 0.25
    ) -> str:
        """
        Mix voiceover with background music. CRITICAL: Output is always exactly target_duration.

        Args:
            voiceover_path: Path to voiceover audio (concatenated scenes)
            output_path: Path to save final mixed audio
            target_duration: Fixed duration in seconds (default 17.0) - NEVER EXCEEDED
            music_volume: Background music volume (0.0 to 1.0, default 0.25 = 25%)

        Returns:
            Path to final mixed audio file (always exactly target_duration seconds)
        """
        try:
            # Get random music file
            music_path = self.get_random_music_path()

            # Load voiceover
            voice = AudioSegment.from_file(voiceover_path)

            # Convert target duration to milliseconds
            target_ms = int(target_duration * 1000)

            # CUT OR PAD voiceover to exactly target duration
            if len(voice) > target_ms:
                logger.warning(f"Voiceover ({len(voice)/1000:.1f}s) exceeds target ({target_duration}s), cutting to fit")
                voice = voice[:target_ms]
            elif len(voice) < target_ms:
                # Pad with silence if shorter
                silence_needed = target_ms - len(voice)
                silence = AudioSegment.silent(duration=silence_needed)
                voice = voice + silence
                logger.info(f"Padded voiceover with {silence_needed/1000:.1f}s silence to reach {target_duration}s")

            # If no music, just export voiceover at exact duration
            if not music_path:
                logger.info("No background music - using voiceover only")
                voice.export(output_path, format='mp3', bitrate='128k')
                logger.info(f"✅ Audio created: {target_duration}s (voiceover only)")
                return output_path

            # Load music
            music = AudioSegment.from_file(music_path)

            # Reduce music volume to 25% (-12dB approximation)
            music = music - 12
            logger.info(f"Reduced music volume to {music_volume * 100:.0f}% (-12dB)")

            # Loop music if shorter than target
            if len(music) < target_ms:
                loops_needed = (target_ms // len(music)) + 1
                logger.info(f"Looping music {loops_needed} times to reach {target_duration}s")
                music = music * loops_needed

            # CUT music to exactly target duration
            music = music[:target_ms]
            logger.info(f"Cut music to exactly {target_duration}s")

            # Overlay voiceover on top of music
            mixed = music.overlay(voice)

            # Double-check duration is exact
            if len(mixed) != target_ms:
                logger.warning(f"Mixed audio duration mismatch, forcing to {target_duration}s")
                mixed = mixed[:target_ms]

            # Export
            mixed.export(output_path, format='mp3', bitrate='128k')

            logger.info(f"✅ Mixed audio created: {len(mixed)/1000:.2f}s (voiceover + background music)")
            return output_path

        except Exception as e:
            logger.error(f"Music mixing failed: {e}")
            logger.warning("Falling back to voiceover only")

            # Fallback: just export voiceover at exact duration
            try:
                voice = AudioSegment.from_file(voiceover_path)
                target_ms = int(target_duration * 1000)

                # Ensure exact duration
                if len(voice) > target_ms:
                    voice = voice[:target_ms]
                elif len(voice) < target_ms:
                    silence = AudioSegment.silent(duration=target_ms - len(voice))
                    voice = voice + silence

                voice.export(output_path, format='mp3', bitrate='128k')
                return output_path
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                raise


def main():
    """
    Test the MusicManager.

    Usage:
        python src/music_manager.py
    """
    try:
        print("\n" + "="*70)
        print("TESTING MUSIC MANAGER")
        print("="*70)

        # Initialize
        manager = MusicManager()

        # Check for music files
        music_path = manager.get_random_music_path()
        if music_path:
            print(f"\n✅ Found music: {music_path}")
        else:
            print("\n⚠️  No music files found")
            print("   Add MP3 files to music/ directory to enable background music")

        # Create test voiceover
        print("\nCreating test voiceover...")
        from gtts import gTTS
        os.makedirs("output/audio", exist_ok=True)
        test_voice_path = "output/audio/test_voice.mp3"
        tts = gTTS(text="This is a test voiceover for the music mixer.", lang='en', tld='co.uk', slow=False)
        tts.save(test_voice_path)
        print(f"✅ Created test voiceover")

        # Test mixing
        print("\nMixing audio (fixed 17-second duration)...")
        output_path = "output/audio/test_mixed.mp3"
        result = manager.mix_with_music(
            voiceover_path=test_voice_path,
            output_path=output_path,
            target_duration=17.0,
            music_volume=0.25
        )

        # Verify duration
        final_audio = AudioSegment.from_file(result)
        duration = len(final_audio) / 1000.0
        print(f"✅ Final audio duration: {duration:.2f} seconds")

        if abs(duration - 17.0) < 0.1:
            print("✅ Duration is exactly 17 seconds!")
        else:
            print(f"⚠️  Duration mismatch: expected 17.0s, got {duration:.2f}s")

        print("\n" + "="*70)
        print("MUSIC MANAGER TEST COMPLETE")
        print("="*70)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
