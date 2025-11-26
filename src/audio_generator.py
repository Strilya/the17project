"""
Audio Generator Module

This module handles generating and optimizing voiceovers for Instagram Reels.
It uses Google Cloud Text-to-Speech Neural2 for high-quality voice generation.

Main functionality:
- Generate voiceovers with Google Neural2 voices
- Natural, human-like speech quality
- Adjustable speed (1.0-2.0x) with no quality loss
- Optimized audio for Instagram Reels
"""

import os
import logging
from pathlib import Path
from typing import Optional
from google.cloud import texttospeech
from pydub import AudioSegment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AudioGenerator:
    """
    Generates optimized voiceovers for Instagram Reels using Google Neural2.

    Features:
    - High-quality Neural2 text-to-speech
    - Natural, human-like voice (en-US-Neural2-F)
    - Native speed control with no quality loss
    - Professional audio output for Instagram
    """

    def __init__(self):
        """Initialize AudioGenerator with Google Cloud Neural2."""
        # Google Cloud credentials from environment (set in GitHub Actions)
        # GOOGLE_APPLICATION_CREDENTIALS should point to service account JSON

        self.client = texttospeech.TextToSpeechClient()

        # Configure voice - en-US-Neural2-F (warm, friendly female)
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-F",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )

        logger.info("AudioGenerator initialized with Google Neural2 voice (en-US-Neural2-F)")

    def generate_voiceover(
        self,
        text: str,
        output_path: str,
        speed_factor: float = 1.15
    ) -> str:
        """
        Generate voiceover using Google Cloud Neural2 TTS.

        Args:
            text: Text to convert to speech
            output_path: Path to save MP3 file
            speed_factor: Speed multiplier (1.0 = normal, 1.15 = 15% faster)

        Returns:
            Path to generated audio file
        """
        try:
            logger.info(f"Generating Neural2 voiceover at {speed_factor}x speed")

            # Prepare synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Audio config with speed
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speed_factor,
                pitch=0.0,
                effects_profile_id=["small-bluetooth-speaker-class-device"]
            )

            # Generate speech
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=audio_config
            )

            # Save to file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as out:
                out.write(response.audio_content)

            logger.info(f"✅ Neural2 voiceover saved: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Voiceover generation failed: {e}")
            raise


def main():
    """
    Main function for testing AudioGenerator locally.

    Usage:
        python src/audio_generator.py

    Note: Requires GOOGLE_APPLICATION_CREDENTIALS environment variable
    """
    try:
        print("\n" + "="*70)
        print("TESTING GOOGLE NEURAL2 TTS")
        print("="*70)

        # Initialize generator
        generator = AudioGenerator()

        # Test text
        test_text = "Seeing 17 everywhere? The universe is sending you a powerful message about new beginnings and spiritual awakening."

        print(f"\nGenerating Neural2 voiceover (en-US-Neural2-F)")
        print(f"Text: {test_text}")

        # Generate audio
        output_path = "output/audio/test_audio.mp3"
        result_path = generator.generate_voiceover(
            text=test_text,
            output_path=output_path,
            speed_factor=1.15
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
            print(f"   Quality: Google Neural2 (high-quality)")

        print("\n" + "="*70)
        print("NEURAL2 TTS TEST COMPLETE")
        print("="*70)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\nMake sure GOOGLE_APPLICATION_CREDENTIALS is set:")
        print("export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account.json'")
        raise


if __name__ == "__main__":
    main()
