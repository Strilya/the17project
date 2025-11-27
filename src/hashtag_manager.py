"""
Hashtag Manager Module

This module manages dynamic hashtag rotation for Instagram posts.
It ensures variety by rotating through different hashtag combinations
while maintaining core brand hashtags.

Main functionality:
- Core brand hashtags (always included)
- Rotating hashtag pools by category
- Track recently used hashtags
- Random selection for variety
"""

import json
import random
import logging
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Don't repeat same hashtags within 7 days
HASHTAG_COOLDOWN_DAYS = 7


class HashtagManager:
    """Manages dynamic hashtag rotation with variety."""

    def __init__(self, config_path: Path = None):
        """Initialize hashtag manager."""
        if config_path is None:
            config_path = Path("config/hashtag_pools.json")
        
        self.config_path = config_path
        self.tracker_path = Path("config/hashtag_tracker.json")
        
        # Load or create hashtag pools
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.pools = json.load(f)
        else:
            self.pools = self._create_default_pools()
            self._save_pools()
        
        # Load or create tracker
        if self.tracker_path.exists():
            with open(self.tracker_path, 'r') as f:
                self.tracker = json.load(f)
        else:
            self.tracker = {
                "recent_hashtags": [],
                "last_reset": None
            }
            self._save_tracker()

    def _create_default_pools(self) -> Dict:
        """Create default hashtag pools."""
        return {
            "core_brand": [
                "#The17Project",
                "#AngelNumbers",
                "#Manifestation",
                "#Spirituality",
                "#LawyOfAttraction",
                "#SpiritualAwakening",
                "#Productivity",
                "#Mindfulness"
            ],
            "angel_numbers_broad": [
                "#AngelNumber",
                "#AngelNumberMeanings",
                "#Numerology",
                "#NumerologyReading",
                "#SacredNumbers",
                "#DivineTiming",
                "#UniverseSigns",
                "#SpiritualSigns",
                "#Synchronicity",
                "#1111Meaning"
            ],
            "angel_numbers_specific": [
                "#AngelNumber17",
                "#AngelNumber111",
                "#AngelNumber222",
                "#AngelNumber333",
                "#AngelNumber444",
                "#AngelNumber555",
                "#AngelNumber717",
                "#AngelNumber911",
                "#AngelNumber1111",
                "#SeeingNumbers",
                "#RepeatNumbers"
            ],
            "manifestation": [
                "#ManifestYourDreams",
                "#ManifestationCoach",
                "#ManifestationTips",
                "#LawOfAttractionTips",
                "#AbundanceMindset",
                "#ManifestingAbundance",
                "#ManifestYourLife",
                "#ManifestingMagic",
                "#369Method",
                "#ScriptingManifestation",
                "#VisionBoardGoals",
                "#ManifestationJourney",
                "#PositiveAffirmations",
                "#AffirmationDaily"
            ],
            "spiritual_growth": [
                "#SpiritualGrowth",
                "#SpiritualJourney",
                "#SpiritualAwakening",
                "#Consciousness",
                "#RaiseYourVibration",
                "#HigherSelf",
                "#IntuitionDevelopment",
                "#SpiritualGuidance",
                "#SoulPurpose",
                "#DivineFeminine",
                "#SpiritualHealing",
                "#EnergyHealing",
                "#ChakraAlignment",
                "#SpirituallyAwake",
                "#InnerWisdom"
            ],
            "productivity": [
                "#ProductivityTips",
                "#DeepWork",
                "#FocusMode",
                "#FlowState",
                "#TimeManagement",
                "#ProductivityHacks",
                "#WorkSmarter",
                "#ProductiveLife",
                "#IntentionalLiving",
                "#MindfulProductivity",
                "#ProductiveMorning",
                "#GoalSetting",
                "#ProductivityCoach",
                "#EfficiencyTips"
            ],
            "wellness_mindfulness": [
                "#MindfulnessMatters",
                "#MeditationPractice",
                "#DailyMeditation",
                "#ZenLife",
                "#InnerPeace",
                "#MindfulLiving",
                "#SelfCare",
                "#WellnessJourney",
                "#MentalClarity",
                "#PresentMoment",
                "#GratitudePractice",
                "#PositiveVibes",
                "#GoodEnergy"
            ],
            "lifestyle_motivation": [
                "#MotivationDaily",
                "#InspirationalQuotes",
                "#PositiveMindset",
                "#PersonalGrowth",
                "#SelfImprovement",
                "#SuccessMindset",
                "#DreamBig",
                "#BelieveInYourself",
                "#YouGotThis",
                "#EmpoweredWomen",
                "#BossLady",
                "#GirlBoss",
                "#MillennialLife",
                "#GenZ"
            ]
        }

    def _save_pools(self):
        """Save hashtag pools to config file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.pools, f, indent=2)
        logger.info(f"Saved hashtag pools to {self.config_path}")

    def _save_tracker(self):
        """Save tracker to file."""
        self.tracker_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tracker_path, 'w') as f:
            json.dump(self.tracker, f, indent=2)
        logger.info(f"Saved hashtag tracker to {self.tracker_path}")

    def _clean_recent_hashtags(self):
        """Remove hashtags older than cooldown period."""
        cutoff_date = datetime.now() - timedelta(days=HASHTAG_COOLDOWN_DAYS)
        
        self.tracker["recent_hashtags"] = [
            entry for entry in self.tracker["recent_hashtags"]
            if datetime.fromisoformat(entry["date"]) > cutoff_date
        ]

    def _get_recently_used_hashtags(self) -> Set[str]:
        """Get set of recently used hashtags."""
        self._clean_recent_hashtags()
        
        recent = set()
        for entry in self.tracker["recent_hashtags"]:
            recent.update(entry["hashtags"])
        
        return recent

    def generate_hashtags(self, category: str, count: int = 15) -> List[str]:
        """
        Generate dynamic hashtag set.
        
        Args:
            category: Content category (angel_numbers, productivity, etc.)
            count: Number of rotating hashtags to add (default 15)
            
        Returns:
            List of hashtags (core + rotating)
        """
        logger.info(f"\n🏷️  GENERATING DYNAMIC HASHTAGS")
        logger.info(f"  Category: {category}")
        logger.info(f"  Target rotating count: {count}")
        
        # Always include ALL core brand hashtags
        core = self.pools.get("core_brand", [])
        hashtags = core.copy()
        logger.info(f"  Core hashtags: {len(core)}")
        
        # Get recently used hashtags to avoid
        recent = self._get_recently_used_hashtags()
        logger.info(f"  Recently used (avoiding): {len(recent)}")
        
        # Determine relevant pools based on category
        relevant_pools = []
        
        if category == "angel_numbers":
            relevant_pools = [
                "angel_numbers_broad",
                "angel_numbers_specific",
                "manifestation",
                "spiritual_growth"
            ]
        elif category == "productivity":
            relevant_pools = [
                "productivity",
                "wellness_mindfulness",
                "lifestyle_motivation",
                "spiritual_growth"
            ]
        elif category == "manifestation":
            relevant_pools = [
                "manifestation",
                "angel_numbers_broad",
                "spiritual_growth",
                "lifestyle_motivation"
            ]
        elif category == "spiritual_growth":
            relevant_pools = [
                "spiritual_growth",
                "wellness_mindfulness",
                "manifestation",
                "angel_numbers_broad"
            ]
        else:
            # Default: use all pools
            relevant_pools = list(self.pools.keys())
            if "core_brand" in relevant_pools:
                relevant_pools.remove("core_brand")
        
        # Collect available hashtags from relevant pools
        available = []
        for pool_name in relevant_pools:
            pool = self.pools.get(pool_name, [])
            # Filter out recently used and already selected
            available.extend([
                tag for tag in pool 
                if tag not in recent and tag not in hashtags
            ])
        
        # Shuffle for randomness
        random.shuffle(available)
        
        # Select hashtags up to count
        rotating = available[:count]
        hashtags.extend(rotating)
        
        logger.info(f"  Rotating hashtags: {len(rotating)}")
        logger.info(f"  Total hashtags: {len(hashtags)}")
        
        return hashtags

    def mark_hashtags_used(self, hashtags: List[str]):
        """
        Mark hashtags as recently used.
        
        Args:
            hashtags: List of hashtags to mark
        """
        entry = {
            "hashtags": hashtags,
            "date": datetime.now().isoformat()
        }
        
        self.tracker["recent_hashtags"].append(entry)
        self._save_tracker()
        
        logger.info(f"✅ Marked {len(hashtags)} hashtags as used")


def main():
    """Test hashtag generation."""
    manager = HashtagManager()
    
    categories = ["angel_numbers", "productivity", "manifestation", "spiritual_growth"]
    
    for category in categories:
        print(f"\n{'='*70}")
        print(f"Testing: {category}")
        print('='*70)
        
        hashtags = manager.generate_hashtags(category, count=15)
        
        print(f"\nGenerated {len(hashtags)} hashtags:")
        for tag in hashtags:
            print(f"  {tag}")
        
        # Mark as used
        manager.mark_hashtags_used(hashtags)


if __name__ == "__main__":
    main()
