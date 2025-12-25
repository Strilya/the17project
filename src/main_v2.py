"""
Main Workflow V2 - A/B Testing Capable

Identical to main.py but can switch between V1 and V2 content generators
via the USE_V2_CONTENT environment variable.

Usage:
    # Use original content (V1):
    python src/main_v2.py

    # Use improved content (V2):
    USE_V2_CONTENT=true python src/main_v2.py

This allows A/B testing of content approaches without modifying the original workflow.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Import BOTH content generators for A/B testing
from generate_content import ContentGenerator as ContentGeneratorV1
try:
    from generate_content_v2 import ContentGeneratorV2
    V2_AVAILABLE = True
except ImportError:
    V2_AVAILABLE = False
    logging.warning("ContentGeneratorV2 not available, will use V1 only")

from save_to_sheets import SheetsManager
from send_slack_notification import SlackNotifier, is_slack_configured
from topic_manager import TopicManager
from video_generator import VideoGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('content_generation.log')
    ]
)
logger = logging.getLogger(__name__)

load_dotenv(override=True)


class ContentAutomationV2:
    """
    Content automation with A/B testing.

    Control via environment variable:
        USE_V2_CONTENT=true  -> Use improved content generator (V2)
        USE_V2_CONTENT=false -> Use original content generator (V1, default)
    """

    def __init__(self):
        """Initialize with version selection."""
        logger.info("="*70)
        logger.info("THE17PROJECT CONTENT AUTOMATION V2")
        logger.info("="*70)
        logger.info(f"Started: {datetime.now().isoformat()}")

        try:
            # Determine which content generator to use
            use_v2 = os.getenv('USE_V2_CONTENT', 'false').lower() == 'true'

            if use_v2 and V2_AVAILABLE:
                logger.info("🆕 Using IMPROVED content generator (V2)")
                logger.info("   Features: Controversial hooks, specific scenarios, strong CTAs")
                self.content_generator = ContentGeneratorV2(use_v2_prompts=True)
                self.content_version = 'v2'
            else:
                if use_v2 and not V2_AVAILABLE:
                    logger.warning("⚠️  V2 requested but not available, falling back to V1")
                logger.info("📦 Using ORIGINAL content generator (V1)")
                self.content_generator = ContentGeneratorV1()
                self.content_version = 'v1'

            # Initialize other services (unchanged from original)
            self.topic_manager = TopicManager()
            logger.info("✓ Topic manager initialized")

            self.sheets_manager = SheetsManager()
            logger.info("✓ Sheets manager initialized")

            self.video_generator = VideoGenerator()
            logger.info("✓ Video generator initialized")

            self.slack_enabled = is_slack_configured()
            if self.slack_enabled:
                self.slack_notifier = SlackNotifier()
                logger.info("✓ Slack notifier initialized")
            else:
                self.slack_notifier = None
                logger.warning("⚠️  Slack not configured - notifications will be skipped")

            logger.info("="*70)
            logger.info(f"✅ All services initialized (Content: {self.content_version.upper()})")
            logger.info("="*70 + "\n")

        except Exception as e:
            logger.error(f"❌ Failed to initialize services: {e}")
            raise

    def run(self) -> Dict[str, Any]:
        """
        Execute workflow (IDENTICAL to original main.py).

        Returns:
            Dict with workflow results + version metadata
        """
        workflow_result = {
            "success": False,
            "content_generated": False,
            "saved_to_sheets": False,
            "video_generated": False,
            "video_path": None,
            "slack_notified": False,
            "slack_skipped": False,
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "content_version": self.content_version  # NEW: track version
        }

        try:
            # STEP 1: Select topic
            logger.info("\n" + "-"*70)
            logger.info("STEP 1: Selecting topic from rotation")
            logger.info("-"*70)

            specific_topic = self.topic_manager.get_next_topic()
            logger.info(f"Selected: {specific_topic['value']} ({specific_topic['type']})")

            workflow_result["topic"] = specific_topic["value"]
            workflow_result["category"] = specific_topic["type"]

            # STEP 2: Generate content
            logger.info("\n" + "-"*70)
            logger.info(f"STEP 2: Generating content with {self.content_version.upper()}")
            logger.info("-"*70)

            content = self.content_generator.generate_content(specific_topic)
            workflow_result["content_generated"] = True
            workflow_result["content"] = content

            # Track V2 metadata if available
            if isinstance(content, dict):
                workflow_result["prompt_version"] = content.get('prompt_version', self.content_version)
                workflow_result["hook_style"] = content.get('hook_style_used', 'unknown')

            logger.info("✅ Content generated successfully")

            # STEP 3: Generate video
            logger.info("\n" + "-"*70)
            logger.info("STEP 3: Generating 17-second Instagram Reel")
            logger.info("-"*70)

            video_path = ""
            if "video_scenes" in content and content["video_scenes"]:
                try:
                    video_path = self.video_generator.generate_reel(
                        content=content["video_scenes"],
                        category=specific_topic["type"]
                    )
                    workflow_result["video_generated"] = True
                    workflow_result["video_path"] = video_path
                    logger.info(f"✅ Video generated: {video_path}")
                except Exception as video_error:
                    logger.error(f"❌ Video generation failed: {video_error}")
                    logger.warning("⚠️  Continuing workflow without video")
                    workflow_result["video_generated"] = False
            else:
                logger.warning("⚠️  No video_scenes in content, skipping video")
                workflow_result["video_generated"] = False

            # STEP 4: Save to Google Sheets
            logger.info("\n" + "-"*70)
            logger.info("STEP 4: Saving to Google Sheets")
            logger.info("-"*70)

            sheet_row = self.sheets_manager.save_content(
                content=content,
                topic=specific_topic["value"],
                category=specific_topic["type"],
                video_path=video_path
            )
            workflow_result["saved_to_sheets"] = True
            workflow_result["sheet_row"] = sheet_row

            sheet_url = f"https://docs.google.com/spreadsheets/d/{os.getenv('SHEET_ID')}"
            workflow_result["sheet_url"] = sheet_url

            logger.info(f"✅ Saved to Google Sheets (Row {sheet_row})")

            # STEP 5: Mark topic as used
            logger.info("\n" + "-"*70)
            logger.info("STEP 5: Updating topic tracker")
            logger.info("-"*70)

            self.topic_manager.mark_topic_used(
                topic=specific_topic["value"],
                category=specific_topic["type"]
            )
            logger.info(f"✅ Topic '{specific_topic['value']}' marked as used")

            # STEP 6: Send Slack notification
            logger.info("\n" + "-"*70)
            logger.info("STEP 6: Sending Slack notification")
            logger.info("-"*70)

            if self.slack_notifier and self.slack_enabled:
                slack_response = self.slack_notifier.send_mobile_post(
                    content=content,
                    video_path=video_path if workflow_result["video_generated"] else None,
                    sheet_url=sheet_url,
                    sheet_row=sheet_row
                )

                if slack_response.get("skipped"):
                    workflow_result["slack_skipped"] = True
                    logger.info("⚠️  Slack notification skipped (not configured)")
                else:
                    workflow_result["slack_notified"] = True
                    workflow_result["slack_message_ts"] = slack_response.get("message_ts")
                    workflow_result["video_uploaded"] = slack_response.get("video_uploaded", False)
                    logger.info("✅ Slack mobile post sent")
                    if slack_response.get("video_uploaded"):
                        logger.info("   📹 Video uploaded to Slack")
            else:
                workflow_result["slack_skipped"] = True
                logger.info("⚠️  Slack notification skipped (not configured)")

            # SUCCESS
            workflow_result["success"] = True

            # Final summary
            logger.info("\n" + "="*70)
            logger.info("✨ WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("="*70)
            logger.info(f"Content Version: {self.content_version.upper()}")
            if 'hook_style' in workflow_result:
                logger.info(f"Hook Style: {workflow_result['hook_style']}")
            logger.info(f"Topic: {specific_topic['value']} ({specific_topic['type']})")
            logger.info(f"Caption: {len(content['caption'])} characters")
            logger.info(f"Hashtags: {len(content['hashtags'].split())}")
            logger.info(f"Tokens: {content.get('tokens_used', 'N/A')}")
            logger.info(f"Sheet URL: {sheet_url}")
            if workflow_result["video_generated"]:
                logger.info(f"Video: {workflow_result['video_path']}")
            if workflow_result["slack_notified"]:
                logger.info("Slack: ✅ Sent")
            else:
                logger.info("Slack: ⚠️  Skipped")
            logger.info("="*70 + "\n")

            return workflow_result

        except Exception as e:
            error_msg = f"Workflow failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            workflow_result["error"] = error_msg

            # Try to send error notification
            if self.slack_notifier and self.slack_enabled:
                try:
                    self.slack_notifier.send_error_notification(error_msg)
                    logger.info("Error notification sent to Slack")
                except:
                    logger.error("Failed to send error notification to Slack")

            raise


def main():
    """Main entry point."""
    try:
        automation = ContentAutomationV2()
        result = automation.run()

        if result["success"]:
            logger.info(f"✅ Automation completed successfully (Version: {result['content_version'].upper()})")
            sys.exit(0)
        else:
            logger.error("❌ Automation failed")
            sys.exit(1)

    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
