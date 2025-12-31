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
# COLOR PALETTE - For text rotation in videos
# ============================================================================

TEXT_COLORS = {
    'yellow': (255, 200, 0),      # Dark Yellow/Orange (original)
    'pink': (255, 100, 150),      # Hot Pink
    'purple': (150, 100, 255),    # Purple
    'coral': (255, 80, 80),       # Red/Coral
    'skyblue': (100, 200, 255),   # Sky Blue
    'orange': (255, 150, 50),     # Orange
}

# Color names in rotation order
COLOR_ROTATION_ORDER = ['yellow', 'pink', 'purple', 'coral', 'orange', 'skyblue']


# ============================================================================
# HASHTAG SETS - Relevant to content type
# ============================================================================

LIFE_PATH_HASHTAGS = [
    'numerology',
    'lifepath',
    'lifepathumber',
    'spirituality',
    'selfdiscovery',
    'manifestation',
    'lawofattraction',
    'spiritualawakening',
    'numerologyreading',
    'birthdatenumerology',
    'knowyourself',
    'personalgrowth',
    'selfawareness',
    'astrology',
    'zodiac',
    'birthchart',
    'soulgrowth',
    'spiritualjourney',
    'consciousness',
    'awakening',
    'innerwork',
    'selfmastery',
    'lifepurpose',
    'destinynumber',
    'soulpurpose',
    'spiritualgrowth',
    'mindfulness',
    'transformation',
    'healing',
    'enlightenment'
]

ANGEL_NUMBER_HASHTAGS = [
    'numerology',
    'angelnumbers',
    'angelmessages',
    'divineguidance',
    'synchronicity',
    'signs',
    'universe',
    'spiritualguidance',
    'divinity',
    'spirituality',
    'manifestation',
    'lawofattraction',
    'spiritualawakening',
    'universesigns',
    'divinesigns',
    'angelicguidance',
    'spiritualsigns',
    'awakening',
    'consciousness',
    'highervibration',
    'energyhealing',
    'lightworker',
    'starseed',
    'raiseyourvibration',
    'spiritualpath',
    'divinetiming',
    'trusttheuniverse',
    'innerwisdom',
    'intuition',
    'spiritualjourney'
]


# ============================================================================
# CONTENT SCHEDULING LOGIC
# ============================================================================

def load_used_combinations_from_sheets(sheets_logger):
    """
    Load previously generated combinations from Google Sheets for rotation tracking

    Args:
        sheets_logger: SheetsLogger instance

    Returns:
        dict with 'life_path' and 'angel_number' sets of used (number, angle/style) tuples
    """
    if not sheets_logger or not hasattr(sheets_logger, 'enabled') or not sheets_logger.enabled:
        return {'life_path': set(), 'angel_number': set()}

    try:
        # Get all data from sheet
        all_data = sheets_logger.sheet.get_all_values()

        life_path_combos = set()
        angel_number_combos = set()

        # Skip header row
        for row in all_data[1:]:
            if len(row) >= 3 and row[1] != 'TEST':
                identifier = row[1]  # Column B: Number or "LP7-identity"
                style = row[2]       # Column C: Style/Type

                # Check if it's a Life Path entry (format: "LP7-identity")
                if identifier.startswith('LP') and '-' in identifier:
                    # Extract number and angle from "LP7-identity"
                    parts = identifier.split('-', 1)
                    lp_num = int(parts[0][2:])  # Remove "LP" prefix
                    angle = parts[1] if len(parts) > 1 else 'identity'
                    life_path_combos.add((lp_num, angle))
                else:
                    # Angel number entry
                    angel_number_combos.add((identifier, style))

        return {
            'life_path': life_path_combos,
            'angel_number': angel_number_combos
        }

    except Exception as e:
        print(f"   ⚠️  Failed to load rotation history: {e}")
        return {'life_path': set(), 'angel_number': set()}


