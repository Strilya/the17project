"""
Unit tests for The17Project content generation system.

Tests cover:
- Content generation via Claude AI API
- Google Sheets integration
- Slack notifications
- Error handling and validation
"""

# Import os module to access environment variables and file paths
import os
# Import json module to handle JSON data for mocking API responses
import json
# Import pytest for test framework functionality and assertions
import pytest
# Import Mock, patch, and MagicMock from unittest.mock to create test doubles
from unittest.mock import Mock, patch, MagicMock
# Import datetime to handle timestamp testing
from datetime import datetime

# Import modules to test - these are our actual application modules
import sys
# Insert the src directory into Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the ContentGenerator class that we'll be testing
from generate_content import ContentGenerator
# Import the SheetsManager class that handles Google Sheets operations
from save_to_sheets import SheetsManager
# Import the SlackNotifier class that sends Slack notifications
from send_slack_notification import SlackNotifier


class TestContentGenerator:
    """Test cases for ContentGenerator class."""

    # Use @patch.dict to temporarily set environment variables for this test only
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    def test_initialization(self):
        """Test ContentGenerator initializes correctly."""
        # Patch the Anthropic class to avoid making real API calls during tests
        with patch('generate_content.Anthropic'):
            # Create a new ContentGenerator instance to test initialization
            generator = ContentGenerator()
            # Assert the API key was loaded correctly from environment variable
            assert generator.api_key == 'test-key-123'
            # Assert the temperature parameter has the expected default value
            assert generator.temperature == 0.8
            # Assert the max_tokens parameter has the expected default value (increased for Claude)
            assert generator.max_tokens == 1000

    # Clear all environment variables to test missing API key scenario
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key_raises_error(self):
        """Test that missing API key raises ValueError."""
        # Use pytest.raises to assert that a ValueError is raised
        # The match parameter checks that the error message contains the expected text
        with pytest.raises(ValueError, match="Anthropic API key not found"):
            # Attempting to create ContentGenerator without API key should raise error
            ContentGenerator()

    # Patch the Anthropic class to mock API responses
    @patch('generate_content.Anthropic')
    # Set a test API key in the environment for this test
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_generate_content_returns_valid_structure(self, mock_anthropic):
        """Test that generated content has correct structure."""
        # Create a Mock object to simulate the Claude AI API response
        mock_response = Mock()
        # Mock the content attribute which contains the response text
        # Claude returns content as a list of content blocks
        mock_content_block = Mock()
        # Set the text of the content block to a JSON string with expected structure
        # This simulates what Claude AI would return for our content generation
        mock_content_block.text = json.dumps({
            "caption": "Test caption for The17Project",
            "hashtags": ["#test", "#the17project", "#angelnumbers"],
            "image_description": "Purple background with gold text"
        })
        # Assign the content block to the response
        mock_response.content = [mock_content_block]
        # Mock the token usage information that Claude returns
        # Claude returns separate input and output token counts
        mock_response.usage = Mock()
        mock_response.usage.input_tokens = 150
        mock_response.usage.output_tokens = 100

        # Create a mock client that will be returned by Anthropic()
        mock_client = Mock()
        # Make the messages.create method return our mocked response
        mock_client.messages.create.return_value = mock_response
        # Make Anthropic() constructor return our mock client
        mock_anthropic.return_value = mock_client

        # Create the ContentGenerator with our mocked Anthropic client
        generator = ContentGenerator()
        # Call generate_content which should use our mocked response
        content = generator.generate_content()

        # Verify all required fields are present in the returned content
        # This ensures our generator properly parses and structures the response
        assert "caption" in content
        assert "hashtags" in content
        assert "image_description" in content
        assert "generated_at" in content
        assert "model" in content
        assert "tokens_used" in content

        # Verify the values are correct - model should be claude-3-5-sonnet-20241022
        assert content["model"] == "claude-3-5-sonnet-20241022"
        # Verify tokens_used matches what we mocked (150 + 100 = 250)
        assert content["tokens_used"] == 250
        # Verify hashtags is a list type as expected
        assert isinstance(content["hashtags"], list)

    # Patch Anthropic to test validation logic
    @patch('generate_content.Anthropic')
    # Set test API key
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_validation_catches_missing_fields(self, mock_anthropic):
        """Test that validation catches incomplete content."""
        # Create a mock response with incomplete data (missing required fields)
        mock_response = Mock()
        # Set up the content structure
        mock_content_block = Mock()
        # Return JSON with only caption, missing hashtags and image_description
        # This simulates an invalid/incomplete API response
        mock_content_block.text = json.dumps({
            "caption": "Test caption"
            # Missing hashtags and image_description intentionally
        })
        # Assign the incomplete content to the response
        mock_response.content = [mock_content_block]
        # Mock token usage even though response is incomplete
        mock_response.usage = Mock()
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 50

        # Set up the mock client to return incomplete response
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Create generator instance
        generator = ContentGenerator()

        # Assert that generate_content raises ValueError for incomplete content
        # This tests our validation logic that checks for required fields
        with pytest.raises(ValueError, match="Missing required field"):
            generator.generate_content()


