"""
Life Path Content Generator - Creates engaging Life Path number content
Uses verified numerology data from life_path_database.py
Generates content in same format as angel number generator for compatibility
"""

import os
import json
import random
from anthropic import Anthropic
from life_path_database import get_life_path_data, get_compatibility


class LifePathGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
    
    def generate_content(self, life_path_number, angle, variation):
        """
        Generate Life Path content based on angle and variation
        
        Args:
            life_path_number: int (1-9, 11, 22, 33)
            angle: str ('identity', 'career', 'relationships', etc.)
            variation: str (specific variation within angle)
            
        Returns:
            dict: {'hook': str, 'meaning': str, 'action': str, 'cta': str}
        """
        # Get verified data for this Life Path
        lp_data = get_life_path_data(life_path_number)
        
        if not lp_data:
            raise ValueError(f"Invalid Life Path number: {life_path_number}")
        
        # Route to appropriate generator based on angle
        generators = {
            'identity': self.generate_identity,
            'career': self.generate_career,
            'relationships': self.generate_relationships,
            'compatibility': self.generate_compatibility,
            'shadow_work': self.generate_shadow_work,
            'strengths': self.generate_strengths
        }
        
        generator = generators.get(angle, self.generate_identity)
        return generator(life_path_number, lp_data, variation)
    
    def generate_identity(self, life_path_number, lp_data, variation):
        """Generate identity/who you are content"""
        
        # Build context from verified data
        positive_traits = ', '.join(lp_data['core_traits']['positive'][:5])
        negative_traits = ', '.join(lp_data['core_traits']['negative'][:3])
        
        prompt = f"""Create viral Life Path {life_path_number} identity content.

VERIFIED NUMEROLOGY DATA (DO NOT MAKE UP INFO):
- Name: {lp_data['name']}
- Archetype: {lp_data['archetype']}
- Positive traits: {positive_traits}
- Negative traits: {negative_traits}
- Life purpose: {lp_data['life_purpose']}
- Key characteristics: {', '.join(lp_data['key_characteristics'][:3])}

VARIATION: {variation}

CRITICAL RULES - POSITIVE CONTENT ONLY:
✅ POSITIVE: transformation, growth, self-awareness, empowerment, understanding
❌ AVOID: death, divorce, loss, tragedy, failure, extreme negativity
❌ NO RITUALS: No physical actions, timing requirements, made-up ceremonies
✅ TONE: Empowering, relatable, honest but uplifting

STYLE: Direct, relatable, identity-focused
TONE: "This is WHO you are" - validating, understanding, empowering

DURATION REQUIREMENTS (STRICT):
- Target: 15-20 seconds spoken content
- Maximum: 22 seconds
- Be CONCISE, PUNCHY, FAST-PACED

STRUCTURE (strict word counts):
- Hook (8-10 words): Identity recognition - "Are you Life Path {life_path_number}?"
- Meaning (20-25 words): Core identity traits from VERIFIED data above
- Action (25-30 words): Self-awareness insight, what to embrace/release
- CTA (8-10 words): Comment your number, engagement question

HOOK EXAMPLES - USE VARIETY - 30 OPTIONS:
- "Life Path {life_path_number}s: You've felt this your whole life..."
- "Are you a Life Path {life_path_number}? This explains everything..."
- "If you're Life Path {life_path_number}, you know this feeling..."
- "Life Path {life_path_number}? Finally, someone gets you. Listen..."
- "You're a {life_path_number}. That weird thing you do? Totally normal..."
- "Life Path {life_path_number}s are misunderstood. Here's the real you..."
- "Never met another Life Path {life_path_number}? You're rare. Here's why..."
- "Life Path {life_path_number}: That thing everyone judges you for? It's your gift..."
- "If you're a {life_path_number}, people don't get you. That's the point..."
- "Life Path {life_path_number}s see the world differently. Here's how..."
- "You're a {life_path_number}. This is why you feel out of place..."
- "Life Path {life_path_number}: Stop apologizing for who you are. Own it..."
- "If you're Life Path {life_path_number}, you've been called 'too much.' Wrong..."
- "Life Path {life_path_number}s operate on a different frequency. Here's proof..."
- "You're a {life_path_number}. Your intensity isn't a flaw. It's your power..."
- "Life Path {life_path_number}? That restless feeling makes perfect sense now..."
- "If you're a {life_path_number}, you've always felt different. You are..."
- "Life Path {life_path_number}s: Your way of thinking is your superpower..."
- "You're a {life_path_number}. Society's rules don't apply to you. Never did..."
- "Life Path {life_path_number}: Everyone else is playing checkers. You're playing chess..."
- "If you're a {life_path_number}, conformity feels like death. It should..."
- "Life Path {life_path_number}s can't be put in a box. Stop trying..."
- "You're a {life_path_number}. That 'overthinking' is actually your gift..."
- "Life Path {life_path_number}: You were built different. On purpose..."
- "If you're Life Path {life_path_number}, you question everything. That's the point..."
- "Life Path {life_path_number}s don't fit the mold. Never will. That's the goal..."
- "You're a {life_path_number}. Your sensitivity is strength, not weakness..."
- "Life Path {life_path_number}? People call you intense. They're right. Own it..."
- "If you're a {life_path_number}, you've felt alone your whole life. Here's why..."
- "Life Path {life_path_number}s are wired for more. This is what that means..."

MEANING (use ONLY verified traits above):
- Connect traits to relatable experiences
- Explain WHY they feel/act certain ways
- Validate their experience

ACTION (self-awareness, NOT rituals):
- What to embrace about themselves
- What pattern to be aware of
- How to use their traits positively

Return ONLY valid JSON:
{{
  "hook": "8-10 word identity hook",
  "meaning": "20-25 word meaning using VERIFIED traits",
  "action": "25-30 word self-awareness guidance",
  "cta": "8-10 word engagement CTA"
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.95,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_json(response.content[0].text)
    
    def generate_career(self, life_path_number, lp_data, variation):
        """Generate career/purpose content"""
        
        career_paths = ', '.join(lp_data['career_paths'][:4])
        
        prompt = f"""Create viral Life Path {life_path_number} career content.

