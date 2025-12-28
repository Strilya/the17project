"""
The17Project - Generate ONE test reel
Includes: Google Sheets logging + Slack notifications
"""

import os
import sys
import random
from dotenv import load_dotenv
from datetime import datetime
from content_generator import ContentGenerator
from voice_generator import VoiceGenerator
from video_generator import VideoGenerator
from sheets_logger import SheetsLogger
from slack_notifier import SlackNotifier
from angel_numbers_db import get_all_angel_numbers, get_angel_number_meaning
from moviepy.audio.io.AudioFileClip import AudioFileClip

load_dotenv()

def check_number_inventory(sheets_logger, slack_notifier):
    """Check remaining unused numbers and warn if low"""
    all_numbers = get_all_angel_numbers()
    generated = sheets_logger.get_generated_content()
    used_numbers = set(generated['angel_numbers'])

    total_numbers = len(all_numbers)
    used_count = len(used_numbers)
    remaining = total_numbers - used_count

    usage_percent = (used_count / total_numbers) * 100

    print(f"\n📊 INVENTORY STATUS:")
    print(f"   Total numbers: {total_numbers}")
    print(f"   Used: {used_count}")
    print(f"   Remaining: {remaining}")
    print(f"   Usage: {usage_percent:.1f}%")

    # Warning thresholds
    if remaining <= 10:
        warning = f"""
⚠️⚠️⚠️ CRITICAL: ONLY {remaining} NUMBERS LEFT! ⚠️⚠️⚠️

You need to add more angel numbers to the list URGENTLY!
All numbers will be exhausted in ~{remaining // 3} days at 3/day.
        """
        print(warning)
        send_slack_warning(slack_notifier, warning)

    elif remaining <= 30:
        warning = f"""
⚠️ WARNING: Only {remaining} numbers remaining!

You have ~{remaining // 3} days left at 3 reels/day.
Consider adding more numbers to the list soon.
        """
        print(warning)
        send_slack_warning(slack_notifier, warning)

    elif remaining <= 60:
        print(f"   ⚡ {remaining // 3} days remaining at current rate\n")
    else:
        print(f"   ✅ {remaining // 3} days of content remaining\n")

    return remaining

def send_slack_warning(slack_notifier, message):
    """Send low inventory warning to Slack"""
    if not slack_notifier.enabled:
        return

    try:
        slack_notifier.client.chat_postMessage(
            channel=os.getenv('SLACK_CHANNEL_ID'),
            text=message
        )
    except Exception as e:
        print(f"   ⚠️  Failed to send Slack warning: {e}")

def main():
    print("=" * 70)
    print("THE17PROJECT - PROFESSIONAL REEL GENERATOR")
    print("=" * 70)

    # Initialize
    content_gen = ContentGenerator()
    voice_gen = VoiceGenerator()
    video_gen = VideoGenerator()

    # Initialize logging and notifications
    print("\n🔌 Setting up integrations...")
    sheets_logger = SheetsLogger()
    slack_notifier = SlackNotifier()

    # Determine output directory (use absolute path)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if os.path.exists('/mnt/user-data/outputs'):
        output_base = '/mnt/user-data/outputs'
    else:
        output_base = os.path.join(project_root, 'output')

    os.makedirs(output_base, exist_ok=True)

    # Check inventory and warn if low
    remaining = check_number_inventory(sheets_logger, slack_notifier)

    if remaining == 0:
        print("❌ NO NUMBERS LEFT! Add more to angel_numbers_db.py")
        sys.exit(1)

    # Smart angel number selection (avoid repeats)
    print("🔍 Selecting unique angel number...")
    all_numbers = get_all_angel_numbers()
    generated = sheets_logger.get_generated_content()
    used_numbers = set(generated['angel_numbers'])

    # Get unused numbers
    unused = [n for n in all_numbers if n not in used_numbers]

    if not unused:
        # All used - start new cycle with shuffle
        unused = all_numbers.copy()
        random.shuffle(unused)
        print("   ♻️  All numbers used, starting new cycle")

    angel_number = random.choice(unused)
    meaning = get_angel_number_meaning(angel_number)

    print(f"\n📊 Angel Number: {angel_number}")
    print(f"   Meaning: {meaning}")
    print(f"🎬 Generating professional storytelling reel...\n")

    # Generate content
    content = content_gen.generate_storytelling(angel_number)

    print(f"Hook: {content['hook']}")
    print(f"CTA: {content['cta']}\n")

    # Generate voice with segmented timing for perfect text sync
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_voice_path = f"{output_base}/temp_voice_{timestamp}.mp3"
    temp_voice_path, voice_timings = voice_gen.generate_segmented_speech(content, temp_voice_path)

    # Get voice duration for logging
    voice_audio = AudioFileClip(temp_voice_path)
    voice_duration = voice_audio.duration
    total_duration = voice_duration + 2  # Add 2s end card

    # Full text for transcript
    full_text = f"{content['hook']}. {content['meaning']}. {content['action']}. {content['cta']}"

    # Generate professional video with all features + synced text
    video_path = f"{output_base}/{angel_number}_reel_{timestamp}.mp4"
    result = video_gen.generate_video(content, temp_voice_path, video_path, "Storytelling", voice_timings)

    if result:
        print(f"\n✅ PROFESSIONAL REEL CREATED: {video_path}")
        print(f"   Duration: {total_duration:.1f}s (voice + 2s end card)")
        print(f"   Features: Multiple clips, synced captions, watermarks, music, end card")

        # Log to Google Sheets
        print(f"\n📊 Logging to integrations...")
        hashtags = sheets_logger.log_reel(
            angel_number=angel_number,
            style="Storytelling",
            content=content,
            transcript=full_text,
            video_path=video_path,
            duration=total_duration,
            video_sources=["Pexels", "Pixabay"]  # Update if tracking specific sources
        )

        # Send Slack notification
        if hashtags:
            slack_notifier.send_reel_notification(
                angel_number=angel_number,
                style="Storytelling",
                content=content,
                hashtags=hashtags,
                video_path=video_path,
                duration=total_duration
            )

        # Cleanup temp files
        try:
            if os.path.exists(temp_voice_path):
                os.remove(temp_voice_path)
                print(f"\n🗑️  Cleaned up temp voice file")
        except Exception as e:
            pass

        print(f"\n{'=' * 70}")
        print(f"✅ ALL DONE!")
        print(f"{'=' * 70}")
        print(f"Video: {video_path}")
        if hashtags:
            print(f"\nHashtags:\n{hashtags}")

    else:
        print(f"\n❌ REEL GENERATION FAILED")

        # Cleanup temp files even on failure
        try:
            if os.path.exists(temp_voice_path):
                os.remove(temp_voice_path)
        except Exception as e:
            pass

if __name__ == "__main__":
    main()

