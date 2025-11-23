"""
Main Workflow Orchestrator

This is the entry point for the automated Instagram content generation workflow.
It coordinates all three modules: content generation, Google Sheets logging, and Slack notifications.

Workflow:
1. Generate content using Claude AI API
2. Save content to Google Sheets
3. Send Slack notification (optional - skipped if not configured)
4. Handle errors gracefully

This script is called by GitHub Actions daily at 8:00 AM EST.

Note: Slack notifications are optional. The workflow will complete successfully
even if SLACK_BOT_TOKEN and SLACK_CHANNEL_ID are not configured.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any

from dotenv import load_dotenv

# Import our custom modules
# ContentGenerator handles AI content generation using Claude AI
from generate_content import ContentGenerator
# SheetsManager handles saving content to Google Sheets
from save_to_sheets import SheetsManager
# SlackNotifier handles Slack notifications (optional integration)
# is_slack_configured checks if Slack credentials are available
from send_slack_notification import SlackNotifier, is_slack_configured

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('content_generation.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ContentAutomation:
    """
    Main automation orchestrator for The17Project Instagram content.

    This class coordinates the entire workflow:
    1. Content generation via Claude AI
    2. Saving to Google Sheets
    3. Slack notifications (optional - skipped if not configured)
    4. Error handling and recovery
    """

    def __init__(self):
        """Initialize all required services."""
        # Print header for log readability
        logger.info("="*70)
        logger.info("THE17PROJECT CONTENT AUTOMATION")
        logger.info("="*70)
        logger.info(f"Starting automation at {datetime.now().isoformat()}")

        try:
            # Initialize content generator (required)
            # This handles AI content generation using Claude AI
            # use_first_post=True (default) generates introduction post
            # Change to use_first_post=False after first post is published
            self.content_generator = ContentGenerator(use_first_post=True)
            logger.info("✓ Content generator initialized (FIRST POST MODE)")

            # Initialize Google Sheets manager (required)
            # This handles saving content to the tracking spreadsheet
            self.sheets_manager = SheetsManager()
            logger.info("✓ Sheets manager initialized")

            # Initialize Slack notifier (optional)
            # Check if Slack is configured before initializing
            self.slack_enabled = is_slack_configured()
            if self.slack_enabled:
                # Slack is configured, initialize the notifier
                self.slack_notifier = SlackNotifier()
                logger.info("✓ Slack notifier initialized")
            else:
                # Slack is not configured, set notifier to None
                self.slack_notifier = None
                logger.warning("⚠ Slack not configured - notifications will be skipped")
                logger.warning("  Set SLACK_BOT_TOKEN and SLACK_CHANNEL_ID to enable Slack")

            logger.info("All required services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise

    def run(self) -> Dict[str, Any]:
        """
        Execute the complete content generation workflow.

        Returns:
            Dictionary with workflow results and status

        Workflow steps:
        1. Generate content using Claude AI API
        2. Save content to Google Sheets
        3. Send Slack notification with preview (optional - skipped if not configured)
        4. Return success status
        """
        # Initialize workflow result dictionary to track progress
        workflow_result = {
            "success": False,
            "content_generated": False,
            "saved_to_sheets": False,
            "slack_notified": False,
            "slack_skipped": False,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Step 1: Generate content using Claude AI
            logger.info("\n" + "-"*70)
            logger.info("STEP 1: Generating content with Claude AI")
            logger.info("-"*70)

            # Call the content generator to create Instagram content
            content = self.content_generator.generate_content()
            # Mark content generation as successful
            workflow_result["content_generated"] = True
            # Store the generated content in the result
            workflow_result["content"] = content

            logger.info("✅ Content generated successfully")

            # Step 2: Save to Google Sheets
            logger.info("\n" + "-"*70)
            logger.info("STEP 2: Saving to Google Sheets")
            logger.info("-"*70)

            # Save the content to Google Sheets for tracking
            self.sheets_manager.save_content(content)
            # Mark sheets saving as successful
            workflow_result["saved_to_sheets"] = True

            # Build the Google Sheets URL for reference
            sheet_url = f"https://docs.google.com/spreadsheets/d/{os.getenv('SHEET_ID')}"
            workflow_result["sheet_url"] = sheet_url

            logger.info("✅ Content saved to Google Sheets")

            # Step 3: Send Slack notification (optional)
            logger.info("\n" + "-"*70)
            logger.info("STEP 3: Sending Slack notification")
            logger.info("-"*70)

            # Check if Slack notifier is available
            if self.slack_notifier and self.slack_enabled:
                # Slack is configured, send notification
                slack_response = self.slack_notifier.send_content_notification(
                    content=content,
                    sheet_url=sheet_url
                )
                # Check if notification was actually sent or skipped
                if slack_response.get("skipped"):
                    workflow_result["slack_skipped"] = True
                    logger.info("⚠ Slack notification skipped (not configured)")
                else:
                    workflow_result["slack_notified"] = True
                    workflow_result["slack_message_ts"] = slack_response.get("ts")
                    logger.info("✅ Slack notification sent")
            else:
                # Slack is not configured, skip notification
                workflow_result["slack_skipped"] = True
                logger.info("⚠ Slack notification skipped (not configured)")

            # All required steps completed successfully
            # Workflow is successful even if Slack was skipped
            workflow_result["success"] = True

            # Log final summary
            logger.info("\n" + "="*70)
            logger.info("✨ WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("="*70)
            logger.info(f"Caption length: {len(content['caption'])} characters")
            logger.info(f"Hashtags: {len(content['hashtags'])}")
            logger.info(f"Tokens used: {content.get('tokens_used', 'N/A')}")
            logger.info(f"Sheet URL: {sheet_url}")
            if workflow_result["slack_skipped"]:
                logger.info("Slack: Skipped (not configured)")
            else:
                logger.info("Slack: Notification sent")
            logger.info("="*70 + "\n")

            return workflow_result

        except Exception as e:
            # Handle errors that occurred during the workflow
            error_msg = f"Workflow failed: {str(e)}"
            logger.error(error_msg)
            workflow_result["error"] = error_msg

            # Try to send error notification to Slack (if configured)
            if self.slack_notifier and self.slack_enabled:
                try:
                    self.slack_notifier.send_error_notification(error_msg)
                    logger.info("Error notification sent to Slack")
                except:
                    logger.error("Failed to send error notification to Slack")

            # Re-raise the exception
            raise

    def test_run(self) -> None:
        """
        Run a test workflow and print results.

        This is useful for local testing before deploying to GitHub Actions.
        """
        try:
            # Execute the workflow
            result = self.run()

            # Print results summary
            print("\n" + "="*70)
            print("TEST RUN RESULTS")
            print("="*70)
            print(f"Success: {result['success']}")
            print(f"Content Generated: {result['content_generated']}")
            print(f"Saved to Sheets: {result['saved_to_sheets']}")
            # Show Slack status (sent, skipped, or failed)
            if result.get('slack_skipped'):
                print(f"Slack Notified: Skipped (not configured)")
            else:
                print(f"Slack Notified: {result['slack_notified']}")

            if result['success']:
                print(f"\n✅ All required steps completed successfully!")
                print(f"\nSheet URL: {result.get('sheet_url', 'N/A')}")
                print(f"\nGenerated Content Preview:")
                print(f"Caption: {result['content']['caption'][:100]}...")
                print(f"Hashtags: {len(result['content']['hashtags'])} tags")
            else:
                print(f"\n❌ Workflow failed: {result.get('error', 'Unknown error')}")

            print("="*70 + "\n")

        except Exception as e:
            print(f"\n❌ Test run failed: {e}\n")
            raise


def main():
    """
    Main entry point for the content automation workflow.

    This function is called by GitHub Actions scheduler.
    It can also be run locally for testing.

    Usage:
        python src/main.py
    """
    try:
        automation = ContentAutomation()
        result = automation.run()

        # Exit with appropriate code
        if result["success"]:
            logger.info("Automation completed successfully")
            sys.exit(0)
        else:
            logger.error("Automation failed")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
