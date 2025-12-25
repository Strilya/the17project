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
    
    print(f"📊 Angel Number: {angel_number}")
    print()
    
    # Generate 3 different styles
    styles = [
        ("storytelling", "Deep Storytelling", content_gen.generate_storytelling),
        ("practical", "Practical Tips", content_gen.generate_practical),
        ("insights", "Spiritual Insights", content_gen.generate_insights)
    ]
    
    generated_videos = []
    
    for i, (style_id, style_name, generator_func) in enumerate(styles, 1):
        print(f"{'='*70}")
        print(f"VIDEO {i}/3: {style_name}")
        print(f"{'='*70}")
        
        # Generate content
        print(f"📝 Generating content...")
        content = generator_func(angel_number)
        
        print(f"   Hook: {content['hook']}")
        print(f"   CTA: {content['cta']}")
        
        # Combine all text for voice
        full_text = f"{content['hook']}. {content['meaning']}. {content['action']}. {content['cta']}"
        
        # Generate voice
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        voice_path = f"output/voice_{style_id}_{timestamp}.mp3"
        voice_gen.generate_speech(full_text, voice_path)
        
        # Generate video
        video_path = f"output/{angel_number}_{style_id}_{timestamp}.mp4"
        result = video_gen.generate_video(content, voice_path, video_path, style_name)
        
        if result:
            generated_videos.append(result)
            print(f"✅ VIDEO {i} COMPLETE: {video_path}")
        else:
            print(f"⚠️  VIDEO {i} FAILED")
        
        print()
    
    print("=" * 70)
    print(f"✅ GENERATION COMPLETE!")
    print(f"Generated {len(generated_videos)}/3 videos successfully")
    print("=" * 70)
    
    for video in generated_videos:
        print(f"  📹 {video}")

if __name__ == "__main__":
    main()

