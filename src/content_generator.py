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
- "{angel_number} showed up right before my biggest win. Here's what it meant..."
- "Three times in one hour. {angel_number}. Then the opportunity appeared..."
- "{angel_number} on the receipt. The clock. My phone. I paid attention. Everything shifted..."
- "First time seeing {angel_number}? This is your activation moment..."
- "The universe sent {angel_number} five times today. Message clear. Taking action now..."
- "{angel_number} during my morning walk. That afternoon, the breakthrough happened..."
- "{angel_number} on every license plate today. Universe is communicating. Are you listening?"
- "Been seeing {angel_number} weekly. Finally decoded it. Game changer..."
- "The timer stopped at {angel_number}. The call came. The offer arrived. All connected..."
- "{angel_number} three days straight. Made the move. Best decision ever..."
- "{angel_number} flashed right before I met them. Now I know why..."
- "Started tracking every {angel_number} sighting. The pattern was undeniable..."
- "{angel_number} appeared during the biggest opportunity. Gave me confirmation. Went all in..."
- "That moment {angel_number} appeared and everything suddenly clicked..."
- "{angel_number} on the clock when they called. When the email arrived. When doors opened..."
- "Been manifesting this. Then {angel_number} appeared. Within 48 hours, it manifested..."
- "Everyone sees {angel_number}. Few decode it. Even fewer act. Be the one who does..."
- "Woke up at {angel_number}. Checked my phone. {angel_number} again. Universe is talking..."
- "{angel_number} appeared at the exact right time. Changed my entire trajectory..."
- "Seeing {angel_number} on repeat? That's not coincidence. That's confirmation. Move..."
- "Noticed {angel_number} everywhere this week. Took aligned action. Results are insane..."
- "{angel_number} during meditation. During my workout. On the elevator. Message received..."
- "The universe is sending you {angel_number} for a reason. Here's what it means..."
- "{angel_number} appeared and I finally trusted my gut. No looking back..."
- "Kept seeing {angel_number}. Researched the meaning. Took action. Life upgraded..."
- "{angel_number} showed up before every major milestone. Started paying attention..."
- "That feeling when {angel_number} appears and you just KNOW. Trust it..."
- "{angel_number} on receipts all week. Followed the signs. Abundance followed..."
- "Been aligned with {angel_number} energy. The opportunities are flowing now..."
- "You're seeing {angel_number} because you're ready. Time to level up..."

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
- "Stop making wishes at {angel_number}. Start taking action. Here's how..."
- "Everyone thinks {angel_number} means wait. Wrong. It means move now..."
- "You're seeing {angel_number} but nothing's happening? You're missing this..."
- "{angel_number} isn't about luck. It's about alignment. Here's the difference..."
- "Seeing {angel_number} everywhere? The universe is giving you a roadmap..."
- "Tested {angel_number} signals for months. Here's what actually works..."
- "{angel_number} on repeat? That's divine amplification. Time to act..."
- "The real meaning of {angel_number}? Not what TikTok told you. Listen..."
- "{angel_number} doesn't mean 'good luck coming.' It means you're already lucky. Move..."
- "{angel_number} is a green light, not a stop sign. Go now..."
- "That {angel_number} sighting? It's confirmation you're on the right path..."
- "{angel_number} showed up. Now do the work. Here's what that means..."
- "The truth about {angel_number}? You're ready. The universe knows it..."
- "Seeing {angel_number} multiple times? That's divine emphasis. Pay attention..."
- "{angel_number} means the window is open. And it's opening wider..."
- "{angel_number} is the universe's way of saying YES. Believe it..."
- "That {angel_number} pattern? It's specific guidance. Here's how to decode it..."
- "{angel_number} appears when you're aligned. Keep going. You're close..."
- "Seeing {angel_number} on clocks vs receipts? Different meanings. Know which..."
- "{angel_number} validates your readiness. You're more prepared than you think..."
- "The universe sent {angel_number}. That's your sign. This is your time..."
- "{angel_number} is your cue. The moment is now. Here's what to do..."
- "You saw {angel_number}. The universe is confirming your next move..."
- "Most people see {angel_number} and overthink. Smart people see it and act..."
- "{angel_number} doesn't whisper. It announces. You're being called up..."
- "That {angel_number} sequence? It's your personal code. Unlock it like this..."
- "Seeing {angel_number} means you've been chosen. Time to step up..."
- "{angel_number} is testing your trust. Pass the test. Take the leap..."
- "The {angel_number} signal? It's the universe opening doors. Walk through..."
- "You keep seeing {angel_number} because abundance is chasing YOU. Let it catch you..."

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
- "Someone I know saw {angel_number} every day for three months. Then manifested their dream life..."
- "She finally listened to {angel_number}. Made the leap. Everything shifted overnight..."
- "{angel_number} appeared right before her interview. She trusted it. Got the offer..."
- "After seeing {angel_number}, she made the move. Best decision of her life..."
- "Thought {angel_number} was random. Until the pattern became crystal clear..."
- "{angel_number} started appearing during morning walks. Followed the signs. Life upgraded..."
- "Saw {angel_number} three days straight. Took aligned action. Results are wild..."
- "Every time {angel_number} appeared, something amazing happened. Coincidence? Nope..."
- "Started trusting {angel_number} signs. Within 90 days, complete transformation..."
- "Tracked {angel_number} patterns for weeks. The message was undeniable..."
- "She saw {angel_number} before every major win. Pattern recognition unlocked everything..."
- "{angel_number} appeared when doors started opening. Followed the breadcrumbs. Found the path..."
- "He started trusting {angel_number}. His whole reality shifted in 60 days..."
- "Took action within minutes of seeing {angel_number}. Life is unrecognizable now..."
- "After aligning with {angel_number}, opportunities started flooding in..."
- "Documented every {angel_number} sighting for months. The clarity was mind-blowing..."
- "{angel_number} appeared before meeting her soulmate. She paid attention. Changed everything..."
- "Followed {angel_number} guidance despite the fear. Now living the dream..."
- "She saw {angel_number} and just knew. Trusted her intuition. Zero regrets..."
- "{angel_number} kept appearing at perfect timing. Learned to trust the flow..."
- "After the breakthrough, {angel_number} stopped appearing. Mission accomplished..."
- "Saw {angel_number} weekly for months. Each time, closer to the goal..."
- "Someone manifested their dream with {angel_number}. The results are insane..."
- "{angel_number} appeared when validation was needed most. Universe always delivers..."
- "Tracked {angel_number} for 90 days. The patterns revealed the roadmap..."
- "After {angel_number} showed up, she took the leap. Everything unlocked instantly..."
- "He saw {angel_number} and made the ask. She said yes. Divine timing..."
- "Followed the {angel_number} breadcrumbs. Led straight to the breakthrough..."
- "Started seeing {angel_number} on repeat. Took it as confirmation. Went all in..."
- "Every {angel_number} sighting brought a new opportunity. Pattern was obvious..."

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

