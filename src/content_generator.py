"""
Content Generator - Creates 3 types of angel number content
Uses Claude AI to generate deep, meaningful content
"""

import os
from anthropic import Anthropic

class ContentGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
    def generate_storytelling(self, angel_number):
        """Deep storytelling approach - personal, emotional"""
        prompt = f"""Create compelling angel number content for {angel_number}.

Style: Deep storytelling with personal authority
Length: 17-20 seconds when spoken
Format: Hook → Meaning → Action → CTA

Requirements:
- Hook (3s): Controversial or specific statement that grabs attention
- Meaning (5s): What {angel_number} ACTUALLY means (not generic)
- Action (6-8s): 3 specific steps to take RIGHT NOW
- CTA (3s): Strong follow + engagement prompt

Return JSON:
{{
  "hook": "12-15 words max",
  "meaning": "20-25 words explaining the real meaning",
  "action": "30-35 words with 3 numbered steps",
  "cta": "12-15 words with strong call to action"
}}"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def generate_practical(self, angel_number):
        """Practical tips - what to do when you see this number"""
        # TODO: Implement practical tips generator
        pass
    
    def generate_insights(self, angel_number):
        """Interesting facts and spiritual insights"""
        # TODO: Implement insights generator
        pass

