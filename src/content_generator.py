"""
Content Generator - Creates engaging angel number content
Based on research: time-specific meanings, life situations, manifestation techniques
"""

import os
import json
import random
from anthropic import Anthropic

class ContentGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
        
        # Most common angel numbers (clock-based + meaningful)
        self.angel_numbers = [
            "1111", "111", "222", "333", "444", "555", "666", "777", "888", "999",
            "1212", "1010", "1234", "911", "711"
        ]
        
    def generate_storytelling(self, angel_number):
        """Deep storytelling - vulnerability, personal authority, emotional"""

        prompt = f"""Create viral angel number content for {angel_number}.

CRITICAL RULES - NO BULLSHIT CONTENT:
✅ POSITIVE: transformation, growth, abundance, opportunity, success, breakthrough, awakening
❌ AVOID: death, divorce, loss, tragedy, failure, breakup, grief, illness, fired
❌ BANNED PHRASES: "within X minutes", "write on paper and burn it", "say X times", "place under pillow", "light a candle", "hold to heart", "whisper your dreams"
❌ NO RITUALS: No physical actions, timing requirements, or made-up ceremonies
✅ ALLOWED ACTIONS: Mental/emotional shifts, awareness, trust, reflection, decision-making, taking aligned action
✅ TONE: Empowering but realistic, grounded, authentic, actionable WITHOUT being weird

STYLE: Deep storytelling, Morgan Freeman narrator voice
TONE: Vulnerable, authoritative, emotional weight, UPLIFTING

DURATION REQUIREMENTS (STRICT):
- Target: 15-20 seconds spoken content
- Maximum allowed: 22 seconds spoken content
- With 2s end card = 24s total (well under 30s limit)
- Be CONCISE, PUNCHY, FAST-PACED

STRUCTURE (strict word counts - DO NOT EXCEED):
- Hook (8-10 words max): Personal vulnerability or controversial statement (POSITIVE outcome)
- Meaning (20-25 words max): Real numerological meaning, what it signals (GROUNDED)
- Action (25-30 words max): Practical mental/emotional guidance, what to BE AWARE OF, trust your intuition (NO RITUALS)
- CTA (8-10 words max): Strong follow + engagement question

HOOK EXAMPLES - HIGH URGENCY/CURIOSITY (pick one randomly):
- "STOP scrolling if you keep seeing {angel_number}..."
- "WAIT - if {angel_number} keeps appearing, this is urgent..."
- "If you're seeing {angel_number}, the universe needs you to hear this NOW..."
- "PAUSE. You seeing {angel_number} is NOT a coincidence..."
- "{angel_number} is literally stalking you. Here's why..."
- "The REAL reason {angel_number} won't leave you alone..."
- "What they don't tell you about seeing {angel_number}..."
- "I ignored {angel_number} for months. Biggest mistake ever..."
- "Your guides are SCREAMING {angel_number} at you because..."
- "The hidden message behind {angel_number} that changes everything..."
- "If {angel_number} keeps finding you, you're being chosen..."
- "{angel_number} appearing means your life is about to shift..."
- "POV: You finally understand why {angel_number} follows you..."
- "That feeling when {angel_number} appears? Trust it..."
- "You're not crazy for noticing {angel_number}. You're awakening..."

MEANING EXAMPLES (GROUNDED - NO BULLSHIT):
- "Seeing {angel_number} means you're exactly where you need to be. Trust your path and keep going."
- "Keep seeing {angel_number}? The universe is confirming you're on the right track. Stay aware."
- "{angel_number} appearing means major alignment is happening. Your intuition is spot-on right now."

ACTION EXAMPLES (MENTAL/EMOTIONAL - NO RITUALS):
- "When you see {angel_number}, pause and notice what you were thinking about. That's your answer."
- "Seeing {angel_number} is confirmation to trust that decision you've been considering. Your gut knows."
- "The {angel_number} signal means: stay aware, trust your intuition, and take that next step you've been putting off."

Return ONLY valid JSON:
{{
  "hook": "8-10 word vulnerable/controversial hook with POSITIVE outcome",
  "meaning": "20-25 word time/situation-specific meaning (EMPOWERING)",
  "action": "25-30 word manifestation technique with specific steps",
  "cta": "8-10 word follow prompt with question"
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._fix_angel_number(self._parse_json(response.content[0].text), angel_number)

    def generate_practical(self, angel_number):
        """Practical tips - myth-busting, what to actually do"""

        prompt = f"""Create myth-busting angel number content for {angel_number}.

