"""
Audio Generator - IMPROVED WITH MULTIPLE VOICES

Features:
- 3 different Google Neural2 voices for variety
- Random voice selection per video
- Better audio quality
- Each voice has unique personality
"""

import os
import logging
import random
from typing import Optional
from pathlib import Path
from google.cloud import texttospeech

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AudioGenerator:
    """Generate voiceovers with MULTIPLE Neural2 voices for variety."""

    # VOICE VARIETY - 20 Most Popular Instagram Voices (10 Female, 10 Male)
    VOICES = {
        # TOP 10 FEMALE VOICES (Instagram favorites)
        "warm_friendly_female": {
            "name": "en-US-Neural2-F",
            "description": "Warm, friendly female - most popular on spiritual/manifestation content",
            "pitch": 0.0,
            "gender": texttospeech.SsmlVoiceGender.FEMALE
        },
        "calm_meditation_female": {
            "name": "en-US-Neural2-C",
            "description": "Calm, soothing female - meditation and mindfulness standard",
            "pitch": -1.0,
            "gender": texttospeech.SsmlVoiceGender.FEMALE
        },
        "energetic_uplifting_female": {
            "name": "en-US-Neural2-H",
            "description": "Energetic, enthusiastic female - manifestation content favorite",
            "pitch": 1.5,
            "gender": texttospeech.SsmlVoiceGender.FEMALE
        },
        "conversational_natural_female": {
            "name": "en-US-Neural2-A",
            "description": "Natural conversational female - like talking to a friend",
            "pitch": 0.0,
            "gender": texttospeech.SsmlVoiceGender.FEMALE
        },
        "clear_pleasant_female": {
            "name": "en-US-Neural2-G",
            "description": "Clear, pleasant female - professional yet approachable",
            "pitch": 0.5,
            "gender": texttospeech.SsmlVoiceGender.FEMALE
        },
        "soft_gentle_female": {
            "name": "en-US-Neural2-E",
            "description": "Soft, gentle female - peaceful and comforting",
            "pitch": -0.5,
            "gender": texttospeech.SsmlVoiceGender.FEMALE
        },
        "studio_narrator_female": {
            "name": "en-US-Studio-O",
            "description": "Professional narrator female - documentary style",
            "pitch": 0.0,
            "gender": texttospeech.SsmlVoiceGender.FEMALE
        },
        "storyteller_female": {
            "name": "en-US-Studio-Q",
            "description": "Soft storyteller female - engaging and warm",
            "pitch": 0.0,
            "gender": texttospeech.SsmlVoiceGender.FEMALE
        },
        "smooth_wavenet_female": {
            "name": "en-US-Wavenet-A",
            "description": "Smooth, polished female - high quality classic",
            "pitch": 0.0,
            "gender": texttospeech.SsmlVoiceGender.FEMALE
        },
        "professional_wavenet_female": {
            "name": "en-US-Wavenet-C",
            "description": "Professional female - confident and clear",
            "pitch": 0.0,
            "gender": texttospeech.SsmlVoiceGender.FEMALE
        },
        
        # TOP 10 MALE VOICES (Instagram favorites)
        "professional_confident_male": {
            "name": "en-US-Neural2-D",
            "description": "Professional male - productivity and business content favorite",
            "pitch": 0.0,
            "gender": texttospeech.SsmlVoiceGender.MALE
        },
        "young_relatable_male": {
            "name": "en-US-Neural2-J",
            "description": "Young, relatable male - Gen Z appeal",
            "pitch": 0.5,
            "gender": texttospeech.SsmlVoiceGender.MALE
        },
        "deep_authoritative_male": {
            "name": "en-US-Neural2-I",
            "description": "Deep, mature male - authority and wisdom",
            "pitch": -1.0,
            "gender": texttospeech.SsmlVoiceGender.MALE
        },
        "casual_friendly_male": {
            "name": "en-US-Neural2-A",
            "description": "Casual, friendly male - conversational and easy",
            "pitch": 0.0,
            "gender": texttospeech.SsmlVoiceGender.MALE
        },
        "documentary_narrator_male": {
            "name": "en-US-Studio-M",
            "description": "Documentary narrator male - engaging storytelling",
            "pitch": 0.0,
            "gender": texttospeech.SsmlVoiceGender.MALE
        },
        "deep_wavenet_male": {
            "name": "en-US-Wavenet-B",
            "description": "Deep, rich male - commanding presence",
            "pitch": -0.5,
            "gender": texttospeech.SsmlVoiceGender.MALE
        },
        "clear_professional_male": {
            "name": "en-US-Wavenet-D",
            "description": "Clear, professional male - news anchor quality",
            "pitch": 0.0,
            "gender": texttospeech.SsmlVoiceGender.MALE
        },
        "mature_experienced_male": {
            "name": "en-US-Wavenet-I",
            "description": "Mature, experienced male - wise and trustworthy",
            "pitch": -0.5,
            "gender": texttospeech.SsmlVoiceGender.MALE
        },
        "casual_wavenet_male": {
            "name": "en-US-Wavenet-J",
            "description": "Casual, approachable male - everyday conversation",
            "pitch": 0.5,
            "gender": texttospeech.SsmlVoiceGender.MALE
        },
        "versatile_male": {
            "name": "en-US-Neural2-J",
            "description": "Versatile male - adapts to any content style",
            "pitch": 0.0,
            "gender": texttospeech.SsmlVoiceGender.MALE
        }
    }

    def __init__(self):
        """Initialize audio generator with Google Cloud Neural2."""
        # Google Cloud credentials from environment
        self.client = texttospeech.TextToSpeechClient()
        
        logger.info("AudioGenerator initialized with 20 Neural2 voices (10 female, 10 male)")
        logger.info("Voices rotate automatically for maximum variety")
        for voice_key, voice_info in self.VOICES.items():
            logger.info(f"  - {voice_key}: {voice_info['description']}")

    def generate_voiceover(
        self,
        text: str,
        output_path: str,
        speed_factor: float = 1.15,
        voice_key: Optional[str] = None
    ) -> str:
        """
        Generate voiceover using Google Cloud Neural2 TTS.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save MP3 file
            speed_factor: Speed multiplier (1.0 = normal, 1.15 = 15% faster)
            voice_key: Specific voice to use (or None for random)
        
        Returns:
            Path to generated audio file
        """
        try:
            # Pick random voice if not specified
            if voice_key is None or voice_key not in self.VOICES:
                voice_key = random.choice(list(self.VOICES.keys()))
            
            voice_config = self.VOICES[voice_key]
            
            logger.info(f"Generating Neural2 voiceover:")
            logger.info(f"  Voice: {voice_key} ({voice_config['description']})")
            logger.info(f"  Speed: {speed_factor}x")
            
            # Configure voice
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name=voice_config["name"],
                ssml_gender=voice_config["gender"]
            )
            
            # Prepare synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Audio config with speed and pitch
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speed_factor,
                pitch=voice_config["pitch"],
                effects_profile_id=["small-bluetooth-speaker-class-device"]
            )
            
            # Generate speech
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
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

    def get_random_voice_key(self) -> str:
        """Get random voice key for variety."""
        return random.choice(list(self.VOICES.keys()))


def main():
    """Test audio generator with all voices."""
    generator = AudioGenerator()

    test_text = "Angel number 717 signals powerful spiritual awakening and transformation in your life right now."

    print("\n" + "="*70)
    print("TESTING NEURAL2 VOICE VARIETY")
    print("="*70)

    for voice_key, voice_info in generator.VOICES.items():
        print(f"\n🎤 Testing: {voice_key}")
        print(f"   {voice_info['description']}")
        
        output_path = f"test_{voice_key}.mp3"
        
        generator.generate_voiceover(
            text=test_text,
            output_path=output_path,
            speed_factor=1.15,
            voice_key=voice_key
        )
        
        print(f"   ✅ Saved: {output_path}")

    print("\n" + "="*70)
    print("Test complete! Listen to the MP3 files to compare voices.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
