"""
Content Generator - OPTIMIZED FOR 17 SECONDS

Generates SHORT, punchy content that fits naturally in 17 seconds:
- Hook: 3-4s (8-12 words)
- Meaning: 5-6s (15-20 words) 
- Action: 5-6s (15-20 words)
- CTA: 2-3s (6-10 words)

Total: ~16-19 seconds of natural speech at 1.15-1.25x speed
"""

import os
import json
import logging
from typing import Dict, Optional
from pathlib import Path
from anthropic import Anthropic

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generate SHORT Instagram Reel content using Claude API."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize ContentGenerator."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "prompts.json"

        with open(config_path, 'r') as f:
            self.prompts = json.load(f)

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

        logger.info("ContentGenerator initialized (17s optimized)")

    def generate_content(
        self,
        topic: str,
        category: str = "angel_numbers",
        style: str = "spiritual"
    ) -> Dict[str, str]:
        """
        Generate SHORT 4-scene reel content.
        
        CRITICAL: Content must fit in 17 seconds total.
        """
        logger.info(f"\nGenerating content for: {topic} ({category})")

        # Build strict prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(topic, category, style)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,  # Limit length
                temperature=0.8,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )

            content_text = response.content[0].text.strip()
            
            # Parse response
            content = self._parse_content(content_text)
            
            # Validate length
            self._validate_length(content)
            
            logger.info("✅ Content generated (17s optimized)")
            return content

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return self._get_fallback_content(topic)

    def _build_system_prompt(self) -> str:
        """Build system prompt with STRICT length requirements."""
        return """You are an expert Instagram Reel content creator for The17Project - a spiritual productivity brand.

YOUR CRITICAL TASK: Generate content that fits in EXACTLY 17 SECONDS when read aloud.

STRICT WORD LIMITS (NON-NEGOTIABLE):
- Hook: 8-12 words (3-4 seconds)
- Meaning: 15-20 words (5-6 seconds)
- Action: 15-20 words (5-6 seconds)
- CTA: 6-10 words (2-3 seconds)

STYLE RULES:
- Direct, punchy, powerful
- No fluff or filler words
- Every word must count
- Spiritual but actionable
- Use "you" and "your" (personal)
- End CTA with @the17project

OUTPUT FORMAT (EXACTLY THIS):
HOOK: [8-12 words max]
MEANING: [15-20 words max]
ACTION: [15-20 words max]
CTA: [6-10 words max]

EXAMPLE (GOOD LENGTH):
HOOK: Seeing 717 everywhere?
MEANING: Angel number 717 signals spiritual awakening and new beginnings approaching fast.
ACTION: Trust your intuition today. The universe is guiding you forward.
CTA: Follow @the17project for daily guidance.

DO NOT exceed word limits. Quality over quantity."""

    def _build_user_prompt(self, topic: str, category: str, style: str) -> str:
        """Build user prompt for specific topic."""
        
        category_context = {
            "angel_numbers": "Focus on spiritual meaning, synchronicity, and divine guidance",
            "productivity": "Focus on actionable systems, results, and efficiency",
            "manifestation": "Focus on visualization, energy, and conscious creation",
            "spiritual_growth": "Focus on inner transformation, awareness, and evolution"
        }
        
        context = category_context.get(category, "Focus on practical spiritual wisdom")
        
        return f"""Generate a 17-SECOND Instagram Reel about: {topic}

Category: {category}
Style: {style}
Context: {context}

CRITICAL REQUIREMENTS:
1. Hook: 8-12 words MAX - grab attention immediately
2. Meaning: 15-20 words MAX - core message, spiritual insight
3. Action: 15-20 words MAX - practical step they can take TODAY
4. CTA: 6-10 words MAX - must end with @the17project

TONE: Mystical yet grounded, inspiring yet practical

Remember: This will be READ ALOUD in 17 seconds. Keep it SHORT and POWERFUL.

Generate now:"""

    def _parse_content(self, text: str) -> Dict[str, str]:
        """Parse Claude's response into 4 scenes."""
        content = {
            "hook": "",
            "meaning": "",
            "action": "",
            "cta": ""
        }

        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("HOOK:"):
                content["hook"] = line.replace("HOOK:", "").strip()
            elif line.startswith("MEANING:"):
                content["meaning"] = line.replace("MEANING:", "").strip()
            elif line.startswith("ACTION:"):
                content["action"] = line.replace("ACTION:", "").strip()
            elif line.startswith("CTA:"):
                content["cta"] = line.replace("CTA:", "").strip()

        # Fallback if parsing failed
        if not all(content.values()):
            logger.warning("Parse failed, using fallback")
            return self._get_fallback_content("spiritual guidance")

        return content

    def _validate_length(self, content: Dict[str, str]):
        """Validate word counts."""
        limits = {
            "hook": (8, 12),
            "meaning": (15, 20),
            "action": (15, 20),
            "cta": (6, 10)
        }

        for scene, text in content.items():
            word_count = len(text.split())
            min_words, max_words = limits[scene]
            
            if word_count < min_words:
                logger.warning(f"{scene}: {word_count} words (too short, min {min_words})")
            elif word_count > max_words:
                logger.warning(f"{scene}: {word_count} words (too long, max {max_words})")
            else:
                logger.info(f"{scene}: {word_count} words ✅")

    def _get_fallback_content(self, topic: str) -> Dict[str, str]:
        """Fallback content if generation fails."""
        return {
            "hook": "Ready for transformation?",
            "meaning": "Small daily actions create massive shifts in your reality.",
            "action": "Choose one positive change. Start today. Stay consistent.",
            "cta": "Follow @the17project for guidance."
        }


def main():
    """Test content generator."""
    generator = ContentGenerator()

    print("\n" + "="*70)
    print("TESTING 17-SECOND CONTENT GENERATOR")
    print("="*70)

    topics = [
        ("Angel number 717", "angel_numbers"),
        ("Morning routine power", "productivity"),
        ("Manifesting abundance", "manifestation")
    ]

    for topic, category in topics:
        print(f"\n📝 Topic: {topic}")
        print("-" * 70)
        
        content = generator.generate_reel_content(topic, category)
        
        print(f"\nHOOK: {content['hook']}")
        print(f"MEANING: {content['meaning']}")
        print(f"ACTION: {content['action']}")
        print(f"CTA: {content['cta']}")
        
        total_words = sum(len(text.split()) for text in content.values())
        print(f"\nTotal words: {total_words} (target: 44-62)")
        print("-" * 70)

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
