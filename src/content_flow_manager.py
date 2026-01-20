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
# SMART CONTEXTUAL HASHTAG SYSTEM
# Selects EXACTLY 5 relevant hashtags based on content theme
# ============================================================================

# Theme-based hashtag pools (select 3 from matching theme)
THEME_HASHTAGS = {
    'manifestation': ['manifestation', 'lawofattraction', 'abundance', 'manifest', 'attracting'],
    'protection': ['divineprotection', 'spiritualguidance', 'angelsigns', 'guided', 'protected'],
    'transformation': ['transformation', 'change', 'spiritualjourney', 'awakening', 'evolving'],
    'love': ['twinflame', 'soulmate', 'divinelove', 'loveenergy', 'heartchakra'],
    'new_beginnings': ['newbeginnings', 'freshstart', 'opportunity', 'starting', 'rebirth'],
    'intuition': ['intuition', 'innerwisdom', 'trustyourself', 'innerknowing', 'gutfeeling'],
    'alignment': ['alignment', 'synchronicity', 'divinetiming', 'flow', 'inflow'],
    'abundance': ['abundance', 'prosperity', 'wealthy', 'receiving', 'blessed'],
    'spiritual_growth': ['spiritualgrowth', 'ascension', 'higherself', 'consciousness', 'enlightenment'],
    'action': ['divineaction', 'takeaction', 'movingforward', 'momentum', 'progress'],
    'trust': ['trusttheuniverse', 'faith', 'believing', 'surrender', 'lettinggo'],
    'clarity': ['clarity', 'clearpath', 'vision', 'insight', 'understanding'],
}

# Angel number to primary theme mapping
ANGEL_NUMBER_THEMES = {
    # 1s - New beginnings, manifestation, leadership
    '111': ['manifestation', 'new_beginnings', 'alignment'],
    '1111': ['manifestation', 'new_beginnings', 'spiritual_growth'],
    '11': ['intuition', 'spiritual_growth', 'alignment'],

    # 2s - Balance, relationships, partnerships
    '222': ['love', 'trust', 'alignment'],
    '2222': ['love', 'trust', 'alignment'],
    '22': ['alignment', 'trust', 'manifestation'],

    # 3s - Creativity, communication, growth
    '333': ['spiritual_growth', 'alignment', 'trust'],
    '3333': ['spiritual_growth', 'manifestation', 'abundance'],
    '33': ['spiritual_growth', 'intuition', 'clarity'],

    # 4s - Protection, stability, foundation
    '444': ['protection', 'trust', 'alignment'],
    '4444': ['protection', 'abundance', 'trust'],
    '44': ['protection', 'alignment', 'trust'],

    # 5s - Change, transformation, freedom
    '555': ['transformation', 'new_beginnings', 'action'],
    '5555': ['transformation', 'action', 'new_beginnings'],
    '55': ['transformation', 'action', 'clarity'],

    # 6s - Balance, harmony, love
    '666': ['love', 'alignment', 'trust'],
    '6666': ['love', 'abundance', 'alignment'],
    '66': ['love', 'trust', 'alignment'],

    # 7s - Spirituality, intuition, inner wisdom
    '777': ['spiritual_growth', 'intuition', 'alignment'],
    '7777': ['spiritual_growth', 'intuition', 'abundance'],
    '77': ['intuition', 'spiritual_growth', 'clarity'],

    # 8s - Abundance, success, power
    '888': ['abundance', 'manifestation', 'action'],
    '8888': ['abundance', 'manifestation', 'new_beginnings'],
    '88': ['abundance', 'action', 'manifestation'],

    # 9s - Completion, endings, humanitarianism
    '999': ['transformation', 'spiritual_growth', 'new_beginnings'],
    '9999': ['transformation', 'spiritual_growth', 'trust'],
    '99': ['transformation', 'clarity', 'trust'],

    # 0s - Infinite potential, divine connection
    '000': ['spiritual_growth', 'new_beginnings', 'trust'],
    '0000': ['spiritual_growth', 'manifestation', 'alignment'],
    '00': ['spiritual_growth', 'intuition', 'alignment'],

    # Mixed sequences
    '1010': ['new_beginnings', 'spiritual_growth', 'action'],
    '1212': ['manifestation', 'alignment', 'new_beginnings'],
    '1234': ['action', 'new_beginnings', 'manifestation'],
    '911': ['transformation', 'new_beginnings', 'spiritual_growth'],
    '711': ['spiritual_growth', 'intuition', 'manifestation'],
    '411': ['protection', 'new_beginnings', 'action'],
    '311': ['spiritual_growth', 'manifestation', 'action'],
    '611': ['love', 'new_beginnings', 'alignment'],
    '811': ['abundance', 'new_beginnings', 'manifestation'],
    '1717': ['spiritual_growth', 'manifestation', 'intuition'],
    '1818': ['abundance', 'manifestation', 'new_beginnings'],
    '1919': ['transformation', 'new_beginnings', 'action'],
    '2020': ['trust', 'alignment', 'clarity'],
    '2121': ['new_beginnings', 'love', 'manifestation'],
    '2323': ['spiritual_growth', 'love', 'trust'],
    '3434': ['protection', 'spiritual_growth', 'alignment'],
    '4545': ['transformation', 'protection', 'action'],
    '5656': ['transformation', 'love', 'new_beginnings'],
    '6767': ['spiritual_growth', 'love', 'intuition'],
    '7878': ['spiritual_growth', 'abundance', 'intuition'],
    '8989': ['abundance', 'transformation', 'action'],
    '1313': ['spiritual_growth', 'transformation', 'action'],
    '1414': ['protection', 'new_beginnings', 'manifestation'],
    '1515': ['transformation', 'new_beginnings', 'action'],
    '1616': ['love', 'new_beginnings', 'alignment'],
}