def select_text_color(used_colors=None):
    """
    Select a text color with rotation tracking - don't repeat until all colors used

    Args:
        used_colors: set/list of color names already used

    Returns:
        tuple: (color_name, color_rgb_tuple)
        Example: ('pink', (255, 100, 150))
    """
    if used_colors is None:
        used_colors = set()
    else:
        used_colors = set(used_colors)

    # Find unused colors
    available_colors = [c for c in COLOR_ROTATION_ORDER if c not in used_colors]

    # If all colors used, reset cycle
    if not available_colors:
        print("   ♻️  All text colors used, starting new color rotation cycle")
        available_colors = COLOR_ROTATION_ORDER.copy()

    # Pick random color from available
    color_name = random.choice(available_colors)
    color_rgb = TEXT_COLORS[color_name]

    return color_name, color_rgb


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


def get_content_plan_for_day(day_type=None, reel_count=3, sheets_logger=None):
    """
    Get the content plan for a given day type with rotation tracking

    Args:
        day_type: str ('life_path', 'angel_number', 'wildcard')
        reel_count: int (how many reels to generate, default 3)
        sheets_logger: SheetsLogger instance for loading rotation history

    Returns:
        list: Content specifications for each reel
    """
    if day_type is None:
        day_type = get_day_type()

    # Load previously used combinations for rotation
    used_combos = load_used_combinations_from_sheets(sheets_logger)

    if day_type == 'life_path':
        return get_life_path_plan(reel_count, used_combos['life_path'])
    elif day_type == 'angel_number':
        return get_angel_number_plan(reel_count, used_combos['angel_number'])
    else:  # wildcard
        return get_wildcard_plan(reel_count, used_combos)


def get_life_path_plan(count=3, previously_used_combos=None):
    """
    Generate plan for Life Path content (Mon/Wed/Fri)

    Strategy: Rotate through (number, angle) combinations - don't repeat until full cycle complete
    Example: LP7-Identity, LP3-Career, LP5-Relationships
    Next LP7 will have different angle until all LP7 angles are used

    Args:
        count: int (number of reels)
        previously_used_combos: set/list of (number, angle) tuples already generated

    Returns:
        list of dicts with content specs
    """
    all_life_paths = get_all_life_paths()
    all_angles = list(LIFE_PATH_CONTENT_ANGLES.keys())

    # Initialize previously used combinations
    if previously_used_combos is None:
        previously_used_combos = set()
    else:
        # Convert to set of tuples (number, angle)
        previously_used_combos = set(previously_used_combos)

    plan = []

    # Track what we've used in this batch (avoid duplicates in same day)
    used_today = set()

    for i in range(count):
        # Try to find an unused combination
        available_combos = []
        for lp in all_life_paths:
            for angle in all_angles:
                combo = (lp, angle)
                if combo not in previously_used_combos and combo not in used_today:
                    available_combos.append(combo)

        # If no unused combinations left, start new cycle
        if not available_combos:
            print("   ♻️  All Life Path combinations used, starting new rotation cycle")
            previously_used_combos = set()
            # Rebuild available combos excluding today's
            available_combos = [(lp, angle) for lp in all_life_paths for angle in all_angles
                              if (lp, angle) not in used_today]

        # Pick a random combination
        life_path, angle = random.choice(available_combos)
        used_today.add((life_path, angle))

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


def get_angel_number_plan(count=3, previously_used_combos=None):
    """
    Generate plan for Angel Number content (Tue/Thu/Sat)

    Strategy: Rotate through (number, style) combinations - don't repeat until full cycle complete
    Next time same angel number is used, it will have different style

    Args:
        count: int (number of reels)
        previously_used_combos: set/list of (number, style) tuples already generated

    Returns:
        list of dicts with content specs
    """
    all_numbers = get_all_angel_numbers()
    styles = ['storytelling', 'practical', 'insights']

    # Initialize previously used combinations
    if previously_used_combos is None:
        previously_used_combos = set()
    else:
        # Convert to set of tuples (number, style)
        previously_used_combos = set(previously_used_combos)

    plan = []
    used_today = set()

    for i in range(count):
        # Try to find an unused combination
        available_combos = []
        for num in all_numbers:
            for style in styles:
                combo = (num, style)
                if combo not in previously_used_combos and combo not in used_today:
                    available_combos.append(combo)

        # If no unused combinations left, start new cycle
        if not available_combos:
            print("   ♻️  All Angel Number combinations used, starting new rotation cycle")
            previously_used_combos = set()
            # Rebuild available combos excluding today's
            available_combos = [(num, style) for num in all_numbers for style in styles
                              if (num, style) not in used_today]

        # Pick a random combination
        angel_number, style = random.choice(available_combos)
        used_today.add((angel_number, style))

        plan.append({
            'type': 'angel_number',
            'angel_number': angel_number,
            'style': style,
            'reel_number': i + 1
        })

    return plan


