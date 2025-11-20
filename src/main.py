"""
Main Workflow Orchestrator

This is the entry point for the automated Instagram content generation workflow.
It coordinates all three modules: content generation, Google Sheets logging, and Slack notifications.

Workflow:
1. Generate content using OpenAI API
2. Save content to Google Sheets
3. Send Slack notification
4. Handle errors gracefully

This script is called by GitHub Actions daily at 8:00 AM EST.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any

from dotenv import load_dotenv

# Import our custom modules
from generate_content import ContentGenerator
from save_to_sheets import SheetsManager
from send_slack_notification import SlackNotifier

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
    1. Content generation via OpenAI
    2. Saving to Google Sheets
    3. Slack notifications
    4. Error handling and recovery
    """

    def __init__(self):
        """Initialize all required services."""
        logger.info("="*70)
        logger.info("THE17PROJECT CONTENT AUTOMATION")
        logger.info("="*70)
        logger.info(f"Starting automation at {datetime.now().isoformat()}")

        try:
            # Initialize services
            self.content_generator = ContentGenerator()
            self.sheets_manager = SheetsManager()
            self.slack_notifier = SlackNotifier()

            logger.info("All services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise

    def run(self) -> Dict[str, Any]:
        """
        Execute the complete content generation workflow.

        Returns:
            Dictionary with workflow results and status

        Workflow steps:
        1. Generate content using OpenAI API
        2. Save content to Google Sheets
        3. Send Slack notification with preview
        4. Return success status
        """
        workflow_result = {
            "success": False,
            "content_generated": False,
            "saved_to_sheets": False,
            "slack_notified": False,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Step 1: Generate content
            logger.info("\n" + "-"*70)
            logger.info("STEP 1: Generating content with OpenAI")
            logger.info("-"*70)

            content = self.content_generator.generate_content()
            workflow_result["content_generated"] = True
            workflow_result["content"] = content

            logger.info("✅ Content generated successfully")

            # Step 2: Save to Google Sheets
            logger.info("\n" + "-"*70)
            logger.info("STEP 2: Saving to Google Sheets")
            logger.info("-"*70)

            self.sheets_manager.save_content(content)
            workflow_result["saved_to_sheets"] = True

            sheet_url = f"https://docs.google.com/spreadsheets/d/{os.getenv('SHEET_ID')}"
            workflow_result["sheet_url"] = sheet_url

            logger.info("✅ Content saved to Google Sheets")

            # Step 3: Send Slack notification
            logger.info("\n" + "-"*70)
            logger.info("STEP 3: Sending Slack notification")
            logger.info("-"*70)

            slack_response = self.slack_notifier.send_content_notification(
                content=content,
                sheet_url=sheet_url
            )
            workflow_result["slack_notified"] = True
            workflow_result["slack_message_ts"] = slack_response.get("ts")

            logger.info("✅ Slack notification sent")

            # All steps completed successfully
            workflow_result["success"] = True

            logger.info("\n" + "="*70)
            logger.info("✨ WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("="*70)
            logger.info(f"Caption length: {len(content['caption'])} characters")
            logger.info(f"Hashtags: {len(content['hashtags'])}")
            logger.info(f"Tokens used: {content.get('tokens_used', 'N/A')}")
            logger.info(f"Sheet URL: {sheet_url}")
            logger.info("="*70 + "\n")

            return workflow_result

        except Exception as e:
            # Handle errors
            error_msg = f"Workflow failed: {str(e)}"
            logger.error(error_msg)
            workflow_result["error"] = error_msg

            # Try to send error notification to Slack
            try:
                self.slack_notifier.send_error_notification(error_msg)
                logger.info("Error notification sent to Slack")
            except:
                logger.error("Failed to send error notification to Slack")

            raise

    def test_run(self) -> None:
        """
        Run a test workflow and print results.

        This is useful for local testing before deploying to GitHub Actions.
        """
        try:
            result = self.run()

            print("\n" + "="*70)
            print("TEST RUN RESULTS")
            print("="*70)
            print(f"Success: {result['success']}")
            print(f"Content Generated: {result['content_generated']}")
            print(f"Saved to Sheets: {result['saved_to_sheets']}")
            print(f"Slack Notified: {result['slack_notified']}")

            if result['success']:
                print(f"\n✅ All steps completed successfully!")
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
