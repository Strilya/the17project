"""
Audio Generator Module

This module handles generating and optimizing voiceovers for Instagram Reels.
It uses gTTS for text-to-speech and pydub for audio speed optimization.

Main functionality:
- Generate voiceovers with gTTS
- Speed up audio by 15% for better pacing
- Rotate TLD accents for variety
- Optimize audio quality for Instagram
"""

import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
from gtts import gTTS
from pydub import AudioSegment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AudioGenerator:
    """
    Generates optimized voiceovers for Instagram Reels.

    Features:
    - Text-to-speech with gTTS
    - 15% speed increase for better pacing
    - Daily TLD rotation for accent variety
    - Smooth audio transitions
    """

    def __init__(self):
        """Initialize the AudioGenerator with rotating TLD accents."""
        # Rotate TLD daily for accent variety
        self.tld_options = ['com', 'co.uk', 'com.au', 'co.in']
        self.current_tld = self._get_daily_tld()
        logger.info(f"AudioGenerator initialized with TLD: {self.current_tld}")

    def _get_daily_tld(self) -> str:
        """
        Get TLD that rotates daily for accent variety.

        Returns:
            TLD string (com, co.uk, com.au, or co.in)
        """
        # Rotate based on day of year
        day_of_year = datetime.now().timetuple().tm_yday
        index = day_of_year % len(self.tld_options)
        return self.tld_options[index]

    def generate_voiceover(
        self,
        text: str,
        output_path: str,
        speed_factor: float = 1.15
    ) -> str:
        """
        Generate optimized voiceover with speed adjustment.

        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            speed_factor: Speed multiplier (1.15 = 15% faster)

        Returns:
            Path to generated audio file
        """
        try:
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            # Generate initial audio with gTTS
            temp_path = output_path.replace('.mp3', '_temp.mp3')
            logger.info(f"Generating TTS audio with TLD: {self.current_tld}")

            tts = gTTS(text=text, lang='en', tld=self.current_tld, slow=False)
            tts.save(temp_path)

            # Load audio with pydub
            logger.info(f"Loading audio for speed optimization...")
            audio = AudioSegment.from_mp3(temp_path)

            # Speed up audio by specified factor
            logger.info(f"Speeding up audio by {speed_factor}x...")
            sped_up_audio = self._speedup_audio(audio, speed_factor)

            # Export optimized audio
            sped_up_audio.export(
                output_path,
                format="mp3",
                bitrate="128k",
                parameters=["-q:a", "2"]  # High quality
            )

            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            logger.info(f"Generated optimized voiceover: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate voiceover: {e}")
            raise

    def _speedup_audio(
        self,
        audio: AudioSegment,
        speed_factor: float = 1.15
    ) -> AudioSegment:
        """
        Speed up audio without changing pitch.

        Args:
            audio: AudioSegment to speed up
            speed_factor: Speed multiplier (1.15 = 15% faster)

        Returns:
            Sped up AudioSegment
        """
        # Use speedup with optimized parameters for smooth audio
        # chunk_size=150 and crossfade=25 prevent choppiness
        sped_up = audio.speedup(
            playback_speed=speed_factor,
            chunk_size=150,
            crossfade=25
        )
        return sped_up


def main():
    """
    Main function for testing AudioGenerator locally.

    Usage:
        python src/audio_generator.py
    """
    try:
        print("\n" + "="*70)
        print("TESTING AUDIO GENERATOR")
        print("="*70)

        # Initialize generator
        generator = AudioGenerator()

        # Test text
        test_text = "Seeing 17 everywhere? The universe is sending you a powerful message about new beginnings and spiritual awakening."

        print(f"\nGenerating test audio with TLD: {generator.current_tld}")
        print(f"Text: {test_text}")

        # Generate audio
        output_path = "output/audio/test_audio.mp3"
        result_path = generator.generate_voiceover(
            text=test_text,
            output_path=output_path
        )

        print(f"\n✅ Audio generated: {result_path}")

        # Check file exists
        if Path(result_path).exists():
            size_kb = Path(result_path).stat().st_size / 1024
            print(f"   File size: {size_kb:.2f} KB")

            # Load and check duration
            audio = AudioSegment.from_mp3(result_path)
            duration = len(audio) / 1000.0  # Convert ms to seconds
            print(f"   Duration: {duration:.2f} seconds")

        print("\n" + "="*70)
        print("AUDIO GENERATOR TEST COMPLETE")
        print("="*70)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
