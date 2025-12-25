"""
Content Generator - Creates 3 types of angel number content
Uses Claude AI to generate deep, meaningful content
"""

import os
import json
from anthropic import Anthropic

class ContentGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
        
        # Angel numbers to rotate through
        self.angel_numbers = [
            "111", "222", "333", "444", "555", "666", "777", "888", "999",
            "1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888", "9999",
            "1212", "1234", "1010", "1122", "1313", "1414", "1717"
        ]
        
    def generate_storytelling(self, angel_number):
        """Deep storytelling approach - personal, emotional, controversial"""
        prompt = f"""Create compelling angel number content for {angel_number}.

STYLE: Deep storytelling with personal authority
TARGET: 17-20 seconds when spoken (slow, deliberate pace)
TONE: Controversial, specific, hooks attention

STRUCTURE:
- Hook (12-15 words): Bold, controversial statement that stops the scroll
- Meaning (20-25 words): What {angel_number} ACTUALLY means (not generic fluff)
- Action (30-35 words): 3 specific, numbered steps to take RIGHT NOW
- CTA (12-15 words): Strong call to follow + engagement prompt

EXAMPLES OF GOOD HOOKS:
- "Everyone gets {angel_number} wrong. Here's what it actually means..."
- "Seeing {angel_number} but nothing manifests? You're missing THIS step..."
- "I ignored {angel_number} for months. Biggest mistake of my life..."

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
            temperature=0.9,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        # Parse JSON from response
        try:
            return json.loads(content)
        except:
            # Extract JSON if Claude added extra text
            start = content.find('{')
            end = content.rfind('}') + 1
            return json.loads(content[start:end])
    
    def generate_practical(self, angel_number):
        """Practical tips - what to do when you see this number"""
        prompt = f"""Create practical angel number guidance for {angel_number}.

STYLE: Action-oriented, specific, immediately useful
TARGET: 17-20 seconds when spoken
TONE: Direct, helpful, no-nonsense

STRUCTURE:
- Hook (12-15 words): Specific scenario when people see this number
- Meaning (20-25 words): Why they're seeing it NOW and what it signals
- Action (30-35 words): 3 concrete actions to take in next 24 hours
- CTA (12-15 words): Follow for daily guidance + ask for their number

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
            temperature=0.9,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        try:
            return json.loads(content)
        except:
            start = content.find('{')
            end = content.rfind('}') + 1
            return json.loads(content[start:end])
    
    def generate_insights(self, angel_number):
        """Interesting facts and spiritual insights"""
        prompt = f"""Create fascinating spiritual insight about {angel_number}.

STYLE: Educational, mind-opening, makes people think
TARGET: 17-20 seconds when spoken
TONE: Mysterious, intriguing, authoritative

STRUCTURE:
- Hook (12-15 words): Surprising fact or little-known truth about the number
- Meaning (20-25 words): Deep spiritual/numerological significance
- Action (30-35 words): How to apply this knowledge for transformation
- CTA (12-15 words): Follow for hidden meanings + share your experience

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
            temperature=0.9,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        try:
            return json.loads(content)
        except:
            start = content.find('{')
            end = content.rfind('}') + 1
            return json.loads(content[start:end])

