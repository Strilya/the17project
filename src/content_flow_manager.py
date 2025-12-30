"""
Content Flow Manager - Handles scheduling and content distribution
Mon/Wed/Fri: Life Path Numbers (3 reels/day)
Tue/Thu/Sat: Angel Numbers (3 reels/day)
Sunday: Wildcard (mix or special content)

This manages WHAT gets generated on WHICH day to ensure variety and coverage
"""

import random
from datetime import datetime
from life_path_database import get_all_life_paths, get_life_path_data
from angel_numbers_db import get_all_angel_numbers


# ============================================================================
# CONTENT ANGLES - Each Life Path has multiple angles to explore
# ============================================================================

LIFE_PATH_CONTENT_ANGLES = {
    'identity': {
        'name': 'Who You Are',
        'focus': 'Core identity, traits, personality',
        'variations': [
            'core_traits',
            'hidden_strengths',
            'what_makes_you_unique'
        ]
    },
    'career': {
        'name': 'Career & Purpose',
        'focus': 'Work, career paths, life purpose',
        'variations': [
            'ideal_careers',
            'why_corporate_fails',
            'hidden_talents'
        ]
    },
    'relationships': {
        'name': 'Relationships & Love',
        'focus': 'How you love, relationship patterns',
        'variations': [
            'love_style',
            'relationship_challenges',
            'what_partners_need_to_know'
        ]
    },
    'compatibility': {
        'name': 'Compatibility',
        'focus': 'Which numbers you vibe with',
        'variations': [
            'best_matches',
            'challenging_matches',
            'soulmate_numbers'
        ]
    },
    'shadow_work': {
        'name': 'Shadow Work',
        'focus': 'Toxic traits, challenges, growth areas',
        'variations': [
            'toxic_trait',
            'biggest_weakness',
            'what_holds_you_back'
        ]
    },
    'strengths': {
        'name': 'Strengths & Gifts',
        'focus': 'Superpowers, natural abilities',
        'variations': [
            'superpower',
            'natural_gift',
            'competitive_advantage'
        ]
    }
}


# ============================================================================
# CAPTION TEMPLATES - ACTUALLY GOOD, NOT BULLSHIT
# ============================================================================

CAPTION_TEMPLATES = {
    'identity': [
        """Life Path {number}: {name}

{hook}

Most people don't get you. They see {negative_trait} when really you're just {positive_reframe}.

Your gift: {strength}
Your challenge: {challenge}

Drop your number 👇
Calculate: [link in bio]

{hashtags}""",

        """Are you Life Path {number}?

Then you know this feeling: {relatable_struggle}

Here's what nobody tells you: {truth}

You're not broken. You're {archetype}.

Comment your number below 👇

{hashtags}""",

        """Life Path {number} truth bomb:

{controversial_statement}

That's why you {behavior_pattern}.

Your real power? {hidden_strength}

Tag a {number} who needs this 👇

{hashtags}"""
    ],
    
    'career': [
        """Life Path {number} career advice:

Stop forcing yourself into {bad_career_fit}. 

You thrive in: {ideal_career}

Why? Because you need {core_need}.

Your zone of genius: {superpower}

Drop your number 👇

{hashtags}""",

        """If you're Life Path {number} and hate your job:

It's not you. It's the job.

You weren't built for {limitation}.
You were built for {purpose}.

Best careers: {career_list}

Calculate yours [link in bio]

{hashtags}""",

        """Life Path {number}s make terrible {bad_role} but incredible {good_role}.

Why? 

{explanation}

Stop trying to be what you're not.

Tag a {number} who needs to hear this 👇

{hashtags}"""
    ],
    
    'relationships': [
        """Dating Life Path {number}?

What you need to know:

They {relationship_pattern}.

It's not personal. It's their {core_trait}.

Give them {what_they_need} and they'll {positive_outcome}.

Are you a {number}? Drop it below 👇

{hashtags}""",

        """Life Path {number} in love:

You {love_behavior}.

Partners think: {misunderstanding}
Reality: {truth}

What you actually need: {real_need}

Comment if this hits home 👇

{hashtags}""",

        """Why Life Path {number}s struggle in relationships:

{struggle}

You're not broken. You're {reframe}.

The right partner will {ideal_response}.

Tag your {number} 👇

{hashtags}"""
    ],
    
    'compatibility': [
        """Life Path {number} + {compatible_number} = {result}

Why it works:
{explanation}

Why it's challenging:
{challenge}

But when you both {solution}, it's magic.

Drop your combo below 👇👇

{hashtags}""",

        """Life Path {number}s vibe best with:

{best_match_1}: {why_1}
{best_match_2}: {why_2}
{best_match_3}: {why_3}

Worst match? {worst_match} ({why_bad})

What's your experience? Comment 👇

{hashtags}""",

        """If you're Life Path {number} seeing {compatible_number} everywhere:

The universe is confirming: {message}

This number amplifies your {trait}.

What to do: {action}

Calculate yours [link in bio]

{hashtags}"""
    ],
    
    'shadow_work': [
        """Life Path {number} toxic trait:

{toxic_behavior}

Why you do it: {root_cause}

How to fix it: {solution}

Call yourself out below 👇

{hashtags}""",

        """Life Path {number}s: 

Your biggest strength ({strength}) is also your biggest weakness.

When unchecked, you {negative_manifestation}.

The fix: {solution}

Who else struggles with this? 👇

{hashtags}""",

        """Harsh truth for Life Path {number}:

{hard_truth}

It's keeping you from {goal}.

Stop {bad_habit}.
Start {good_habit}.

Tag a {number} who needs this wake-up call 👇

{hashtags}"""
    ],
    
    'strengths': [
        """Life Path {number} superpower:

{superpower}

While others struggle with {common_struggle}, you {natural_ability}.

How to use it: {application}

Claim your power below 👇

{hashtags}""",

        """Life Path {number}s have a gift most people don't:

{gift}

You don't even realize how rare this is.

Famous {number}s who used it: {celebrity_example}

What's yours? Drop your number 👇

{hashtags}""",

        """Why Life Path {number}s are underestimated:

People see: {surface_perception}
Reality: {hidden_power}

Your competitive advantage: {strength}

Once you own this, you're unstoppable.

{hashtags}"""
    ]
}