class TestSheetsManager:
    """Test cases for SheetsManager class."""

    # Patch gspread.authorize to avoid real Google Sheets API calls
    @patch('save_to_sheets.gspread.authorize')
    # Set required environment variables for Google Sheets
    @patch.dict(os.environ, {
        'SHEET_ID': 'test-sheet-id',
        # GOOGLE_SHEETS_CREDENTIALS must be valid JSON
        'GOOGLE_SHEETS_CREDENTIALS': json.dumps({
            "type": "service_account",
            "project_id": "test-project"
        })
    })
    def test_initialization(self, mock_authorize):
        """Test SheetsManager initializes correctly."""
        # Create a mock client to be returned by authorize()
        mock_client = Mock()
        # Make authorize return our mock client
        mock_authorize.return_value = mock_client

        # Create SheetsManager instance to test initialization
        manager = SheetsManager()
        # Verify the sheet_id was loaded from environment variable correctly
        assert manager.sheet_id == 'test-sheet-id'
        # Verify that gspread.authorize was called to authenticate
        assert mock_authorize.called

    # Clear environment to test missing configuration
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_sheet_id_raises_error(self):
        """Test that missing sheet ID raises ValueError."""
        # Assert that ValueError is raised when SHEET_ID is missing
        # This ensures we fail fast with clear error messages
        with pytest.raises(ValueError, match="Sheet ID not found"):
            # Attempting to create SheetsManager without SHEET_ID should fail
            SheetsManager()

    # Patch gspread to mock Google Sheets operations
    @patch('save_to_sheets.gspread.authorize')
    # Set up environment with required credentials
    @patch.dict(os.environ, {
        'SHEET_ID': 'test-sheet-id',
        'GOOGLE_SHEETS_CREDENTIALS': json.dumps({"type": "service_account"})
    })
    def test_save_content_appends_row(self, mock_authorize):
        """Test that save_content appends a row to the sheet."""
        # Create mock worksheet to simulate Google Sheets operations
        mock_worksheet = Mock()
        # Create mock client for gspread
        mock_client = Mock()
        # Create mock spreadsheet object
        mock_spreadsheet = Mock()
        # Make get_worksheet return our mock worksheet
        mock_spreadsheet.get_worksheet.return_value = mock_worksheet
        # Make open_by_key return our mock spreadsheet
        mock_client.open_by_key.return_value = mock_spreadsheet
        # Make authorize return our mock client
        mock_authorize.return_value = mock_client

        # Mock row_values to simulate existing headers in the sheet
        # This is needed because save_content reads headers to format data
        mock_worksheet.row_values.return_value = ["Timestamp", "Date", "Caption"]
        # Mock row_count to simulate sheet has 10 rows
        mock_worksheet.row_count = 10

        # Create SheetsManager with all our mocks in place
        manager = SheetsManager()

        # Create test content that matches our expected content structure
        # Note: model name updated to Claude's model
        content = {
            "caption": "Test caption",
            "hashtags": ["#test", "#content"],
            "image_description": "Test image",
            "generated_at": "2024-01-15T08:00:00",
            "model": "claude-3-5-sonnet-20241022",
            "tokens_used": 200
        }

        # Call save_content which should append a row to the sheet
        manager.save_content(content)

        # Verify that append_row was called on the worksheet
        # This confirms save_content actually tried to save the data
        assert mock_worksheet.append_row.called
        # Get the arguments that were passed to append_row
        call_args = mock_worksheet.append_row.call_args[0][0]

        # Verify the row has the correct number of columns (10 expected)
        assert len(call_args) == 10  # Should have 10 columns
        # Verify the caption was placed in the correct column (index 2)
        assert call_args[2] == "Test caption"
        # Verify hashtags were formatted correctly (joined with spaces)
        assert "#test #content" in call_args[3]


