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
- "Saw {angel_number} right before my biggest breakthrough. Here's what it meant..."
- "Woke up at {angel_number} the night before everything changed. Listen..."
- "{angel_number} appeared when I needed it most. Completely shifted my reality..."
- "I ignored {angel_number} for weeks. Huge mistake. Here's what happened..."
- "Three times in one hour. {angel_number}. Then the opportunity showed up..."
- "{angel_number} on the receipt. The clock. My phone. I finally listened..."
- "They said {angel_number} was coincidence. My bank account says otherwise..."
- "Stopped seeing {angel_number} after I took action. Here's why that matters..."
- "{angel_number} showed up at the perfect moment. Changed my entire path..."
- "First time seeing {angel_number}? This is your wake-up call..."
- "The universe sent {angel_number} five times today. Message received. Acting now..."
- "{angel_number} during my morning meditation. That afternoon, everything clicked..."
- "Dismissed {angel_number} as random. Then it appeared in my dream. Can't ignore anymore..."
- "My phone died at {angel_number}. Looked up. Saw the sign. Life shifted..."
- "{angel_number} on every license plate today. Universe is screaming. You listening?"
- "Doubted {angel_number} until it showed up in the most impossible place..."
- "Been seeing {angel_number} weekly. Finally decoded the message. Mind blown..."
- "{angel_number} appeared right when I was about to quit. Changed everything..."
- "The timer stopped at {angel_number}. The call came. The offer arrived. Connected..."
- "{angel_number} three days straight. Took the leap. Best decision I ever made..."
- "Seeing {angel_number} after heartbreak? That's not random. That's your restart..."
- "{angel_number} flashed right before I met them. Now I understand why..."
- "Kept a journal of every {angel_number} sighting. The pattern was undeniable..."
- "{angel_number} showed up when I needed confirmation most. Universe answered loud..."
- "My skeptic friend saw {angel_number} and ignored it. Then missed the opportunity..."
- "{angel_number} appeared during the scariest decision. Gave me the courage. No regrets..."
- "That moment {angel_number} popped up and everything suddenly made sense..."
- "{angel_number} on the clock when they texted. When the email came. When opportunity knocked..."
- "Been manifesting for months. Then {angel_number} appeared. Within 48 hours, it happened..."
- "Everyone sees {angel_number}. Few understand it. Even fewer act. Be the one who does..."

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
- "Stop making wishes at {angel_number}. That's not how it works. Listen..."
- "Everyone thinks {angel_number} means wait. They're wrong. Here's the truth..."
- "You're seeing {angel_number} but nothing happens? You're missing this ONE thing..."
- "{angel_number} isn't about luck. It's about timing. Here's the difference..."
- "Seeing {angel_number} everywhere? Most people waste it. Don't be most people..."
- "I tested {angel_number} 50 times. Only works when you do THIS first..."
- "{angel_number} on repeat? The universe isn't subtle. Time to move..."
- "You can ignore {angel_number}. Or you can understand what it's really saying..."
- "Most {angel_number} content is nonsense. Here's what actually matters..."
- "{angel_number} means action, not waiting. Here's what to do next..."
- "The real meaning of {angel_number}? Not what TikTok told you. Listen up..."
- "{angel_number} doesn't mean 'good luck coming.' It means YOU need to move now..."
- "Seeing {angel_number} but feeling stuck? You're interpreting it backwards..."
- "{angel_number} is a green light, not a stop sign. Act now or miss it..."
- "That {angel_number} sighting? It's not confirmation. It's a deadline. Hurry..."
- "You're doing {angel_number} wrong. No wonder nothing's manifesting. Fix this..."
- "{angel_number} showed up. Cool. Now do the work. That's the part nobody tells you..."
- "The truth about {angel_number}? It's testing you. Are you ready to move?"
- "{angel_number} doesn't care about your fears. It's pushing you anyway. Go..."
- "Seeing {angel_number} multiple times? That's not repetition. That's urgency. React..."
- "{angel_number} means the window is open. But it won't stay open forever..."
- "You keep seeing {angel_number} because you keep hesitating. Stop overthinking. Do it..."
- "{angel_number} is not a gentle nudge. It's the universe yelling. Listen..."
- "That {angel_number} pattern? It's specific instructions. Decode it. Act on it..."
- "{angel_number} appears when you're aligned. So why aren't you moving yet?"
- "Seeing {angel_number} on clocks vs receipts? Different messages. Know the difference..."
- "{angel_number} doesn't validate wishes. It validates readiness. Are you ready?"
- "The universe sent {angel_number}. That was the easy part. Your move now..."
- "{angel_number} is your cue. Not tomorrow. Not next week. Right now..."
- "You saw {angel_number}. Great. Now take the scary step you've been avoiding..."

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
- "Client saw {angel_number} every day for three months. Then everything clicked..."
- "She finally listened to {angel_number}. Made the leap. Life completely shifted..."
- "He ignored {angel_number} for 2 weeks. Then missed the opportunity. Don't..."
- "{angel_number} appeared right before her interview. She trusted it. Got the offer..."
- "After seeing {angel_number}, she quit her job. Scary? Yes. Worth it? Absolutely..."
- "My friend thought {angel_number} was random. Until the pattern became undeniable..."
- "{angel_number} started appearing during meditation. Followed the guidance. Mind blown..."
- "Saw {angel_number} three days straight. Took the risk. Best decision ever made..."
- "Every time she saw {angel_number}, something shifted. Finally understood the message..."
- "They doubted {angel_number} signals. Their transformation proved them wrong..."
- "Client kept a {angel_number} journal for 6 months. The insights were life-changing..."
- "She saw {angel_number} before every major win. Coincidence? Nope. Pattern..."
- "{angel_number} appeared when she was lost. Followed it. Found her purpose..."
- "He started trusting {angel_number} signs. Within 90 days, complete transformation..."
- "My student saw {angel_number} and took immediate action. Her life is unrecognizable now..."
- "{angel_number} showed up during her darkest moment. Became her guiding light..."
- "After ignoring {angel_number} for months, she finally listened. Everything changed overnight..."
- "He documented every {angel_number} sighting. The universe's message was crystal clear..."
- "{angel_number} appeared before she met her soulmate. She almost ignored it..."
- "Client followed {angel_number} guidance despite fear. Now living her dream life..."
- "She saw {angel_number} and knew. Trusted her gut. Made the move. No regrets..."
- "{angel_number} kept appearing at decision points. She learned to trust the signs..."
- "After her breakthrough, {angel_number} stopped appearing. The work was done..."
- "He saw {angel_number} weekly for a year. Each time, closer to his goal..."
- "My friend manifested with {angel_number}. The results speak for themselves..."
- "{angel_number} appeared when she needed validation most. Universe delivered perfectly..."
- "She tracked {angel_number} patterns for 3 months. Mind-blowing clarity emerged..."
- "After {angel_number} showed up, she gave herself permission. Everything unlocked..."
- "He saw {angel_number} and finally asked. She said yes. Timing was everything..."
- "Client followed {angel_number} breadcrumbs. Led her exactly where she needed to be..."

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