VERIFIED NUMEROLOGY DATA:
- Name: {lp_data['name']}
- Life purpose: {lp_data['life_purpose']}
- Career paths: {career_paths}
- Key characteristics: {', '.join(lp_data['key_characteristics'][:3])}
- Challenges: {', '.join(lp_data['challenges'][:2])}

VARIATION: {variation}

CRITICAL RULES - POSITIVE & PRACTICAL:
✅ POSITIVE: career growth, purpose, alignment, success, opportunity
❌ AVOID: job loss, failure, poverty, unemployment fears
✅ TONE: Empowering career guidance, practical, hopeful

STYLE: Career coaching, practical purpose
TONE: "Here's your zone of genius"

DURATION: 15-20 seconds max (22 second absolute limit)

STRUCTURE:
- Hook (8-10 words): Career struggle or question
- Meaning (20-25 words): Why certain careers work/don't work (use verified data)
- Action (25-30 words): What careers align, what to pursue
- CTA (8-10 words): Engagement about their career/purpose

HOOK EXAMPLES - USE VARIETY - 30 OPTIONS:
- "Life Path {life_path_number}s hate their job? It's not you..."
- "If you're Life Path {life_path_number}, corporate life destroys you. Here's why..."
- "Life Path {life_path_number} career truth nobody tells you..."
- "You're a {life_path_number} stuck in the wrong career. Time to pivot..."
- "Life Path {life_path_number}s thrive here. Struggle everywhere else. Listen..."
- "Every job feels wrong? You're a Life Path {life_path_number}. Here's why..."
- "Life Path {life_path_number}: Stop forcing yourself into the wrong path..."
- "If you're a {life_path_number}, traditional careers suffocate you. Do this instead..."
- "Life Path {life_path_number}s need purpose, not paychecks. Here's your path..."
- "You're a {life_path_number}. Your career should look completely different..."
- "Life Path {life_path_number}? The 9-to-5 is killing you. Here's the way out..."
- "If you're a {life_path_number}, you'll never thrive in corporate. Accept it..."
- "Life Path {life_path_number}s excel when they do THIS. Fail at everything else..."
- "You're a {life_path_number}. Your boss doesn't get you. They never will..."
- "Life Path {life_path_number}: That job that drains everyone else energizes you..."
- "If you're Life Path {life_path_number}, you need autonomy. Period. No exceptions..."
- "Life Path {life_path_number}s were made for entrepreneurship. Here's the proof..."
- "You're a {life_path_number}. Stop chasing titles. Build something meaningful instead..."
- "Life Path {life_path_number}? Work-life balance is a myth for you. Here's what you need..."
- "If you're a {life_path_number}, your career path doesn't exist yet. Create it..."
- "Life Path {life_path_number}s burn out fast in the wrong environment. Know the signs..."
- "You're a {life_path_number}. That passion project? That's your real career..."
- "Life Path {life_path_number}: Stop waiting for permission. Start building now..."
- "If you're Life Path {life_path_number}, you'll never be satisfied with average. Good..."
- "Life Path {life_path_number}s need this type of work. Everything else is settling..."
- "You're a {life_path_number}. That 'unrealistic' dream? It's your actual calling..."
- "Life Path {life_path_number}? You're unemployable. That's your greatest asset..."
- "If you're a {life_path_number}, working for someone else feels wrong. It is..."
- "Life Path {life_path_number}s need impact, not income. Here's how to get both..."
- "You're a {life_path_number}. The career advice you're getting is wrong. Try this..."

