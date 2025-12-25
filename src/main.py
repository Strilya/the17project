"""
The17Project - Angel Numbers Content Generator
Generates 3 videos daily with rotating content styles
"""

import os
import random
from dotenv import load_dotenv
from datetime import datetime
from content_generator import ContentGenerator
from voice_generator import VoiceGenerator
from video_generator import VideoGenerator

# Load environment variables
load_dotenv()

def main():
    print("=" * 70)
    print("THE17PROJECT - ANGEL NUMBERS CONTENT GENERATOR")
    print("=" * 70)
    print(f"Started: {datetime.now()}")
    print()
    
    # Initialize generators
    content_gen = ContentGenerator()
    voice_gen = VoiceGenerator()
    video_gen = VideoGenerator()
    
    # Get random angel number
    angel_number = random.choice(content_gen.angel_numbers)
    
    print(f"📊 Generating content for angel number: {angel_number}")
    print()
    
    # Generate 3 different styles
    styles = [
        ("storytelling", "Deep Storytelling"),
        ("practical", "Practical Tips"),
        ("insights", "Spiritual Insights")
    ]
    
    for style_id, style_name in styles:
        print(f"🎬 Creating {style_name} video...")
        
        # Generate content
        if style_id == "storytelling":
            content = content_gen.generate_storytelling(angel_number)
        elif style_id == "practical":
            content = content_gen.generate_practical(angel_number)
        else:
            content = content_gen.generate_insights(angel_number)
        
        print(f"   ✅ Content generated")
        print(f"   Hook: {content['hook'][:50]}...")
        
        # Combine all text for voice generation
        full_text = f"{content['hook']}. {content['meaning']}. {content['action']}. {content['cta']}"
        
        # Generate voice
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        voice_path = f"output/voice_{style_id}_{timestamp}.mp3"
        voice_gen.generate_speech(full_text, voice_path)
        
        # TODO: Generate video with background, text overlays, music
        print(f"   ⏳ Video generation (coming next)...")
        print()
    
    print("=" * 70)
    print("✅ All 3 videos generated successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()

