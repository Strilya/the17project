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

HOOK EXAMPLES - USE VARIETY (POSITIVE) - 30 OPTIONS:
- "If you're seeing {angel_number}, stop scrolling. This is for you..."
- "Why does {angel_number} keep showing up? Let me explain..."
- "Okay so {angel_number} is literally everywhere. What does this mean?"
- "You're not crazy for seeing {angel_number}. Here's what's happening..."
- "{angel_number} again? The universe is trying to tell you something..."
- "Real talk: {angel_number} is not a coincidence. Listen to this..."
- "So I looked up {angel_number} and... this explains everything..."
- "Why am I seeing {angel_number} constantly? Here's the real answer..."
- "If {angel_number} keeps appearing, pay attention to this part..."
- "The truth about {angel_number}? Way deeper than you think..."
- "Seeing {angel_number} everywhere lately? This is what it means..."
- "{angel_number} on your clock right now? Not random. Here's why..."
- "Can we talk about {angel_number}? This number is significant..."
- "If you keep seeing {angel_number}, the universe is signaling you..."
- "Wait... you're seeing {angel_number} too? You need to hear this..."
- "{angel_number} is following you for a reason. Let me explain..."
- "The meaning of {angel_number} just clicked. Mind actually blown..."
- "So about {angel_number}... there's something you need to know..."
- "If {angel_number} is your number right now, this is your sign..."
- "Everyone keeps asking about {angel_number}. Here's the truth..."
- "Seeing {angel_number} and feeling confused? This makes it clear..."
- "The {angel_number} energy is strong right now. Here's what to do..."
- "If {angel_number} is popping up, don't ignore it. Here's why..."
- "Real question: why does {angel_number} follow me everywhere?"
- "Okay but {angel_number} is actually wild when you understand it..."
- "You seeing {angel_number} means you're being called. Pay attention..."
- "If {angel_number} keeps showing up, you're aligned. Here's your next move..."
- "The {angel_number} code is activating for you. Ready for this?"
- "Why {angel_number}? Why now? You're ready. Here's what's next..."
- "Keep seeing {angel_number}? That's your green light. Go..."

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

HOOK EXAMPLES - USE VARIETY (POSITIVE) - 30 OPTIONS:
- "Stop wishing on {angel_number}. Do this instead. Game changer..."
- "Everyone thinks {angel_number} means wait. It actually means the opposite..."
- "You're seeing {angel_number} but nothing happens? Missing one thing..."
- "{angel_number} isn't luck. It's alignment. Big difference. Let me explain..."
- "Seeing {angel_number} everywhere? The universe mapped your next move..."
- "Tested this {angel_number} method for weeks. Results speak for themselves..."
- "{angel_number} on repeat? That's not repetition. That's amplification..."
- "What they don't tell you about {angel_number}... this changes everything..."
- "So {angel_number} doesn't mean good luck. It means you ARE the luck..."
- "{angel_number} is literally a green light. Why are you still waiting?"
- "That {angel_number} you saw? Confirmation you're already on it..."
- "{angel_number} is the sign. The work is what comes after..."
- "Here's what {angel_number} actually means: you're already ready. Move..."
- "Seeing {angel_number} multiple times isn't random. It's emphasis. Act..."
- "{angel_number} means your window's open. And it's getting wider..."
- "{angel_number} is the universe literally saying YES. Take the hint..."
- "Decode {angel_number} like this and everything shifts. Watch..."
- "{angel_number} shows up when you're close. Keep going. You're almost there..."
- "Clock vs receipt {angel_number}? Different meanings. Know the difference..."
- "{angel_number} confirms you're way more ready than you realize..."
- "The universe sent you {angel_number}. Your move. Your moment..."
- "{angel_number} is your cue to move NOW. Not later. Now..."
- "You saw {angel_number}. That's confirmation. Your next move is clear..."
- "Most people see {angel_number} and freeze. Winners see it and go..."
- "{angel_number} isn't whispering. It's announcing your moment. Step up..."
- "That {angel_number} pattern? Your personal code. Crack it like this..."
- "Seeing {angel_number} means you've been activated. Time to rise..."
- "{angel_number} is testing if you trust yourself. Do you? Prove it..."
- "When {angel_number} appears, doors open. Question is: will you walk through?"
- "You keep seeing {angel_number} because abundance chose YOU. Accept it..."

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

HOOK EXAMPLES - USE VARIETY (POSITIVE) - 30 OPTIONS:
- "Someone saw {angel_number} daily for months. Then their whole life flipped. Wild..."
- "She listened to {angel_number} and took the leap. Everything changed overnight..."
- "{angel_number} showed up before her interview. She went with it. Boom. Hired..."
- "What happens when you actually act on {angel_number}? Let me show you..."
- "Thought {angel_number} was random. Tracked it for weeks. Patterns don't lie..."
- "{angel_number} during walks. During coffee. During work. Then it clicked..."
- "Saw {angel_number} three days straight. Took it seriously. Results are crazy..."
- "Every time {angel_number} appears, opportunities follow. Tested this theory. Confirmed..."
- "Started trusting {angel_number}. 90 days later. Completely different person..."
- "Tracked every {angel_number} sighting for a month. The message was clear..."
- "Pattern I noticed: {angel_number} before every win. Every. Single. Time..."
- "{angel_number} when doors open. {angel_number} when paths clear. Notice it?"
- "He trusted {angel_number}. 60 days. Whole new reality. True story..."
- "Act fast when {angel_number} hits. Like within minutes. Watch what happens..."
- "Aligned with {angel_number} energy. Opportunities just started flooding. No cap..."
- "Documented {angel_number} for months. The clarity that emerged was wild..."
- "{angel_number} before meeting the one. She noticed. Everything aligned perfectly..."
- "Followed {angel_number} despite fear. Best decision ever. No question..."
- "When {angel_number} hits and you just know. That feeling. Trust it always..."
- "{angel_number} at perfect moments. Learned to ride that wave. Life-changing..."
- "After the breakthrough, {angel_number} stopped showing up. Work was done..."
- "Weekly {angel_number} for months. Each sighting brought me closer. Wild journey..."
- "Friend manifested with {angel_number}. Results speak louder than I can..."
- "{angel_number} when you need it most. Universe timing is always perfect..."
- "90-day {angel_number} experiment. Patterns revealed my entire roadmap. Insane..."
- "After {angel_number} appeared, took the leap. Everything unlocked. Instant..."
- "Saw {angel_number} and made the move. Divine timing. No other explanation..."
- "Following {angel_number} breadcrumbs led me exactly where I needed to be..."
- "{angel_number} on repeat. Took it as my sign. Went all in. Changed everything..."
- "Every {angel_number} brought new doors. Pattern was undeniable. Proof..."

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