class TestSlackNotifier:
    """Test cases for SlackNotifier class."""

    # Patch the Slack WebClient to avoid real API calls
    @patch('send_slack_notification.WebClient')
    # Set required Slack environment variables
    @patch.dict(os.environ, {
        'SLACK_BOT_TOKEN': 'xoxb-test-token',
        'SLACK_CHANNEL_ID': 'C12345'
    })
    def test_initialization(self, mock_webclient):
        """Test SlackNotifier initializes correctly."""
        # Create mock Slack client
        mock_client = Mock()
        # Mock the auth_test response to simulate successful authentication
        mock_client.auth_test.return_value = {'team': 'Test Team', 'user': 'test_bot'}
        # Make WebClient constructor return our mock
        mock_webclient.return_value = mock_client

        # Create SlackNotifier to test initialization
        notifier = SlackNotifier()
        # Verify bot token was loaded from environment correctly
        assert notifier.bot_token == 'xoxb-test-token'
        # Verify channel ID was loaded from environment correctly
        assert notifier.channel_id == 'C12345'

    # Clear environment to test missing credentials
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_token_raises_error(self):
        """Test that missing Slack token raises ValueError."""
        # Assert ValueError is raised when SLACK_BOT_TOKEN is missing
        # This ensures proper error handling for missing configuration
        with pytest.raises(ValueError, match="Slack bot token not found"):
            # Attempting to create SlackNotifier without token should fail
            SlackNotifier()

    # Patch WebClient to mock Slack API
    @patch('send_slack_notification.WebClient')
    # Set up Slack environment variables
    @patch.dict(os.environ, {
        'SLACK_BOT_TOKEN': 'xoxb-test-token',
        'SLACK_CHANNEL_ID': 'C12345'
    })
    def test_send_notification_posts_message(self, mock_webclient):
        """Test that send_content_notification posts to Slack."""
        # Create mock Slack client
        mock_client = Mock()
        # Mock successful authentication
        mock_client.auth_test.return_value = {'team': 'Test', 'user': 'bot'}
        # Mock successful message posting, returning a message timestamp
        mock_client.chat_postMessage.return_value = {'ts': '1234567890.123'}
        # Make WebClient return our mock
        mock_webclient.return_value = mock_client

        # Create SlackNotifier instance
        notifier = SlackNotifier()

        # Create test content to send in notification
        # Note: model name updated to Claude's model
        content = {
            "caption": "Test caption",
            "hashtags": ["#test"],
            "image_description": "Test image",
            "generated_at": datetime.now().isoformat(),
            "model": "claude-3-5-sonnet-20241022",
            "tokens_used": 200
        }

        # Send notification and capture response
        response = notifier.send_content_notification(content)

        # Verify chat_postMessage was called to send the message
        assert mock_client.chat_postMessage.called
        # Verify the response contains the message timestamp
        assert response['ts'] == '1234567890.123'

        # Get the kwargs that were passed to chat_postMessage
        call_kwargs = mock_client.chat_postMessage.call_args[1]
        # Verify the message includes blocks (Slack's rich formatting)
        assert 'blocks' in call_kwargs
        # Verify message was sent to the correct channel
        assert call_kwargs['channel'] == 'C12345'


