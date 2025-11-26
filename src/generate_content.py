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
import random
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from anthropic import Anthropic

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generate HIGH-QUALITY Instagram Reel content with VARIETY."""
    
    # CONTENT VARIETY - Rotate hook styles for engagement
    HOOK_STYLES = [
        "question",      # "Ever wonder why 717 keeps appearing?"
        "statement",     # "Here's what 717 really means..."
        "statistic",     # "717 appears in 3 major spiritual texts"
        "challenge",     # "Next time you see 717, do this..."
        "revelation"     # "I just learned something about 717..."
    ]
    
    # CTA VARIETY - Rotate calls to action
    CTA_TEMPLATES = [
        "Follow @the17project for daily {topic} guidance",
        "Want more {topic} wisdom? Follow @the17project daily",
        "@the17project drops {topic} secrets every single day",
        "Follow @the17project for your daily {topic} dose",
        "Get daily {topic} insights at @the17project now"
    ]

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
        Generate HIGH-QUALITY varied content.
        
        CRITICAL: Content must fit in 17-21 seconds total.
        """
        logger.info(f"\nGenerating QUALITY content: {topic} ({category})")

        # Pick random hook style for VARIETY
        hook_style = random.choice(self.HOOK_STYLES)
        logger.info(f"Using hook style: {hook_style}")

        # Build strict prompt with variety
        system_prompt = self._build_system_prompt(hook_style)
        user_prompt = self._build_user_prompt(topic, category, style, hook_style)

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

            logger.info("✅ Content generated with VARIETY")

            # Pick random CTA template
            cta_topic_map = {
                "angel_numbers": "angel number",
                "productivity": "productivity",
                "manifestation": "manifestation",
                "spiritual_growth": "spiritual"
            }
            cta_topic = cta_topic_map.get(category, "spiritual")
            
            # Use random CTA template OR keep generated CTA if it's good
            if "@the17project" in content['cta']:
                # Generated CTA is good, keep it
                pass
            else:
                # Use random template as fallback
                cta_template = random.choice(self.CTA_TEMPLATES)
                content['cta'] = cta_template.format(topic=cta_topic)
            
            # Format for workflow
            caption = f"{content['hook']} {content['meaning']} {content['action']} {content['cta']}"

            return {
                "video_scenes": content,
                "caption": caption,
                "hashtags": "#the17project #angelnumbers #spirituality #manifestation #lawofattraction"
            }

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return self._get_fallback_content(topic)

    def _build_system_prompt(self, hook_style: str) -> str:
        """Build system prompt with VARIETY and quality."""
        
        hook_instructions = {
            "question": "Start with a compelling QUESTION that makes them curious",
            "statement": "Start with a bold STATEMENT that challenges assumptions",
            "statistic": "Start with a surprising FACT or STATISTIC",
            "challenge": "Start with a direct CHALLENGE or invitation to try something",
            "revelation": "Start with 'I just discovered' or 'Here's what nobody tells you'"
        }
        
        hook_instruction = hook_instructions.get(hook_style, "Start with an attention-grabbing hook")
        
        return f"""You are an EXPERT Instagram Reel content creator for The17Project - a spiritual productivity brand.

YOUR MISSION: Create ENGAGING, VARIED content that feels fresh every time.

TODAY'S HOOK STYLE: {hook_style.upper()}
{hook_instruction}

STRICT WORD LIMITS:
- Hook: 10-12 words ({hook_style} style)
- Meaning: 18-22 words (deep insight with specifics)
- Action: 18-22 words (concrete, actionable step)
- CTA: 8-10 words (natural, not salesy)

QUALITY RULES:
âœ… Use specific numbers, examples, or details (not generic fluff)
âœ… Make it feel personal ("you", "your")
âœ… Include concrete actions they can take TODAY
âœ… Vary your language - don't repeat the same phrases
âœ… Sound like a real human, not a bot

❌ NO generic spiritual clichÃ©s
❌ NO vague platitudes
❌ NO repetitive patterns

OUTPUT FORMAT:
HOOK: [10-12 words, {hook_style} style]
MEANING: [18-22 words with specific insight]
ACTION: [18-22 words with concrete steps]
CTA: [8-10 words, natural and engaging]

EXAMPLE ({hook_style} style):
{self._get_example_for_style(hook_style)}

Generate content that people will STOP scrolling for."""

    def _get_example_for_style(self, hook_style: str) -> str:
        """Get example content for specific hook style."""
        examples = {
            "question": """HOOK: Why does 717 keep showing up in your life right now?
MEANING: Angel number 717 signals major spiritual awakening and your soul aligning with its true purpose today.
ACTION: Close your eyes. Take three deep breaths. Ask your intuition what message 717 has for you.
CTA: Follow @the17project for daily angel number guidance and wisdom.""",
            
            "statement": """HOOK: Most people miss the real meaning behind angel number 717 completely.
MEANING: It's not just awakening - 717 means your manifestation power is reaching its absolute peak right now.
ACTION: Write down one impossible dream today. The universe is literally conspiring to make it real for you.
CTA: Want more spiritual insights like this? Follow @the17project for daily wisdom.""",
            
            "statistic": """HOOK: Angel number 717 appears during life's three most transformative spiritual moments predictably.
MEANING: Before major awakening, during soul purpose alignment, and right when manifestation ability peaks in your journey.
ACTION: Notice when you see 717 next. That's the universe confirming you're on your highest path forward.
CTA: Get daily angel number secrets at @the17project - follow us now today.""",
            
            "challenge": """HOOK: Next time you see 717, stop everything and do this immediately.
MEANING: Angel number 717 is your soul's alarm clock, signaling that spiritual awakening is happening right this moment.
ACTION: Pause. Close your eyes. Ask yourself: what am I being called to do differently starting today?
CTA: Follow @the17project daily for more spiritual challenges and ancient wisdom revealed.""",
            
            "revelation": """HOOK: I just discovered what 717 really means and it changes everything completely.
MEANING: It's not random synchronicity - 717 appears when your soul is ready for its next quantum leap forward.
ACTION: Trust the path you're on right now. The universe is preparing something incredible for you soon.
CTA: @the17project drops daily spiritual revelations - follow for your daily dose of wisdom."""
        }
        return examples.get(hook_style, examples["question"])

    def _build_user_prompt(self, topic: str, category: str, style: str, hook_style: str) -> str:
        """Build user prompt with variety and context."""
        
        # Get current month for seasonal context
        current_month = datetime.now().strftime("%B")
        
        category_context = {
            "angel_numbers": f"Focus on spiritual meaning, synchronicity, divine timing. Consider {current_month} energy.",
            "productivity": f"Focus on actionable systems, real results. Make it relevant to {current_month} goals.",
            "manifestation": f"Focus on visualization, energy alignment. Tie to {current_month} intentions.",
            "spiritual_growth": f"Focus on transformation, awareness. Connect to {current_month} spiritual themes."
        }
        
        context = category_context.get(category, "Focus on practical spiritual wisdom")
        
        # Map category to CTA topic
        cta_topics = {
            "angel_numbers": "angel number",
            "productivity": "productivity",
            "manifestation": "manifestation",
            "spiritual_growth": "spiritual growth"
        }
        cta_topic = cta_topics.get(category, "spiritual")
        
        return f"""Generate a HIGH-QUALITY Instagram Reel about: {topic}

Category: {category}
Hook Style: {hook_style} (MUST use this specific style)
Context: {context}
Month: {current_month} (consider seasonal relevance if applicable)

REQUIREMENTS:
1. Hook: 10-12 words - Use {hook_style} style (question/statement/statistic/challenge/revelation)
2. Meaning: 18-22 words - Provide SPECIFIC insight with details (not generic fluff)
3. Action: 18-22 words - Give CONCRETE steps they can take TODAY
4. CTA: 8-10 words - Natural language, must include @the17project

MAKE IT QUALITY:
✅ Specific (use numbers, examples, concrete details)
✅ Personal (use "you", "your" - make it feel direct)
✅ Actionable (clear next steps, not vague advice)
✅ Fresh (avoid clichés and overused spiritual phrases)
✅ Engaging (make them WANT to watch til the end)

Generate NOW:"""

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
            "hook": (10, 12),
            "meaning": (18, 22),
            "action": (18, 22),
            "cta": (8, 10)
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
        content = {
            "hook": "Ready for transformation?",
            "meaning": "Small daily actions create massive shifts in your reality.",
            "action": "Choose one positive change. Start today. Stay consistent.",
            "cta": "Follow @the17project for guidance."
        }

        caption = f"{content['hook']} {content['meaning']} {content['action']} {content['cta']}"

        return {
            "video_scenes": content,
            "caption": caption,
            "hashtags": "#the17project #angelnumbers #spirituality"
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