MEANING (use ONLY verified career data):
- Why they struggle in certain environments
- What they actually need in work
- Their natural zone of genius

ACTION (practical career guidance):
- What careers/paths actually fit
- What to look for in work
- How to use their strengths

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
    
    def generate_relationships(self, life_path_number, lp_data, variation):
        """Generate relationship/love content"""
        
        prompt = f"""Create viral Life Path {life_path_number} relationship content.

VERIFIED NUMEROLOGY DATA:
- Name: {lp_data['name']}
- Core traits: {', '.join(lp_data['core_traits']['positive'][:3])}
- Negative traits: {', '.join(lp_data['core_traits']['negative'][:2])}
- Key characteristics: {', '.join(lp_data['key_characteristics'][:3])}
- Challenges: {', '.join(lp_data['challenges'][:2])}

VARIATION: {variation}

CRITICAL RULES - POSITIVE RELATIONSHIP CONTENT:
✅ POSITIVE: growth, understanding, connection, healthy love
❌ AVOID: divorce, breakups, toxic relationships, cheating, abandonment
✅ TONE: Understanding, compassionate, growth-oriented

STYLE: Relationship insight, understanding
TONE: "This is how you love and what you need"

DURATION: 15-20 seconds max

STRUCTURE:
- Hook (8-10 words): Relationship pattern or question
- Meaning (20-25 words): How they show up in relationships (verified traits)
- Action (25-30 words): What they need, how partners can understand them
- CTA (8-10 words): Tag someone or share experience

HOOK EXAMPLES - USE VARIETY - 30 OPTIONS:
- "Dating a Life Path {life_path_number}? What you need to know..."
- "Life Path {life_path_number} in love: Why you push people away..."
- "If you're Life Path {life_path_number}, relationships feel like this..."
- "You're a {life_path_number}. That's why relationships are so intense..."
- "Life Path {life_path_number}s love differently. Here's what that means..."
- "If you're dating a {life_path_number}, understand this ONE thing..."
- "Life Path {life_path_number}: Stop settling. You need someone who gets THIS..."
- "You're a {life_path_number}. Your relationship pattern makes perfect sense now..."
- "Life Path {life_path_number}s attract the wrong people. Here's why..."
- "If you're a {life_path_number}, love should feel like this instead..."
- "Life Path {life_path_number}s need space but crave connection. The paradox explained..."
- "You're a {life_path_number}. Partners think you're cold. You're not. Listen..."
- "If you're dating a Life Path {life_path_number}, they need THIS daily..."
- "Life Path {life_path_number}: That intimacy fear? It's protective. Here's how to shift..."
- "You're a {life_path_number}. Your love language confuses everyone. Here's why..."
- "Life Path {life_path_number}s test partners constantly. The real reason is this..."
- "If you're a {life_path_number}, commitment feels scary. It's not what you think..."
- "Life Path {life_path_number}: You attract emotionally unavailable people. Break the pattern..."
- "You're dating a {life_path_number}? Their silence speaks volumes. Decode it..."
- "Life Path {life_path_number}s need deep connection or nothing. Casual doesn't work..."
- "If you're a {life_path_number}, you sabotage good relationships. Here's how to stop..."
- "Life Path {life_path_number}: Your partner feels shut out. Open this way instead..."
- "You're a {life_path_number}. That need for independence isn't selfish. It's essential..."
- "Life Path {life_path_number}s feel everything intensely. Partners need to understand this..."
- "If you're dating a {life_path_number}, they're testing if you're safe. Pass this way..."
- "Life Path {life_path_number}: You give mixed signals in love. Clarify like this..."
- "You're a {life_path_number}. Small talk kills attraction for you. Go deeper..."
- "Life Path {life_path_number}s fall hard but pull away fast. The pattern explained..."
- "If you're a {life_path_number}, you need a partner who gets your depth. Don't settle..."
- "Life Path {life_path_number}: That emotional wall? It's protecting something important. Address it..."

MEANING (use verified traits):
- How their core traits show up in love
- What partners misunderstand about them
- Their actual relationship needs

ACTION (relationship guidance):
- What they need from partners
- What to communicate
- How to create healthy dynamics

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
    
    def generate_compatibility(self, life_path_number, lp_data, variation):
        """Generate compatibility content"""
        
        compat_data = get_compatibility(life_path_number)
        best_matches = ', '.join([str(n) for n in compat_data['best'][:3]])
        challenging = ', '.join([str(n) for n in compat_data['challenging'][:2]])
        
        prompt = f"""Create viral Life Path {life_path_number} compatibility content.

