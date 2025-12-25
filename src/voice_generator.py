"""
Voice Generator - Creates deep male storytelling voice
Uses Google Cloud Text-to-Speech Neural2 voices
"""

import os
from google.cloud import texttospeech

class VoiceGenerator:
    def __init__(self):
        # Set up Google Cloud credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.client = texttospeech.TextToSpeechClient()
        
        # Deep male voice - storytelling style
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-D",  # Deep male voice
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        
        # Audio config - high quality
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9,  # Slightly slower for impact
            pitch=-2.0  # Deeper tone
        )
    
    def generate_speech(self, text, output_path):
        """Generate speech from text and save to file"""
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=self.voice,
            audio_config=self.audio_config
        )
        
        # Save audio file
        with open(output_path, 'wb') as out:
            out.write(response.audio_content)
        
        print(f"✅ Audio saved: {output_path}")
        return output_path