# Life Path number to primary theme mapping
LIFE_PATH_THEMES = {
    1: ['new_beginnings', 'action', 'manifestation'],      # Leader, pioneer
    2: ['love', 'intuition', 'alignment'],                  # Diplomat, peacemaker
    3: ['spiritual_growth', 'manifestation', 'abundance'],  # Creative, communicator
    4: ['protection', 'trust', 'action'],                   # Builder, organizer
    5: ['transformation', 'action', 'new_beginnings'],      # Adventurer, freedom
    6: ['love', 'protection', 'alignment'],                 # Nurturer, healer
    7: ['spiritual_growth', 'intuition', 'clarity'],        # Seeker, analyst
    8: ['abundance', 'manifestation', 'action'],            # Achiever, powerhouse
    9: ['spiritual_growth', 'transformation', 'love'],      # Humanitarian, old soul
    11: ['intuition', 'spiritual_growth', 'manifestation'], # Master intuitive
    22: ['manifestation', 'abundance', 'action'],           # Master builder
    33: ['love', 'spiritual_growth', 'alignment'],          # Master teacher
}

# Default themes for unknown numbers
DEFAULT_THEMES = ['spiritual_growth', 'alignment', 'trust']


def get_contextual_hashtags(content_identifier, content_data=None):
    """
    Generate EXACTLY 5 contextually relevant hashtags based on content theme.

    Args:
        content_identifier: Angel number (e.g., "1111") or life path (e.g., "LP7")
        content_data: Optional dict with hook, meaning, action, cta for additional context

    Returns:
        list: Exactly 5 hashtags (without # prefix)
    """
    hashtags = []

    # Determine if Life Path or Angel Number
    is_life_path = str(content_identifier).startswith('LP')

    if is_life_path:
        # Life Path content
        lp_num = int(str(content_identifier).replace('LP', '').split('-')[0])
        themes = LIFE_PATH_THEMES.get(lp_num, DEFAULT_THEMES)

        # 1. Core hashtag: numerology
        hashtags.append('numerology')

        # 2. Number-specific hashtag
        hashtags.append(f'lifepath{lp_num}')

    else:
        # Angel Number content
        angel_number = str(content_identifier)
        themes = ANGEL_NUMBER_THEMES.get(angel_number, DEFAULT_THEMES)

        # 1. Core hashtag: angelnumbers
        hashtags.append('angelnumbers')

        # 2. Number-specific hashtag
        hashtags.append(angel_number)

    # 3-5. Select 3 theme-relevant hashtags (one from each theme)
    used_hashtags = set(hashtags)

    for theme in themes[:3]:  # Use up to 3 themes
        theme_pool = THEME_HASHTAGS.get(theme, [])
        # Pick one hashtag from this theme that we haven't used
        available = [h for h in theme_pool if h not in used_hashtags]
        if available:
            selected = random.choice(available)
            hashtags.append(selected)
            used_hashtags.add(selected)

    # If we don't have 5 yet, fill with spiritual defaults
    fallback_pool = ['spiritualawakening', 'divinetiming', 'universe', 'signs', 'guided']
    while len(hashtags) < 5:
        for fallback in fallback_pool:
            if fallback not in used_hashtags and len(hashtags) < 5:
                hashtags.append(fallback)
                used_hashtags.add(fallback)

    return hashtags[:5]  # Ensure exactly 5


