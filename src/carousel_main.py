"""
Carousel Generator & Poster for THE17PROJECT
Generates and posts daily carousel to Instagram

Run: python3 src/carousel_main.py
Test: python3 src/carousel_main.py --test
"""

import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from carousel_generator import (
    generate_next_carousel,
    get_carousel_stats,
    get_all_carousel_specs
)
from sheets_logger import SheetsLogger
from slack_notifier import SlackNotifier
from instagram_poster import InstagramPoster

# Instagram posting control
INSTAGRAM_AUTO_POST = os.getenv('INSTAGRAM_AUTO_POST', 'true').lower() == 'true'


def get_posted_carousel_ids(sheets_logger):
    """Get set of carousel IDs already posted from Google Sheets"""
    try:
        posted = sheets_logger.get_posted_carousels()
        return set(posted)
    except Exception as e:
        print(f"   ⚠️  Could not load posted carousels: {e}")
        return set()


def main(test_mode=False):
    """
    Generate and post daily carousel

    Args:
        test_mode: If True, generates carousel but doesn't post or track
    """
    print("=" * 70)
    print("THE17PROJECT - CAROUSEL GENERATOR & POSTER")
    if test_mode:
        print("🧪 TEST MODE - Will not post or track")
    print("=" * 70)

    # Show stats
    stats = get_carousel_stats()
    print(f"\n📊 CAROUSEL INVENTORY:")
    print(f"   Total unique carousels: {stats['total']}")
    print(f"   - Life Path Breakdowns: {stats['life_path_breakdown']}")
    print(f"   - Compatibility Guides: {stats['life_path_compatibility']}")
    print(f"   - Career Deep Dives: {stats['life_path_career']}")
    print(f"   - Love Guides: {stats['life_path_love']}")
    print(f"   - Angel Numbers: {stats['angel_number']}")
    print(f"   Days of unique content: {stats['days_of_content']}")

    # Initialize services
    print("\n🔌 Setting up integrations...")
    sheets_logger = SheetsLogger()
    slack_notifier = SlackNotifier()

    # Get posted carousel IDs
    posted_ids = get_posted_carousel_ids(sheets_logger)
    print(f"   Already posted: {len(posted_ids)} carousels")
    remaining = stats['total'] - len(posted_ids)
    print(f"   Remaining: {remaining} unique carousels")

    # Initialize Instagram poster
    instagram_poster = None
    if INSTAGRAM_AUTO_POST and not test_mode:
        try:
            print("   📱 Initializing Instagram poster...")
            instagram_poster = InstagramPoster()
            print("   ✅ Instagram poster ready")
        except Exception as e:
            print(f"   ⚠️  Instagram login failed: {e}")
            print("   ⚠️  Continuing without Instagram posting")
            instagram_poster = None
    else:
        if test_mode:
            print("   ⚠️  Instagram posting disabled (test mode)")
        else:
            print("   ⚠️  Instagram auto-post disabled")

    # Generate next carousel
    print("\n" + "=" * 70)
    print("GENERATING CAROUSEL")
    print("=" * 70)

    result = generate_next_carousel(posted_ids)

    if not result:
        print("\n❌ Carousel generation failed!")
        return

    print(f"\n✅ Carousel generated successfully!")
    print(f"   ID: {result['carousel_id']}")
    print(f"   Type: {result['type']}")
    print(f"   Slides: {len(result['slide_paths'])}")
    print(f"   Directory: {result['carousel_dir']}")

    # Post to Instagram
    instagram_url = None
    if instagram_poster and not test_mode:
        print("\n📱 Posting carousel to Instagram...")
        instagram_result = instagram_poster.post_carousel(
            image_paths=result['slide_paths'],
            caption=result['caption']
        )

        if instagram_result:
            instagram_url = instagram_result['url']
            print(f"   ✅ Posted to Instagram: {instagram_url}")
        else:
            print("   ❌ Instagram posting failed")

    # Log to Google Sheets (track which carousel was posted)
    if not test_mode:
        print("\n📊 Logging to Google Sheets...")
        try:
            sheets_logger.log_carousel(
                carousel_id=result['carousel_id'],
                carousel_type=result['type'],
                instagram_url=instagram_url
            )
            print("   ✅ Logged to sheets")
        except Exception as e:
            print(f"   ⚠️  Failed to log: {e}")

    # Send Slack notification
    if instagram_url:
        try:
            slack_notifier.send_carousel_notification(
                carousel_id=result['carousel_id'],
                carousel_type=result['type'],
                instagram_url=instagram_url,
                slide_count=len(result['slide_paths'])
            )
        except Exception as e:
            print(f"   ⚠️  Slack notification failed: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("✅ CAROUSEL COMPLETE!")
    print("=" * 70)
    print(f"   Carousel: {result['carousel_id']}")
    if instagram_url:
        print(f"   Instagram: {instagram_url}")
    if test_mode:
        print(f"   🧪 TEST MODE - Not tracked")
        print(f"   Preview slides at: {result['carousel_dir']}")

    print(f"\n📝 Caption preview:")
    print("-" * 40)
    caption = result.get('caption', '')
    print(caption[:400] + "..." if len(caption) > 400 else caption)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate and post carousel')
    parser.add_argument('--test', action='store_true',
                        help='Test mode: generates without posting or tracking')
    args = parser.parse_args()

    main(test_mode=args.test)
