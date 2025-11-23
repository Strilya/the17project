"""
Content Generation Module

This module handles the interaction with Anthropic's Claude AI API to generate
Instagram content (captions, hashtags, and image descriptions) for The17Project.

Main functionality:
- Loads prompt configuration from prompts.json
- Calls Claude AI API (claude-3-5-sonnet model)
- Parses and validates the JSON response
- Returns structured content ready for posting
"""

# Import os module to access environment variables and file paths
import os
# Import json module to handle JSON data parsing and serialization
import json
# Import logging module to track execution and debug issues
import logging
# Import datetime to add timestamps to generated content
from datetime import datetime
# Import typing utilities for type hints and better code documentation
from typing import Dict, Any, Optional
# Import Path for cross-platform file path handling
from pathlib import Path

# Import Anthropic client to interact with Claude AI API
from anthropic import Anthropic
# Import dotenv to load environment variables from .env file
from dotenv import load_dotenv

# Configure logging to output INFO level messages with timestamps
# This helps track the execution flow and debug issues
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Create a logger instance for this module
logger = logging.getLogger(__name__)

# Load environment variables from .env file into os.environ
# This allows us to access API keys and configuration securely
load_dotenv()


class ContentGenerator:
    """
    Handles Instagram content generation using Claude AI API.

    This class manages the entire content generation workflow:
    1. Loading prompt templates from configuration
    2. Making API calls to Claude AI
    3. Parsing and validating responses
    4. Error handling and retries
    """

    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None, use_first_post: bool = True):
        """
        Initialize the ContentGenerator.

        Args:
            api_key: Anthropic API key (defaults to environment variable)
            config_path: Path to prompts.json configuration file
            use_first_post: If True, use first_post_prompt instead of regular prompt (default: True for initial launch)
        """
        self.use_first_post = use_first_post
        # Get API key from parameter or environment variable
        # The API key is required to authenticate with Claude AI
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        # If no API key is found, raise an error immediately
        # This prevents wasting time with invalid configuration
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")

        # Initialize Anthropic client with the API key
        # This client handles all communication with Claude AI
        self.client = Anthropic(api_key=self.api_key)

        # Load configuration from prompts.json
        # If no path is provided, use the default location in config folder
        if config_path is None:
            # Construct path relative to this file: ../config/prompts.json
            config_path = Path(__file__).parent.parent / "config" / "prompts.json"

        # Load the configuration file (contains prompts and settings)
        self.config = self._load_config(config_path)

        # Get temperature setting from environment or use default (0.8)
        # Temperature controls randomness: 0=deterministic, 1=very creative
        self.temperature = float(os.getenv("CONTENT_TEMPERATURE", "0.8"))
        # Get max tokens setting from environment or use default (1000)
        # Max tokens limits the length of Claude's response
        self.max_tokens = int(os.getenv("CONTENT_MAX_TOKENS", "1000"))

        # Log successful initialization for debugging
        logger.info("ContentGenerator initialized successfully with Claude AI")

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """
        Load prompt configuration from JSON file.

        Args:
            config_path: Path to the prompts.json file

        Returns:
            Dictionary containing all prompt configurations
        """
        # Try to open and parse the configuration file
        try:
            # Open file in read mode with UTF-8 encoding
            # UTF-8 ensures special characters are handled correctly
            with open(config_path, 'r', encoding='utf-8') as f:
                # Parse JSON content into a Python dictionary
                config = json.load(f)
            # Log successful configuration load
            logger.info(f"Configuration loaded from {config_path}")
            # Return the parsed configuration
            return config
        # Handle case where file doesn't exist
        except FileNotFoundError:
            # Log the error with the file path
            logger.error(f"Configuration file not found: {config_path}")
            # Re-raise the exception so caller knows about the error
            raise
        # Handle case where file contains invalid JSON
        except json.JSONDecodeError as e:
            # Log the specific JSON error
            logger.error(f"Invalid JSON in configuration file: {e}")
            # Re-raise the exception with context
            raise

    def generate_content(self) -> Dict[str, Any]:
        """
        Generate Instagram content using Claude AI API.

        This method:
        1. Constructs the prompt from configuration
        2. Calls Claude AI API with claude-3-5-sonnet model
        3. Parses the JSON response
        4. Validates the content structure
        5. Adds metadata (timestamp, etc.)

        Returns:
            Dictionary containing:
                - caption: Instagram caption (150-200 words)
                - hashtags: List of 20 hashtags
                - image_description: Canva design instructions
                - generated_at: Timestamp
                - model: Model used for generation

        Raises:
            Exception: If API call fails or response is invalid
        """
        # Wrap all logic in try-except to handle any errors gracefully
        try:
            # Log the start of content generation
            logger.info("Starting content generation with Claude AI...")

            # Select the appropriate prompt based on use_first_post flag
            if self.use_first_post:
                prompt_key = "first_post_prompt"
                logger.info("Using FIRST POST prompt for introduction content")
            else:
                prompt_key = "content_generation_prompt"
                logger.info("Using regular content generation prompt")

            # Construct the full prompt by combining system and user prompts
            # System prompt sets the AI's role and behavior
            # User prompt contains the specific content request
            full_prompt = f"{self.config['system_prompt']}\n\n{self.config[prompt_key]}"

            # Call Claude AI API with the constructed prompt
            # Use claude-3-haiku-20240307 model (fast and reliable)
            logger.info("Calling Claude AI API (claude-3-haiku-20240307)...")
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Use Claude 3 Haiku - widely accessible
                max_tokens=self.max_tokens,  # Limit response length
                temperature=self.temperature,  # Control creativity/randomness
                messages=[
                    {
                        "role": "user",  # Message from the user
                        "content": full_prompt  # The complete prompt text
                    }
                ]
            )

            # Extract the text content from Claude's response
            # Claude returns a list of content blocks; we take the first one
            content_text = response.content[0].text
            # Log that we received a response
            logger.info("Received response from Claude AI")

            # Parse the response text as JSON
            # Claude should return structured JSON based on our prompt
            content = json.loads(content_text)

            # DEBUG: Log the raw structure of what Claude returned
            logger.info(f"Raw content structure from Claude: {json.dumps(content, indent=2)}")
            logger.info(f"Hashtags type: {type(content.get('hashtags')).__name__}")
            logger.info(f"Hashtags value: {content.get('hashtags')}")

            # CRITICAL FIX: Ensure hashtags is always a list
            # If Claude returns a string, split it into a list
            if isinstance(content.get("hashtags"), str):
                logger.warning("Hashtags returned as STRING, converting to list...")
                # Split by spaces or commas, filter empty strings
                hashtags_str = content["hashtags"]
                content["hashtags"] = [tag.strip() for tag in hashtags_str.replace(",", " ").split() if tag.strip()]
                logger.info(f"Converted hashtags to list: {content['hashtags']}")

            # Validate that the content has all required fields
            # This catches any malformed responses early
            self._validate_content(content)

            # Add metadata to the content dictionary
            # This helps track when and how content was generated
            content["generated_at"] = datetime.now().isoformat()  # Current timestamp
            content["model"] = "claude-3-haiku-20240307"  # Model name
            content["tokens_used"] = response.usage.input_tokens + response.usage.output_tokens  # Total tokens

            # Log success with useful statistics
            logger.info("Content generated successfully")
            logger.info(f"Caption length: {len(content['caption'])} characters")
            logger.info(f"Hashtags count: {len(content['hashtags'])}")
            logger.info(f"Tokens used: {content['tokens_used']}")

            # Return the complete content dictionary
            return content

        # Handle JSON parsing errors
        except json.JSONDecodeError as e:
            # Log the specific error
            logger.error(f"Failed to parse Claude AI response as JSON: {e}")
            # Raise a more descriptive exception
            raise Exception(f"Invalid JSON response from Claude AI: {e}")

        # Handle any other errors (API errors, network issues, etc.)
        except Exception as e:
            # Log the error
            logger.error(f"Content generation failed: {e}")
            # Re-raise the exception for the caller to handle
            raise

    def _validate_content(self, content: Dict[str, Any]) -> None:
        """
        Validate that generated content has all required fields.

        Args:
            content: Dictionary containing generated content

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Define the fields that must be present in the content
        # These are essential for posting to Instagram
        required_fields = ["caption", "hashtags", "image_description"]

        # Check each required field
        for field in required_fields:
            # If field is missing, raise an error immediately
            if field not in content:
                raise ValueError(f"Missing required field: {field}")

        # Validate caption length by counting words
        # Split on whitespace to get word count
        caption_words = len(content["caption"].split())
        # Warn if caption is too short (less than 50 words)
        if caption_words < 50:
            logger.warning(f"Caption is short: {caption_words} words")

        # Validate hashtags field is a list
        if not isinstance(content["hashtags"], list):
            raise ValueError("Hashtags must be a list")

        # Warn if we have fewer than 10 hashtags (we expect 20)
        if len(content["hashtags"]) < 10:
            logger.warning(f"Only {len(content['hashtags'])} hashtags generated (expected 20)")

        # Validate image description is not too short
        if len(content["image_description"]) < 50:
            logger.warning("Image description is very short")

        # Log that validation passed
        logger.info("Content validation passed")


def main():
    """
    Main function for testing content generation locally.

    Usage:
        python src/generate_content.py

    Note: Set use_first_post=False after your first post is published
    """
    # Wrap in try-except to handle errors gracefully
    try:
        # Create a ContentGenerator instance
        # use_first_post=True generates introduction post (change to False after first post)
        generator = ContentGenerator(use_first_post=True)
        # Generate content using Claude AI
        content = generator.generate_content()

        # Print a separator line for better readability
        print("\n" + "="*70)
        # Print header
        print("GENERATED CONTENT (via Claude AI)")
        # Print separator
        print("="*70)
        # Print the generated caption
        print(f"\nCAPTION:\n{content['caption']}\n")
        # Print the hashtags joined with spaces
        print(f"\nHASHTAGS:\n{' '.join(content['hashtags'])}\n")
        # Print the image description for Canva
        print(f"\nIMAGE DESCRIPTION:\n{content['image_description']}\n")
        # Print separator
        print("="*70)
        # Print metadata section header
        print(f"\nMetadata:")
        # Print when content was generated
        print(f"  Generated at: {content['generated_at']}")
        # Print which model was used
        print(f"  Model: {content['model']}")
        # Print token usage for cost tracking
        print(f"  Tokens used: {content['tokens_used']}")
        # Print final separator
        print("="*70)

    # Handle any errors that occur during generation
    except Exception as e:
        # Log the error
        logger.error(f"Failed to generate content: {e}")
        # Re-raise so the program exits with error
        raise


# This block only runs if the script is executed directly
# Not run when imported as a module
if __name__ == "__main__":
    # Run the main function
    main()