def format_hashtags_for_caption(hashtags):
    """
    Format hashtags with # prefix for caption use.

    Args:
        hashtags: list of hashtag strings (without #)

    Returns:
        str: Space-separated hashtags with # prefix
    """
    return ' '.join([f'#{tag}' for tag in hashtags])


# Legacy hashtag lists (kept for backwards compatibility)
LIFE_PATH_HASHTAGS = [
    'numerology', 'lifepath', 'lifepathumber', 'spirituality', 'selfdiscovery',
    'manifestation', 'lawofattraction', 'spiritualawakening', 'numerologyreading',
    'birthdatenumerology', 'knowyourself', 'personalgrowth', 'selfawareness'
]

ANGEL_NUMBER_HASHTAGS = [
    'angelnumbers', 'angelmessages', 'divineguidance', 'synchronicity', 'signs',
    'universe', 'spiritualguidance', 'spirituality', 'manifestation', 'lawofattraction'
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
    Generate caption for Life Path content with SMART CONTEXTUAL HASHTAGS.

    Args:
        content_spec: dict with life_path_number, angle, variation
        content_data: dict with hook, meaning, action, cta

    Returns:
        str: Instagram caption with exactly 5 relevant hashtags
    """
    life_path_num = content_spec['life_path_number']
    angle = content_spec['angle']

    # Get Life Path data
    lp_data = get_life_path_data(life_path_num)

    # Get EXACTLY 5 contextual hashtags based on life path themes
    content_identifier = f"LP{life_path_num}"
    hashtag_list = get_contextual_hashtags(content_identifier, content_data)
    hashtags = format_hashtags_for_caption(hashtag_list)

    # Build caption with ACTUAL blank lines (not \n escape characters)
    caption = f"""Life Path {life_path_num}: {lp_data['name']}

{content_data.get('hook', '')}

{content_data.get('meaning', '')}

{content_data.get('action', '')}

👇 What's YOUR Life Path Number?
📍 Calculate yours: seventhlifepath.com
👇 Comment your number below!

New here? Watch my intro (pinned post) 📍

{hashtags}"""

    return caption


def generate_angel_number_caption(content_spec, content_data):
    """
    Generate caption for Angel Number content with SMART CONTEXTUAL HASHTAGS.

    Args:
        content_spec: dict with angel_number, style
        content_data: dict with hook, meaning, action, cta

    Returns:
        str: Instagram caption with exactly 5 relevant hashtags
    """
    angel_number = content_spec['angel_number']

    # Get EXACTLY 5 contextual hashtags based on angel number themes
    hashtag_list = get_contextual_hashtags(angel_number, content_data)
    hashtags = format_hashtags_for_caption(hashtag_list)

    # Build caption with ACTUAL blank lines (not \n escape characters)
    caption = f"""Seeing {angel_number}?

{content_data.get('hook', '')}

{content_data.get('meaning', '')}

{content_data.get('action', '')}

{content_data.get('cta', '')}

👇 What's YOUR Life Path Number?
📍 Calculate yours: seventhlifepath.com
👇 Comment your number below!

New here? Watch my intro (pinned post) 📍

{hashtags}"""

    return caption


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