# ============================================================================
# HASHTAG SETS - Relevant to content type
# ============================================================================

BASE_HASHTAGS = [
    'numerology',
    'lifepath',
    'lifepathumber',
    'spirituality',
    'selfdiscovery',
    'manifestation',
    'lawofattraction',
    'spiritualawakening'
]

LIFE_PATH_HASHTAGS = BASE_HASHTAGS + [
    'numerologyreading',
    'birthdatenumerology',
    'knowyourself',
    'personalgrowth',
    'selfawareness',
    'astrology',
    'zodiac',
    'birthchart'
]

ANGEL_NUMBER_HASHTAGS = BASE_HASHTAGS + [
    'angelnumbers',
    'angelmessages',
    'divineguidance',
    'synchronicity',
    'signs',
    'universe',
    'spiritualguidance',
    'divinity'
]


# ============================================================================
# CONTENT SCHEDULING LOGIC
# ============================================================================

def get_day_type(date=None):
    """
    Determine what type of content to generate based on day of week
    
    Monday/Wednesday/Friday: Life Path Numbers
    Tuesday/Thursday/Saturday: Angel Numbers
    Sunday: Wildcard (mix)
    
    Args:
        date: datetime object (default: today)
        
    Returns:
        str: 'life_path', 'angel_number', or 'wildcard'
    """
    if date is None:
        date = datetime.now()
    
    day_name = date.strftime('%A')
    
    if day_name in ['Monday', 'Wednesday', 'Friday']:
        return 'life_path'
    elif day_name in ['Tuesday', 'Thursday', 'Saturday']:
        return 'angel_number'
    else:  # Sunday
        return 'wildcard'


def get_content_plan_for_day(day_type=None, reel_count=3):
    """
    Get the content plan for a given day type
    
    Args:
        day_type: str ('life_path', 'angel_number', 'wildcard')
        reel_count: int (how many reels to generate, default 3)
        
    Returns:
        list: Content specifications for each reel
    """
    if day_type is None:
        day_type = get_day_type()
    
    if day_type == 'life_path':
        return get_life_path_plan(reel_count)
    elif day_type == 'angel_number':
        return get_angel_number_plan(reel_count)
    else:  # wildcard
        return get_wildcard_plan(reel_count)


