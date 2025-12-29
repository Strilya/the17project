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

HOOK EXAMPLES:
- "Life Path {life_path_number}s: You've felt this your whole life..."
- "Are you a Life Path {life_path_number}? This explains everything..."
- "If you're Life Path {life_path_number}, you know this feeling..."

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

HOOK EXAMPLES:
- "Life Path {life_path_number}s hate their job? It's not you..."
- "If you're Life Path {life_path_number}, corporate life destroys you. Here's why..."
- "Life Path {life_path_number} career truth nobody tells you..."

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

HOOK EXAMPLES:
- "Dating a Life Path {life_path_number}? What you need to know..."
- "Life Path {life_path_number} in love: Why you push people away..."
- "If you're Life Path {life_path_number}, relationships feel like this..."

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

HOOK EXAMPLES:
- "Life Path {life_path_number} + {best_matches[0]}? Here's what happens..."
- "If you're Life Path {life_path_number}, you vibe best with these numbers..."
- "Life Path {life_path_number} compatibility truth nobody talks about..."

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

HOOK EXAMPLES:
- "Life Path {life_path_number} toxic trait you need to fix..."
- "If you're Life Path {life_path_number}, you do this and it's destroying you..."
- "Life Path {life_path_number}s: Your biggest weakness is also your strength..."

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

HOOK EXAMPLES:
- "Life Path {life_path_number} superpower nobody talks about..."
- "If you're Life Path {life_path_number}, you have a gift most people don't..."
- "Life Path {life_path_number}s are underestimated. Here's your hidden power..."

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