VERIFIED COMPATIBILITY DATA:
- Best matches: {best_matches}
- Challenging matches: {challenging}
- Core traits: {', '.join(lp_data['core_traits']['positive'][:3])}

VARIATION: {variation}

CRITICAL RULES:
✅ POSITIVE: compatibility, connection, understanding, growth together
❌ AVOID: "doomed relationships", incompatibility as absolute
✅ TONE: Insightful, practical, hopeful

STYLE: Compatibility insight
TONE: "Here's who you vibe with and why"

DURATION: 15-20 seconds max

STRUCTURE:
- Hook (8-10 words): Compatibility question or pattern
- Meaning (20-25 words): Why certain numbers work/challenge (use verified data)
- Action (25-30 words): What to look for, how to make it work
- CTA (8-10 words): Comment your combination

HOOK EXAMPLES - USE VARIETY - 30 OPTIONS:
- "Life Path {life_path_number} + {best_matches[0]}? Here's what happens..."
- "If you're Life Path {life_path_number}, you vibe best with these numbers..."
- "Life Path {life_path_number} compatibility truth nobody talks about..."
- "You're a {life_path_number}. These numbers get you. Everyone else? Nope..."
- "Life Path {life_path_number} + wrong number = chaos. Here's who works..."
- "If you're a {life_path_number}, avoid THESE numbers. Trust me..."
- "Life Path {life_path_number}s click instantly with these people. Here's why..."
- "You're a {life_path_number}. Your best match might surprise you..."
- "Life Path {life_path_number}: Stop dating the wrong numbers. Try this instead..."
- "If you're a {life_path_number}, this combination is pure magic..."
- "Life Path {life_path_number}s need partners who match this energy. Check yours..."
- "You're a {life_path_number} dating a {challenging[0]}? It's challenging but fixable..."
- "Life Path {life_path_number}: The numbers you're attracted to vs who actually works..."
- "If you're a {life_path_number}, this Life Path combo creates fireworks (good kind)..."
- "Life Path {life_path_number} + same number? Power couple or disaster? Truth..."
- "You're dating a {life_path_number}? These Life Paths harmonize. These clash..."
- "Life Path {life_path_number}s struggle with certain numbers. Not your fault. Chemistry..."
- "If you're a {life_path_number}, your soulmate is likely one of THESE numbers..."
- "Life Path {life_path_number}: That number you keep dating? Wrong match. Try these..."
- "You're a {life_path_number}. This combination feels easy. That one feels forced..."
- "Life Path {life_path_number}s and {best_matches[0]}s together? Unstoppable energy. Here's why..."
- "If you're a {life_path_number}, dating {challenging[0]}s teaches you THIS lesson..."
- "Life Path {life_path_number}: Check your partner's number. If it's this, it explains everything..."
- "You're a {life_path_number}. Your parents' numbers explain your childhood. Decode it..."
- "Life Path {life_path_number}s naturally attract these numbers. Understand the pull..."
- "If you're dating a {life_path_number}, your number compatibility determines THIS..."
- "Life Path {life_path_number}: Friends vs lovers compatibility is different. Know which..."
- "You're a {life_path_number}. Business partners need different numbers than romantic ones..."
- "Life Path {life_path_number}s repel certain numbers for protection. It's energetic..."
- "If you're a {life_path_number}, the number you resist might be your growth partner..."

MEANING (use verified compatibility):
- Why certain numbers complement them
- What makes relationships work/challenging
- Energy dynamics between numbers