def get_life_path_plan(count=3):
    """
    Generate plan for Life Path content (Mon/Wed/Fri)
    
    Strategy: Rotate through different life paths with different angles
    Example: LP7-Identity, LP3-Career, LP5-Relationships
    
    Args:
        count: int (number of reels)
        
    Returns:
        list of dicts with content specs
    """
    all_life_paths = get_all_life_paths()
    all_angles = list(LIFE_PATH_CONTENT_ANGLES.keys())
    
    plan = []
    
    # Use different life paths and angles for variety
    used_life_paths = []
    used_angles = []
    
    for i in range(count):
        # Pick a life path we haven't used yet today
        available_lps = [lp for lp in all_life_paths if lp not in used_life_paths]
        if not available_lps:
            available_lps = all_life_paths  # Reset if we've used all
            used_life_paths = []
        
        life_path = random.choice(available_lps)
        used_life_paths.append(life_path)
        
        # Pick an angle we haven't used yet today
        available_angles = [a for a in all_angles if a not in used_angles]
        if not available_angles:
            available_angles = all_angles  # Reset if we've used all
            used_angles = []
        
        angle = random.choice(available_angles)
        used_angles.append(angle)
        
        # Pick variation within that angle
        variation = random.choice(LIFE_PATH_CONTENT_ANGLES[angle]['variations'])
        
        plan.append({
            'type': 'life_path',
            'life_path_number': life_path,
            'angle': angle,
            'variation': variation,
            'reel_number': i + 1
        })
    
    return plan


def get_angel_number_plan(count=3):
    """
    Generate plan for Angel Number content (Tue/Thu/Sat)
    
    Strategy: Use existing angel number system (unchanged)
    
    Args:
        count: int (number of reels)
        
    Returns:
        list of dicts with content specs
    """
    all_numbers = get_all_angel_numbers()
    styles = ['storytelling', 'practical', 'insights']
    
    plan = []
    
    for i in range(count):
        # Pick random angel number and style
        angel_number = random.choice(all_numbers)
        style = random.choice(styles)
        
        plan.append({
            'type': 'angel_number',
            'angel_number': angel_number,
            'style': style,
            'reel_number': i + 1
        })
    
    return plan


def get_wildcard_plan(count=3):
    """
    Generate plan for Sunday wildcard content
    
    Strategy: Mix of life path, angel numbers, or special content
    
    Args:
        count: int (number of reels)
        
    Returns:
        list of dicts with content specs
    """
    plan = []
    
    # Sunday: Mix it up - 2 life path, 1 angel number (or vice versa)
    content_types = ['life_path', 'life_path', 'angel_number']
    random.shuffle(content_types)
    
    for i, content_type in enumerate(content_types[:count]):
        if content_type == 'life_path':
            lp_plan = get_life_path_plan(1)[0]
            lp_plan['reel_number'] = i + 1
            plan.append(lp_plan)
        else:
            an_plan = get_angel_number_plan(1)[0]
            an_plan['reel_number'] = i + 1
            plan.append(an_plan)
    
    return plan


# ============================================================================
# CAPTION GENERATION
# ============================================================================

def generate_caption(content_spec, content_data):
    """
    Generate Instagram caption based on content type and data
    
    Args:
        content_spec: dict from get_content_plan_for_day()
        content_data: dict with generated content (hook, meaning, action, cta)
        
    Returns:
        str: Ready-to-post Instagram caption
    """
    if content_spec['type'] == 'life_path':
        return generate_life_path_caption(content_spec, content_data)
    else:
        return generate_angel_number_caption(content_spec, content_data)


def generate_life_path_caption(content_spec, content_data):
    """
    Generate caption for Life Path content
    
    Args:
        content_spec: dict with life_path_number, angle, variation
        content_data: dict with hook, meaning, action, cta
        
    Returns:
        str: Instagram caption
    """
    life_path_num = content_spec['life_path_number']
    angle = content_spec['angle']
    
    # Get Life Path data
    lp_data = get_life_path_data(life_path_num)
    
    # Pick template for this angle
    templates = CAPTION_TEMPLATES.get(angle, CAPTION_TEMPLATES['identity'])
    template = random.choice(templates)
    
    # Build hashtags
    hashtags = ' '.join([f'#{tag}' for tag in LIFE_PATH_HASHTAGS[:15]])
    
    # Simple caption that doesn't rely on complex template variables
    # We'll use the actual generated content
    caption = f"""Life Path {life_path_num}: {lp_data['name']}

{content_data.get('hook', '')}

{content_data.get('meaning', '')}

{content_data.get('action', '')}

Calculate yours (link in bio) 👇

{hashtags}

---
New here? Watch my intro 📍 (pinned to profile)"""

    return caption.strip()


