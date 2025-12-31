"""
The17Project - Generate professional reels with Life Path + Angel Number content
Includes: Google Sheets logging + Slack notifications
"""

import os
import sys
import random
import argparse
from dotenv import load_dotenv
from datetime import datetime
from content_generator import ContentGenerator
from voice_generator import VoiceGenerator
from video_generator import VideoGenerator
from sheets_logger import SheetsLogger
from slack_notifier import SlackNotifier
from angel_numbers_db import get_all_angel_numbers, get_angel_number_meaning
from moviepy.audio.io.AudioFileClip import AudioFileClip

# NEW: Life Path system imports
from content_flow_manager import get_day_type, get_content_plan_for_day, generate_caption, select_text_color
from life_path_generator import LifePathGenerator

load_dotenv()

# Configuration: Set to True for full day (3 reels), False for single test reel
GENERATE_FULL_DAY = False  # Scheduled runs use --reel-number to generate specific reel

# TESTING: Force specific day type (set to None for normal operation)
FORCE_DAY_TYPE = None  # Options: 'life_path', 'angel_number', 'wildcard', or None

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

def main(reel_number=None, test_mode=False):
    """
    Generate reels for The17Project

    Args:
        reel_number: Optional int (1, 2, or 3) to generate only that specific reel
                    If None, generates all reels based on GENERATE_FULL_DAY setting
        test_mode: If True, marks reels as TEST to avoid affecting rotation tracking
    """
    print("=" * 70)
    print("THE17PROJECT - PROFESSIONAL REEL GENERATOR")
    if test_mode:
        print("🧪 TEST MODE - Will not affect rotation tracking")
    print("=" * 70)

    # Initialize content generators
    content_gen = ContentGenerator()
    life_path_gen = LifePathGenerator()  # NEW: Life Path generator
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

    # Check inventory and warn if low (still useful for Angel Number days)
    remaining = check_number_inventory(sheets_logger, slack_notifier)

    if remaining == 0:
        print("⚠️  NO ANGEL NUMBERS LEFT! Add more to angel_numbers_db.py")
        print("   (Life Path reels will still work)")

    # NEW: Determine what to generate today
    if FORCE_DAY_TYPE:
        day_type = FORCE_DAY_TYPE
        print(f"\n📅 Day Type: {day_type.upper()} (FORCED FOR TESTING)")
    else:
        day_type = get_day_type()
        print(f"\n📅 Day Type: {day_type.upper()}")

    # Get content plan
    if reel_number:
        # SCHEDULED MODE: Generate only the specified reel
        reel_count = 3
        print(f"🎬 Scheduled Generation: Reel {reel_number}/3\n")
        content_plan = get_content_plan_for_day(day_type, reel_count=reel_count, sheets_logger=sheets_logger)
        # Filter to only the requested reel
        content_plan = [spec for spec in content_plan if spec['reel_number'] == reel_number]
    else:
        # MANUAL MODE: Generate based on GENERATE_FULL_DAY setting
        reel_count = 3 if GENERATE_FULL_DAY else 1
        print(f"🎬 Generating {reel_count} reel(s)...\n")
        content_plan = get_content_plan_for_day(day_type, reel_count=reel_count, sheets_logger=sheets_logger)

    # Generate each reel in the plan
    for reel_spec in content_plan:
        reel_num = reel_spec['reel_number']

        print(f"\n{'='*70}")
        print(f"GENERATING REEL {reel_num}/{reel_count}")
        print(f"{'='*70}")

        # Route to correct generator based on content type
        try:
            if reel_spec['type'] == 'life_path':
                # LIFE PATH CONTENT
                life_path_num = reel_spec['life_path_number']
                angle = reel_spec['angle']
                variation = reel_spec['variation']

                print(f"📊 Life Path {life_path_num} - {angle} ({variation})")
                print(f"🎬 Generating Life Path reel...\n")

                content = life_path_gen.generate_content(
                    life_path_number=life_path_num,
                    angle=angle,
                    variation=variation
                )

                content_type = 'life_path'
                content_identifier = f"LP{life_path_num}-{angle}"
                style_name = f"LP{life_path_num}"

            else:
                # ANGEL NUMBER CONTENT (existing logic)
                angel_number = reel_spec['angel_number']
                style = reel_spec['style']

                print(f"🔢 Angel Number {angel_number} - {style}")
                print(f"🎬 Generating Angel Number reel...\n")

                # Smart selection from unused numbers
                all_numbers = get_all_angel_numbers()
                generated = sheets_logger.get_generated_content()
                used_numbers = set(generated['angel_numbers'])
                unused = [n for n in all_numbers if n not in used_numbers]

                if not unused:
                    unused = all_numbers.copy()
                    random.shuffle(unused)
                    print("   ♻️  All numbers used, starting new cycle")

                # Use specific number from plan or pick from unused
                if angel_number in unused:
                    selected_number = angel_number
                else:
                    selected_number = random.choice(unused)

                # Generate based on style
                if style == 'storytelling':
                    content = content_gen.generate_storytelling(selected_number)
                elif style == 'practical':
                    content = content_gen.generate_practical(selected_number)
                else:
                    content = content_gen.generate_insights(selected_number)

                content_type = 'angel_number'
                content_identifier = selected_number
                style_name = style.capitalize()

        except Exception as e:
            print(f"❌ Content generation failed: {e}")
            print(f"Falling back to angel number generation...")

            # Fallback to angel number if Life Path fails
            all_numbers = get_all_angel_numbers()
            generated = sheets_logger.get_generated_content()
            used_numbers = set(generated['angel_numbers'])
            unused = [n for n in all_numbers if n not in used_numbers]

            if not unused:
                unused = all_numbers.copy()
                random.shuffle(unused)

            fallback_number = random.choice(unused)
            content = content_gen.generate_storytelling(fallback_number)
            content_type = 'angel_number'
            content_identifier = fallback_number
            style_name = "Storytelling"

        print(f"Hook: {content['hook']}")
        print(f"CTA: {content['cta']}\n")

        # Generate voice with segmented timing (SAME for both types)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_voice_path = f"{output_base}/temp_voice_{timestamp}.mp3"
        temp_voice_path, voice_timings = voice_gen.generate_segmented_speech(content, temp_voice_path)

        # Get voice duration for logging
        voice_audio = AudioFileClip(temp_voice_path)
        voice_duration = voice_audio.duration
        total_duration = voice_duration + 2  # Add 2s end card

        # Full text for transcript
        full_text = f"{content['hook']}. {content['meaning']}. {content['action']}. {content['cta']}"

        # Select text color with rotation (TODO: track used colors in sheets)
        color_name, text_color = select_text_color()
        print(f"   🎨 Text color: {color_name.upper()} {text_color}")

        # Generate professional video (SAME for both types)
        video_filename = f"{content_identifier}_reel_{timestamp}.mp4"
        video_path = f"{output_base}/{video_filename}"
        result = video_gen.generate_video(content, temp_voice_path, video_path, style_name, voice_timings, text_color)

        if result:
            print(f"\n✅ PROFESSIONAL REEL CREATED: {video_path}")
            print(f"   Duration: {total_duration:.1f}s (voice + 2s end card)")
            print(f"   Features: Multiple clips, synced captions, watermarks, music, end card")

            # Generate proper caption for Instagram (before logging)
            caption = generate_caption(reel_spec, content)

            # Log to Google Sheets (updated to handle both types)
            print(f"\n📊 Logging to integrations...")
            # Use "TEST" identifier in test mode to avoid affecting rotation tracking
            log_identifier = "TEST" if test_mode else content_identifier
            sheets_logger.log_reel(
                angel_number=log_identifier,
                style=content_type,
                content=content,
                transcript=full_text,
                video_path=video_path,
                duration=total_duration,
                video_sources=["Pexels", "Pixabay"],
                custom_caption=caption  # Use generated caption for both types
            )

            # Send Slack notification (with full caption)
            if caption:
                slack_notifier.send_reel_notification(
                    angel_number=content_identifier,
                    style=content_type,
                    content=content,
                    hashtags=caption,  # Full caption with hashtags
                    video_path=video_path,
                    duration=total_duration,
                    test_mode=test_mode
                )

            # Cleanup temp files
            try:
                if os.path.exists(temp_voice_path):
                    os.remove(temp_voice_path)
                    print(f"\n🗑️  Cleaned up temp voice file")
            except Exception as e:
                pass

            print(f"\n{'=' * 70}")
            print(f"✅ REEL {reel_num}/{reel_count} DONE!")
            if test_mode:
                print(f"🧪 TEST MODE - Not tracked in rotation")
            print(f"{'=' * 70}")
            print(f"Video: {video_path}")
            if caption:
                print(f"\nInstagram Caption:\n{caption[:200]}..." if len(caption) > 200 else f"\nInstagram Caption:\n{caption}")

        else:
            print(f"\n❌ REEL {reel_num}/{reel_count} GENERATION FAILED")

            # Cleanup temp files even on failure
            try:
                if os.path.exists(temp_voice_path):
                    os.remove(temp_voice_path)
            except Exception as e:
                pass

    # Final summary
    print(f"\n{'=' * 70}")
    print(f"✅ ALL {reel_count} REEL(S) COMPLETE!")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate The17Project reels')
    parser.add_argument('--reel-number', type=int, choices=[1, 2, 3],
                        help='Generate only a specific reel (1, 2, or 3) for scheduled runs')
    parser.add_argument('--test', action='store_true',
                        help='Test mode: generates reels without affecting rotation tracking')
    args = parser.parse_args()

    main(reel_number=args.reel_number, test_mode=args.test)