ACTION (compatibility guidance):
- What to look for in partners
- How different numbers interact
- Making any combination work

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
    
    def generate_shadow_work(self, life_path_number, lp_data, variation):
        """Generate shadow work/toxic traits content"""
        
        negative_traits = ', '.join(lp_data['core_traits']['negative'][:3])
        challenges = ', '.join(lp_data['challenges'][:3])
        
        prompt = f"""Create viral Life Path {life_path_number} shadow work content.

VERIFIED NUMEROLOGY DATA:
- Negative traits: {negative_traits}
- Challenges: {challenges}
- What to work on: {lp_data.get('shadow_work', 'Balance and growth')}

VARIATION: {variation}

CRITICAL RULES - HONEST BUT CONSTRUCTIVE:
✅ HONEST: Call out real patterns, be direct
✅ CONSTRUCTIVE: Always provide path to growth
❌ AVOID: Shame, judgment, hopelessness
✅ TONE: Tough love, empowering, growth-focused

STYLE: Shadow work, tough love
TONE: "Here's your toxic trait and how to fix it"

DURATION: 15-20 seconds max

STRUCTURE:
- Hook (8-10 words): Call out the behavior/pattern
- Meaning (20-25 words): Why they do it (root cause from verified data)
- Action (25-30 words): How to fix it, growth path
- CTA (8-10 words): Self-awareness check, accountability

HOOK EXAMPLES - USE VARIETY - 30 OPTIONS:
- "Life Path {life_path_number} toxic trait you need to fix..."
- "If you're Life Path {life_path_number}, you do this and it's destroying you..."
- "Life Path {life_path_number}s: Your biggest weakness is also your strength..."
- "You're a {life_path_number}. This pattern is holding you back. Real talk..."
- "Life Path {life_path_number}s self-sabotage like this. Stop it. Now..."
- "If you're a {life_path_number}, you keep doing THIS. Time to break the cycle..."
- "Life Path {life_path_number}: Your shadow side is showing. Address it..."
- "You're a {life_path_number}. That thing you're avoiding? It's the work..."
- "Life Path {life_path_number}s struggle with this. But you can shift it..."
- "If you're a {life_path_number}, this toxic pattern needs to end today..."
- "Life Path {life_path_number}: The behavior everyone complains about? They're right. Fix it..."
- "You're a {life_path_number}. This is why people leave. Honest feedback..."
- "Life Path {life_path_number}s push people away unconsciously. The pattern revealed..."
- "If you're a {life_path_number}, your ego is your enemy. Time to check it..."
- "Life Path {life_path_number}: That defense mechanism? It's blocking your growth..."
- "You're a {life_path_number}. You're being selfish and don't see it. Wake up..."
- "Life Path {life_path_number}s avoid accountability. Own your part. Grow..."
- "If you're a {life_path_number}, you manipulate without realizing. Stop this way..."
- "Life Path {life_path_number}: Your victim mentality is keeping you stuck. Shift..."
- "You're a {life_path_number}. That pride is costing you relationships. Soften..."
- "Life Path {life_path_number}s intellectualize emotions to avoid feeling. Process instead..."
- "If you're a {life_path_number}, you control everything out of fear. Release..."
- "Life Path {life_path_number}: Your perfectionism paralyzes you. Done beats perfect..."
- "You're a {life_path_number}. Stop escaping. Face the discomfort. It's growth..."
- "Life Path {life_path_number}s isolate when hurt. Reach out instead. Heal..."
- "If you're a {life_path_number}, your passive aggression damages trust. Be direct..."
- "Life Path {life_path_number}: You're playing small to stay safe. Risk bigger..."
- "You're a {life_path_number}. That stubbornness? It's insecurity. Be flexible..."
- "Life Path {life_path_number}s judge harshly to feel superior. Practice compassion..."
- "If you're a {life_path_number}, you're repeating the pattern. Break it now..."

MEANING (use verified negative traits):
- What pattern they fall into
- Root cause (from their core traits)
- How it manifests

ACTION (growth path):
- Specific behavior to change
- New pattern to embrace
- How to use shadow as strength

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
    
    def generate_strengths(self, life_path_number, lp_data, variation):
        """Generate strengths/superpowers content"""
        
        positive_traits = ', '.join(lp_data['core_traits']['positive'][:4])
        famous = ', '.join(lp_data['famous_examples'][:2])
        
        prompt = f"""Create viral Life Path {life_path_number} strengths content.

VERIFIED NUMEROLOGY DATA:
- Positive traits: {positive_traits}
- Life purpose: {lp_data['life_purpose']}
- Famous examples: {famous}