def generate_angel_number_caption(content_spec, content_data):
    """
    Generate caption for Angel Number content
    
    Args:
        content_spec: dict with angel_number, style
        content_data: dict with hook, meaning, action, cta
        
    Returns:
        str: Instagram caption
    """
    angel_number = content_spec['angel_number']
    
    # Build hashtags
    specific_hashtags = [
        f'angelnumber{angel_number}',
        f'{angel_number}',
        'angelnumbers',
        'synchronicity',
        'signs'
    ]
    
    all_hashtags = specific_hashtags + ANGEL_NUMBER_HASHTAGS[:10]
    hashtags = ' '.join([f'#{tag}' for tag in all_hashtags[:15]])
    
    # Build full transcript caption
    caption_parts = [
        f"Seeing {angel_number}?",
        content_data.get('hook', ''),
        content_data.get('meaning', ''),
        content_data.get('action', ''),
        content_data.get('cta', '')
    ]

    # Join parts with double line breaks, then add hashtags
    full_transcript = '\n\n'.join([part for part in caption_parts if part])
    caption = f"{full_transcript}\n\n{hashtags}"

    return caption.strip()


# ============================================================================
# CONTENT TRACKING (To avoid repeats)
# ============================================================================

class ContentTracker:
    """
    Track what Life Path + Angle combinations have been generated
    Works with Google Sheets to avoid repeats
    """
    
    def __init__(self, sheets_logger):
        self.sheets_logger = sheets_logger
        self.generated_combinations = self._load_history()
    
    def _load_history(self):
        """Load previously generated Life Path content from sheets"""
        if not self.sheets_logger or not self.sheets_logger.enabled:
            return set()
        
        try:
            # Get all data from sheets
            generated = self.sheets_logger.get_generated_content()
            
            # Extract Life Path combinations (stored in transcript or metadata)
            # For now, return empty set - will implement after integration
            return set()
        except:
            return set()
    
    def is_combination_used(self, life_path_number, angle, variation):
        """Check if this combination was already generated"""
        combo = f"{life_path_number}-{angle}-{variation}"
        return combo in self.generated_combinations
    
    def mark_combination_used(self, life_path_number, angle, variation):
        """Mark a combination as generated"""
        combo = f"{life_path_number}-{angle}-{variation}"
        self.generated_combinations.add(combo)
    
    def get_unused_combination(self, life_path_number, angle):
        """
        Get an unused variation for a specific life path + angle
        
        Args:
            life_path_number: int
            angle: str
            
        Returns:
            str: variation name or None if all used
        """
        variations = LIFE_PATH_CONTENT_ANGLES[angle]['variations']
        
        for variation in variations:
            if not self.is_combination_used(life_path_number, angle, variation):
                return variation
        
        # All used - return random one (start new cycle)
        return random.choice(variations)


# ============================================================================
# MAIN USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Example: What should we generate today?
    print("=" * 70)
    print("CONTENT PLAN FOR TODAY")
    print("=" * 70)
    
    day_type = get_day_type()
    print(f"\nDay Type: {day_type.upper()}")
    print(f"Date: {datetime.now().strftime('%A, %B %d, %Y')}\n")
    
    plan = get_content_plan_for_day(day_type, reel_count=3)
    
    for i, spec in enumerate(plan, 1):
        print(f"Reel {i}:")
        print(f"  Type: {spec['type']}")
        
        if spec['type'] == 'life_path':
            print(f"  Life Path: {spec['life_path_number']}")
            print(f"  Angle: {spec['angle']}")
            print(f"  Variation: {spec['variation']}")
        else:
            print(f"  Angel Number: {spec['angel_number']}")
            print(f"  Style: {spec['style']}")
        
        print()
    
    print("=" * 70)