def get_wildcard_plan(count=3, used_combos=None):
    """
    Generate plan for Sunday wildcard content with rotation tracking

    Strategy: Mix of life path, angel numbers, or special content

    Args:
        count: int (number of reels)
        used_combos: dict with 'life_path' and 'angel_number' used combinations

    Returns:
        list of dicts with content specs
    """
    if used_combos is None:
        used_combos = {'life_path': set(), 'angel_number': set()}

    plan = []

    # Sunday: Mix it up - 2 life path, 1 angel number (or vice versa)
    content_types = ['life_path', 'life_path', 'angel_number']
    random.shuffle(content_types)

    for i, content_type in enumerate(content_types[:count]):
        if content_type == 'life_path':
            lp_plan = get_life_path_plan(1, used_combos['life_path'])[0]
            lp_plan['reel_number'] = i + 1
            plan.append(lp_plan)
        else:
            an_plan = get_angel_number_plan(1, used_combos['angel_number'])[0]
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
    
    # Build hashtags - add specific Life Path tag + shuffle for variety
    specific_hashtags = [
        f'lifepath{life_path_num}',
        'numerology',
        'lifepath'
    ]

    # Shuffle and select random hashtags from life path pool (exclude already used ones)
    available_tags = [tag for tag in LIFE_PATH_HASHTAGS if tag not in specific_hashtags]
    random_tags = random.sample(available_tags, min(12, len(available_tags)))
    all_hashtags = specific_hashtags + random_tags
    hashtags = ' '.join([f'#{tag}' for tag in all_hashtags[:15]])
    
    # Simple caption that doesn't rely on complex template variables
    # We'll use the actual generated content
    caption = f"""Life Path {life_path_num}: {lp_data['name']}

{content_data.get('hook', '')}

{content_data.get('meaning', '')}

{content_data.get('action', '')}

👇 What's YOUR Life Path Number?

Calculate: seventhlifepath.com
Comment your number below!

New here? Watch my intro (pinned post) 📍

{hashtags}"""

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
    
    # Build hashtags - shuffle for variety across posts
    specific_hashtags = [
        f'angelnumber{angel_number}',
        f'{angel_number}',
        'angelnumbers',
        'synchronicity',
        'signs'
    ]

    # Shuffle and select random hashtags from angel number pool
    available_tags = [tag for tag in ANGEL_NUMBER_HASHTAGS if tag not in specific_hashtags]
    random_tags = random.sample(available_tags, min(10, len(available_tags)))
    all_hashtags = specific_hashtags + random_tags
    hashtags = ' '.join([f'#{tag}' for tag in all_hashtags[:15]])
    
    # Build full transcript caption
    caption_parts = [
        f"Seeing {angel_number}?",
        content_data.get('hook', ''),
        content_data.get('meaning', ''),
        content_data.get('action', ''),
        content_data.get('cta', '')
    ]

    # Join parts with double line breaks, then add CTA and hashtags
    full_transcript = '\n\n'.join([part for part in caption_parts if part])
    caption = f"""{full_transcript}

👇 What's YOUR Life Path Number?

Calculate: seventhlifepath.com
Comment your number below!

New here? Watch my intro (pinned post) 📍

{hashtags}"""

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
