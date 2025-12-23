"""
Content Generator V2 - Improved Hooks & CTAs

Generates scroll-stopping content with controversial hooks and specific scenarios
for better follower conversion. API-compatible with original ContentGenerator.

Key improvements:
- 5 distinct hook styles (controversial, urgent, curiosity, personal, specific)
- Concrete examples instead of generic spiritual talk
- Stronger CTAs with engagement hooks
- Scenario-based content ("Seeing 1111 at 3am?" instead of "Seeing 1111?")
"""

import os
import json
import logging
import random
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from anthropic import Anthropic
from hashtag_manager import HashtagManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContentGeneratorV2:
    """
    IMPROVED content generator with controversial hooks.

    API-compatible with ContentGenerator but uses prompts_v2.json
    for better engagement and follower conversion.
    """

    HOOK_STYLES = [
        "controversial",  # "Everyone gets X wrong"
        "urgent",         # "X isn't random, here's why"
        "curiosity",      # "The X secret nobody tells"
        "personal",       # "I saw X, then this happened"
        "specific"        # "Seeing X at 3am? Urgent"
    ]

    def __init__(self, config_path: Optional[str] = None, use_v2_prompts: bool = True):
        """
        Initialize ContentGeneratorV2.

        Args:
            config_path: Path to prompts config
            use_v2_prompts: If True, use prompts_v2.json, else prompts.json
        """
        if config_path is None:
            prompt_file = "prompts_v2.json" if use_v2_prompts else "prompts.json"
            config_path = Path(__file__).parent.parent / "config" / prompt_file

        logger.info(f"Loading prompts from: {config_path}")

        with open(config_path, 'r') as f:
            self.prompts = json.load(f)

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.hashtag_manager = HashtagManager()
        self.use_v2_prompts = use_v2_prompts

        version = "V2" if use_v2_prompts else "V1"
        logger.info(f"ContentGenerator{version} initialized")

    def generate_content(
        self,
        topic: Dict[str, str],
        force_hook_style: Optional[str] = None,
        category: str = "angel_numbers",
        style: str = "spiritual"
    ) -> Dict[str, any]:
        """
        Generate improved content.

        CRITICAL: Must return same structure as original ContentGenerator

        Args:
            topic: Dict with 'value' and 'type' keys (e.g. {'value': '1111', 'type': 'angel_numbers'})
                   OR string topic value
            force_hook_style: Override random selection (for testing)
            category: Fallback category if topic is a string
            style: Content style (unused, kept for compatibility)

        Returns:
            Dict with same structure as original:
            {
                "caption": str,
                "hashtags": str,  # Space-separated hashtags
                "video_scenes": {
                    "hook": str,
                    "meaning": str,
                    "action": str,
                    "cta": str
                },
                # V2 additions:
                "prompt_version": "v2",
                "hook_style_used": str,
                "content_angle": str,
                "tokens_used": int
            }
        """
        # Extract topic info (handle both dict and string formats)
        if isinstance(topic, dict):
            topic_value = topic['value']
            category = topic['type']
        else:
            topic_value = topic
            # category already set from parameter

        logger.info(f"\n{'='*60}")
        logger.info(f"Generating V2 content: {topic_value} ({category})")
        logger.info(f"{'='*60}")

        # Select hook style
        if force_hook_style and force_hook_style in self.HOOK_STYLES:
            hook_style = force_hook_style
            logger.info(f"Using FORCED hook style: {hook_style}")
        else:
            hook_style = random.choice(self.HOOK_STYLES)
            logger.info(f"Using RANDOM hook style: {hook_style}")

        # Build prompts
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(topic_value, category, hook_style)

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=0.9,  # Higher for variety
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )

            # Parse response
            content_text = response.content[0].text.strip()

            # Extract JSON (handle markdown code blocks)
            if "```json" in content_text:
                content_text = content_text.split("```json")[1].split("```")[0].strip()
            elif "```" in content_text:
                content_text = content_text.split("```")[1].strip()

            content = json.loads(content_text)

            # Validate required fields
            required = ['video_scenes']
            for field in required:
                if field not in content:
                    raise ValueError(f"Missing required field: {field}")

            # Validate video_scenes structure
            scene_required = ['hook', 'meaning', 'action', 'cta']
            for scene in scene_required:
                if scene not in content['video_scenes']:
                    raise ValueError(f"Missing video scene: {scene}")

            # Generate dynamic hashtags (same as V1)
            hashtag_list = self.hashtag_manager.generate_hashtags(
                category=category,
                count=15
            )
            hashtags_str = " ".join(hashtag_list)
            self.hashtag_manager.mark_hashtags_used(hashtag_list)

            # Build caption from video scenes (same as V1)
            scenes = content['video_scenes']
            caption = content.get('caption',
                f"{scenes['hook']} {scenes['meaning']} {scenes['action']} {scenes['cta']}")

            # Format result to match V1 structure
            result = {
                "video_scenes": content['video_scenes'],
                "caption": caption,
                "hashtags": hashtags_str,
                # V2 additions:
                "prompt_version": 'v2' if self.use_v2_prompts else 'v1',
                "hook_style_used": hook_style,
                "content_angle": content.get('content_angle', 'unknown'),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }

            logger.info(f"✅ Content generated successfully")
            logger.info(f"   Hook style: {hook_style}")
            logger.info(f"   Hook: {content['video_scenes']['hook'][:50]}...")
            logger.info(f"   Caption: {len(caption)} chars")
            logger.info(f"   Hashtags: {len(hashtag_list)}")
            logger.info(f"   Tokens: {result['tokens_used']}")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON: {e}")
            logger.error(f"Response preview: {content_text[:300]}")
            # Fall back to V1-style generation
            return self._get_fallback_content(topic_value, category)
        except Exception as e:
            logger.error(f"❌ Content generation failed: {e}")
            # Fall back to V1-style generation
            return self._get_fallback_content(topic_value, category)

    def _build_system_prompt(self) -> str:
        """Build system prompt from config."""
        return self.prompts.get('system_prompt', '')

    def _build_user_prompt(self, topic: str, category: str, hook_style: str) -> str:
        """
        Build user prompt with hook style guidance.

        Args:
            topic: Angel number or topic (e.g. "1111")
            category: Content category (e.g. "angel_numbers")
            hook_style: Selected hook style

        Returns:
            Complete prompt string with placeholders filled
        """
        # Get base prompt
        if self.use_v2_prompts and 'topic_specific_prompt_v2' in self.prompts:
            base_prompt = self.prompts['topic_specific_prompt_v2']
        else:
            # Fallback to V1 prompt if V2 not available
            base_prompt = self.prompts.get('topic_specific_prompt', '')

        # Add specific hook examples if available
        if 'hook_templates' in self.prompts and hook_style in self.prompts['hook_templates']:
            hook_examples = self.prompts['hook_templates'][hook_style]
            hook_guidance = f"\n\n## SELECTED HOOK STYLE: {hook_style.upper()}\n"
            hook_guidance += "Use ONE of these hook patterns:\n"
            for example in hook_examples[:3]:  # Show top 3 examples
                hook_guidance += f"- {example}\n"
            base_prompt += hook_guidance

        # Replace placeholders
        prompt = base_prompt.replace('{TOPIC}', topic)
        prompt = prompt.replace('{CATEGORY}', category)
        prompt = prompt.replace('{topic}', topic.lower())

        return prompt

    def _get_fallback_content(self, topic: str, category: str) -> Dict[str, any]:
        """
        Fallback content if generation fails.
        Returns V1-compatible structure.
        """
        logger.warning("Using fallback content due to generation failure")

        content = {
            "hook": f"Keep seeing {topic} everywhere?",
            "meaning": f"{topic} is a powerful sign from the universe calling your attention.",
            "action": "Pause. Breathe. Trust your intuition about what this means for you.",
            "cta": "Follow @the17project for daily angel number guidance."
        }

        caption = f"{content['hook']} {content['meaning']} {content['action']} {content['cta']}"

        # Generate dynamic hashtags
        hashtag_list = self.hashtag_manager.generate_hashtags(
            category=category,
            count=15
        )
        hashtags_str = " ".join(hashtag_list)
        self.hashtag_manager.mark_hashtags_used(hashtag_list)

        return {
            "video_scenes": content,
            "caption": caption,
            "hashtags": hashtags_str,
            "prompt_version": 'v2',
            "hook_style_used": 'fallback',
            "content_angle": 'fallback',
            "tokens_used": 0
        }


# Backwards-compatible function interface
def generate_content(topic: Dict[str, str]) -> Dict:
    """
    Backwards-compatible function interface.

    Can be called same way as original generate_content.py
    """
    generator = ContentGeneratorV2()
    return generator.generate_content(topic)


def main():
    """Test content generator V2."""
    generator = ContentGeneratorV2()

    print("\n" + "="*70)
    print("TESTING V2 CONTENT GENERATOR - IMPROVED HOOKS")
    print("="*70)

    test_topics = [
        {"value": "1111", "type": "angel_numbers"},
        {"value": "717", "type": "angel_numbers"},
        {"value": "333", "type": "angel_numbers"}
    ]

    for topic in test_topics:
        print(f"\n📝 Topic: {topic['value']}")
        print("-" * 70)

        content = generator.generate_content(topic)

        print(f"\nHOOK: {content['video_scenes']['hook']}")
        print(f"MEANING: {content['video_scenes']['meaning']}")
        print(f"ACTION: {content['video_scenes']['action']}")
        print(f"CTA: {content['video_scenes']['cta']}")
        print(f"\nHook Style: {content['hook_style_used']}")
        print(f"Tokens: {content['tokens_used']}")
        print("-" * 70)

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
