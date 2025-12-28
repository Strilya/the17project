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

HOOK EXAMPLES (POSITIVE):
- "Saw {angel_number} right before my biggest breakthrough. Here's what it meant..."
- "Woke up at {angel_number} the night before landing my dream job. Not random..."
- "Kept seeing {angel_number} during my search. Then I met my soulmate. Here's why..."
- "Kept seeing {angel_number} everywhere before my life completely transformed. Here's why..."

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
            temperature=0.95,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_json(response.content[0].text)
    
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

HOOK EXAMPLES (POSITIVE):
- "Stop making wishes at {angel_number}. That's not how it works. Here's the POWERFUL truth..."
- "Everyone thinks {angel_number} means wait. They're missing the OPPORTUNITY. Listen..."
- "You're seeing {angel_number} but nothing manifests? You're ONE step from breakthrough..."

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
            temperature=0.95,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_json(response.content[0].text)
    
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

HOOK EXAMPLES (POSITIVE):
- "Client saw {angel_number} every single day for three months straight. Then landed her DREAM job..."
- "She finally listened to {angel_number}. Made the leap. Doubled her income in 6 months..."
- "Woke up at {angel_number} for 30 days in a row. Finally listened. Met her soulmate..."

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
            temperature=0.95,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_json(response.content[0].text)
    
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