CRITICAL RULES - POSITIVE CONTENT ONLY:
- NO mentions of death, divorce, loss, tragedy, failure, breakup, grief
- Focus on POSITIVE transformation, growth, abundance, opportunity, success
- Use uplifting scenarios and outcomes
- TONE: Uplifting, empowering, hopeful, inspiring
- AVOID: Death, dying, loss, divorce, breakup, failure, tragedy, accident, grief, fired, illness
- USE: Breakthrough, abundance, alignment, opportunity, awakening, manifestation, success, love, clarity, peace

STYLE: Controversial, practical, authority
TONE: Direct, challenging common beliefs, actionable, POSITIVE

DURATION REQUIREMENTS (STRICT):
- Target: 15-20 seconds spoken content
- Maximum allowed: 22 seconds spoken content
- With 2s end card = 24s total (well under 30s limit)
- Be CONCISE, PUNCHY, FAST-PACED

STRUCTURE (strict word counts - DO NOT EXCEED):
- Hook (8-10 words max): Challenge a common belief or mistake (POSITIVE framing)
- Meaning (20-25 words max): What people get wrong and the real meaning (EMPOWERING)
- Action (25-30 words max): Specific technique or ritual to do RIGHT NOW
- CTA (8-10 words max): Follow + share your experience prompt

HOOK EXAMPLES - HIGH URGENCY/MYTH-BUSTING (pick one randomly):
- "STOP wishing on {angel_number}. Do THIS instead..."
- "Everyone gets {angel_number} WRONG. Here's the truth..."
- "You're seeing {angel_number} but nothing happens? You're missing THIS..."
- "{angel_number} isn't luck. It's a WARNING to act NOW..."
- "The universe sent {angel_number} because you're IGNORING something..."
- "I tested this {angel_number} method. Results were INSANE..."
- "{angel_number} on repeat means ONE thing. And it's urgent..."
- "NOBODY talks about this {angel_number} secret..."
- "{angel_number} is literally screaming at you. Here's why..."
- "Seeing {angel_number}? Your manifestation window closes SOON..."
- "{angel_number} just exposed what you need to do next..."
- "The {angel_number} truth that spiritual gurus WON'T tell you..."
- "{angel_number} is your FINAL sign. Stop waiting..."
- "Why {angel_number} keeps appearing until you DO this..."
- "{angel_number} chose YOU. Here's what that actually means..."

MEANING EXAMPLES (myth-busting - POSITIVE):
- "{angel_number} doesn't mean 'make a wish' - it means your manifestation window is OPEN for the next 17 minutes"
- "Seeing {angel_number} on clock vs receipt means different things - here's what each actually signals for your ABUNDANCE"
- "{angel_number} appearing multiple times in one day isn't repetition - it's DIVINE AMPLIFICATION"

ACTION EXAMPLES (specific rituals - POSITIVE):
- "Next time you see {angel_number}: grab your phone, set timer for 7 minutes, write 7 dreams you're calling in"
- "The {angel_number} abundance hack: identify 4 aligned actions, complete them in 4 hours, watch miracles unfold"
- "See {angel_number}? Text that person. Make that call. Take that leap. You have 11 minutes of divine timing"