VARIATION: {variation}

CRITICAL RULES - EMPOWERING:
✅ CELEBRATE: Highlight unique gifts, natural abilities
✅ INSPIRE: Show how to use strengths
✅ TONE: Uplifting, empowering, confidence-building

STYLE: Strength celebration
TONE: "This is your superpower"

DURATION: 15-20 seconds max

STRUCTURE:
- Hook (8-10 words): Identify the superpower
- Meaning (20-25 words): What makes this trait powerful (verified data)
- Action (25-30 words): How to use it, real-world application
- CTA (8-10 words): Claim your power, share experience

HOOK EXAMPLES - USE VARIETY - 30 OPTIONS:
- "Life Path {life_path_number} superpower nobody talks about..."
- "If you're Life Path {life_path_number}, you have a gift most people don't..."
- "Life Path {life_path_number}s are underestimated. Here's your hidden power..."
- "You're a {life_path_number}. Your secret weapon is THIS. Use it..."
- "Life Path {life_path_number}s can do something incredible. Most don't know it..."
- "If you're a {life_path_number}, this is your unfair advantage. Own it..."
- "Life Path {life_path_number}: Stop hiding this gift. The world needs it..."
- "You're a {life_path_number}. This strength changes everything when you claim it..."
- "Life Path {life_path_number}s have a rare ability. Here's how to master it..."
- "If you're a {life_path_number}, this power is yours. Time to activate it..."
- "Life Path {life_path_number}: The talent you downplay? That's your goldmine..."
- "You're a {life_path_number}. Most people can't do what comes naturally to you..."
- "Life Path {life_path_number}s possess this unique strength. Leverage it fully..."
- "If you're a {life_path_number}, you see what others miss. That's power..."
- "Life Path {life_path_number}: Your natural ability gives you this edge. Claim it..."
- "You're a {life_path_number}. This gift is why you're meant for greatness..."
- "Life Path {life_path_number}s excel at THIS. It's your zone of genius..."
- "If you're a {life_path_number}, your superpower is disguised as this trait..."
- "Life Path {life_path_number}: What feels easy to you? Others struggle with that..."
- "You're a {life_path_number}. That thing you do effortlessly? Monetize it..."
- "Life Path {life_path_number}s have an innate talent for THIS. Master it..."
- "If you're a {life_path_number}, your competitive advantage is already built-in..."
- "Life Path {life_path_number}: Stop overlooking your greatest asset. It's THIS..."
- "You're a {life_path_number}. Your unique perspective is your currency. Sell it..."
- "Life Path {life_path_number}s naturally attract opportunities through this strength..."
- "If you're a {life_path_number}, your intuition is sharper than most. Trust it..."
- "Life Path {life_path_number}: The skill you take for granted? That's rare..."
- "You're a {life_path_number}. This ability is why people are drawn to you..."
- "Life Path {life_path_number}s change the game when they activate THIS power..."
- "If you're a {life_path_number}, your greatest strength is the one you're ignoring..."

MEANING (use verified positive traits):
- What natural ability they have
- Why it's powerful/rare
- How famous {life_path_number}s used it

ACTION (empowerment):
- How to leverage this strength
- Real-world application
- Competitive advantage

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


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Test the generator
    from dotenv import load_dotenv
    load_dotenv()
    
    generator = LifePathGenerator()
    
    print("=" * 70)
    print("TESTING LIFE PATH GENERATOR")
    print("=" * 70)
    
    # Test Life Path 7 - Identity
    print("\nTest 1: Life Path 7 - Identity")
    print("-" * 70)
    
    content = generator.generate_content(
        life_path_number=7,
        angle='identity',
        variation='core_traits'
    )
    
    print(f"Hook: {content['hook']}")
    print(f"Meaning: {content['meaning']}")
    print(f"Action: {content['action']}")
    print(f"CTA: {content['cta']}")
    
    # Test Life Path 5 - Career
    print("\n\nTest 2: Life Path 5 - Career")
    print("-" * 70)
    
    content2 = generator.generate_content(
        life_path_number=5,
        angle='career',
        variation='ideal_careers'
    )
    
    print(f"Hook: {content2['hook']}")
    print(f"Meaning: {content2['meaning']}")
    print(f"Action: {content2['action']}")
    print(f"CTA: {content2['cta']}")
    
    print("\n" + "=" * 70)
    print("✅ GENERATOR WORKING")
    print("=" * 70)