class TestIntegration:
    """Integration tests for the complete workflow."""

    # Patch all three external services for integration testing
    @patch('generate_content.Anthropic')
    @patch('save_to_sheets.gspread.authorize')
    @patch('send_slack_notification.WebClient')
    # Set up all required environment variables for full workflow
    @patch.dict(os.environ, {
        'ANTHROPIC_API_KEY': 'test-key',
        'SHEET_ID': 'test-sheet',
        'GOOGLE_SHEETS_CREDENTIALS': json.dumps({"type": "service_account"}),
        'SLACK_BOT_TOKEN': 'xoxb-test',
        'SLACK_CHANNEL_ID': 'C123'
    })
    def test_full_workflow(self, mock_slack, mock_sheets, mock_anthropic):
        """Test the complete workflow from generation to notification."""
        # Mock Claude AI response for content generation
        mock_anthropic_response = Mock()
        # Set up content structure
        mock_content_block = Mock()
        # Provide complete, valid content in the response
        mock_content_block.text = json.dumps({
            "caption": "Full workflow test",
            "hashtags": ["#test", "#workflow"],
            "image_description": "Test image"
        })
        # Assign the content block to the response
        mock_anthropic_response.content = [mock_content_block]
        # Mock token usage
        mock_anthropic_response.usage = Mock()
        mock_anthropic_response.usage.input_tokens = 200
        mock_anthropic_response.usage.output_tokens = 100

        # Create Anthropic client mock and configure it to return our response
        mock_anthropic_client = Mock()
        mock_anthropic_client.messages.create.return_value = mock_anthropic_response
        mock_anthropic.return_value = mock_anthropic_client

        # Mock Google Sheets worksheet
        mock_worksheet = Mock()
        # Mock existing headers in the sheet
        mock_worksheet.row_values.return_value = ["Headers"]
        # Mock row count
        mock_worksheet.row_count = 5
        # Create spreadsheet mock and connect it to worksheet
        mock_spreadsheet = Mock()
        mock_spreadsheet.get_worksheet.return_value = mock_worksheet
        # Create sheets client and connect everything
        mock_sheets_client = Mock()
        mock_sheets_client.open_by_key.return_value = mock_spreadsheet
        mock_sheets.return_value = mock_sheets_client

        # Mock Slack client
        mock_slack_client = Mock()
        # Mock successful auth
        mock_slack_client.auth_test.return_value = {'team': 'Test', 'user': 'bot'}
        # Mock successful message posting
        mock_slack_client.chat_postMessage.return_value = {'ts': '123'}
        mock_slack.return_value = mock_slack_client

        # Step 1: Generate content using ContentGenerator
        generator = ContentGenerator()
        content = generator.generate_content()

        # Step 2: Save content to Google Sheets using SheetsManager
        sheets = SheetsManager()
        sheets.save_content(content)

        # Step 3: Send Slack notification using SlackNotifier
        notifier = SlackNotifier()
        notifier.send_content_notification(content)

        # Verify all three components were called successfully
        # This confirms the entire workflow executed end-to-end
        assert mock_anthropic_client.messages.create.called
        assert mock_worksheet.append_row.called
        assert mock_slack_client.chat_postMessage.called


# This allows running the tests directly with python test_content_generation.py
if __name__ == "__main__":
    # Run tests with pytest in verbose mode to see detailed output
    pytest.main([__file__, "-v"])