Return ONLY valid JSON:
{{
  "hook": "string",
  "meaning": "string",
  "action": "string",
  "cta": "string"
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._fix_angel_number(self._parse_json(response.content[0].text), angel_number)

    def generate_insights(self, angel_number):
        """Client stories - transformation, real examples, emotional weight"""

        prompt = f"""Create transformation story content for {angel_number}.

CRITICAL RULES - POSITIVE CONTENT ONLY:
- NO mentions of death, divorce, loss, tragedy, failure, breakup, grief
- Focus on POSITIVE transformation, growth, abundance, opportunity, success
- Use uplifting scenarios: "promotion", "breakthrough", "soulmate", "abundance", "dream job", "healing"
- TONE: Uplifting, empowering, hopeful, inspiring, mysterious
- AVOID: Death, dying, loss, divorce, breakup, failure, tragedy, accident, grief, fired, illness, toxic relationships
- USE: Breakthrough, abundance, alignment, opportunity, awakening, manifestation, success, love, clarity, peace, soulmate, promotion

STYLE: Storytelling, case study, emotional
TONE: Mysterious, intriguing, POSITIVE transformation-based

DURATION REQUIREMENTS (STRICT):
- Target: 15-20 seconds spoken content
- Maximum allowed: 22 seconds spoken content
- With 2s end card = 24s total (well under 30s limit)
- Be CONCISE, PUNCHY, FAST-PACED

STRUCTURE (strict word counts - DO NOT EXCEED):
- Hook (8-10 words max): Client story setup or mysterious pattern (POSITIVE outcome)
- Meaning (20-25 words max): What the pattern revealed (EMPOWERING message)
- Action (25-30 words max): What they did and the POSITIVE outcome
- CTA (8-10 words max): Follow for stories + share yours prompt

HOOK EXAMPLES - STORY-BASED URGENCY (pick one randomly):
- "She ignored {angel_number} for weeks. Then THIS happened..."
- "He finally listened to {angel_number}. His life will NEVER be the same..."
- "{angel_number} appeared before her biggest breakthrough. Coincidence? NO..."
- "What happens when you ACTUALLY trust {angel_number}? Watch this..."
- "I tracked {angel_number} for 30 days. What I found was SHOCKING..."
- "{angel_number} kept appearing. She finally acted. Now she's living her DREAM..."
- "The moment he trusted {angel_number}, EVERYTHING changed..."
- "{angel_number} was trying to tell her something. She almost missed it..."
- "True story: {angel_number} saved her from making a HUGE mistake..."
- "She saw {angel_number} right before meeting her soulmate. Here's what happened..."
- "{angel_number} appeared 7 times in one day. The message was CLEAR..."
- "He ignored {angel_number}. Then regretted it. Don't make his mistake..."
- "{angel_number} showed up when she needed it MOST. This is powerful..."
- "The {angel_number} pattern that predicted her entire breakthrough..."
- "After seeing {angel_number}, she quit her job. Best decision EVER..."

MEANING EXAMPLES (revelation - POSITIVE):
- "{angel_number} was guiding her toward the breakthrough she couldn't see yet - the universe knew"
- "Turns out {angel_number} only appears when you're about to meet your life-changing opportunity"
- "The pattern of {angel_number} was showing the EXACT timing of when abundance would flow"

ACTION EXAMPLES (what happened - POSITIVE):
- "She finally started journaling every time she saw {angel_number}. Pattern emerged. Took the leap. Now making triple"
- "He took action within 5 minutes of each {angel_number} sighting. Within 2 months, complete transformation, dream life"
- "Listened the 7th time. Something inside said YES. Changed everything that day. Now living her purpose"

Return ONLY valid JSON:
{{
  "hook": "string",
  "meaning": "string",
  "action": "string",
  "cta": "string"
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._fix_angel_number(self._parse_json(response.content[0].text), angel_number)

    def _parse_json(self, text):
        """Extract JSON from Claude's response"""
        try:
            return json.loads(text)
        except:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
            raise ValueError(f"Could not parse JSON from response: {text}")

    def _fix_angel_number(self, content, correct_number):
        """Replace any wrong angel numbers in content with the correct one"""
        import re
        # Pattern to find 3-4 digit numbers that look like angel numbers
        angel_pattern = r'\b(\d{3,4})\b'

        for key in ['hook', 'meaning', 'action', 'cta']:
            if key in content and content[key]:
                text = content[key]
                # Find all number matches
                matches = re.findall(angel_pattern, text)
                for match in matches:
                    # If it's a different angel number (not time like 11, 17, etc.)
                    if match != correct_number and len(match) >= 3:
                        text = text.replace(match, correct_number)
                        print(f"   ⚠️  Fixed wrong number {match} → {correct_number} in {key}")
                content[key] = text
        return content

