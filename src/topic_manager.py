"""
Topic Manager Module

This module handles intelligent topic tracking and rotation for The17Project
content generation. It ensures content stays fresh by:
- Rotating through topics in a round-robin fashion across categories
- Tracking used topics to prevent repeats
- Maintaining a 90-day history buffer
- Resetting categories when all topics have been used

Main functionality:
- Load and save topic tracking state
- Select next unused topic from rotation
- Mark topics as used
- Reset categories when exhausted
- Check 90-day history for recent repeats
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration constants
DAYS_BEFORE_REPEAT = 90  # Don't repeat same topic within 90 days
ROTATION_STRATEGY = "round_robin"  # Rotate categories evenly


class TopicManager:
    """
    Manages topic rotation and tracking for content generation.

    This class ensures content variety by:
    1. Rotating through categories in round-robin fashion
    2. Prioritizing high-priority topics within each category
    3. Tracking used topics to prevent repeats
    4. Maintaining 90-day history to avoid recent repeats
    5. Auto-resetting categories when all topics exhausted
    """

    def __init__(self, tracker_path: Optional[str] = None):
        """
        Initialize the TopicManager.

        Args:
            tracker_path: Path to topic_tracker.json file
        """
        # Set path to tracker file
        if tracker_path is None:
            self.tracker_path = Path(__file__).parent.parent / "config" / "topic_tracker.json"
        else:
            self.tracker_path = Path(tracker_path)

        # Load tracker data
        self.tracker = self._load_tracker()

        logger.info("TopicManager initialized successfully")
        logger.info(f"Tracker path: {self.tracker_path}")
        self._log_status()

    def _load_tracker(self) -> Dict[str, Any]:
        """
        Load topic tracker from JSON file.

        Returns:
            Dictionary containing tracker data
        """
        try:
            with open(self.tracker_path, 'r', encoding='utf-8') as f:
                tracker = json.load(f)
            logger.info(f"Loaded tracker from {self.tracker_path}")
            return tracker
        except FileNotFoundError:
            logger.error(f"Tracker file not found: {self.tracker_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in tracker file: {e}")
            raise

    def _save_tracker(self) -> None:
        """Save tracker data to JSON file."""
        try:
            with open(self.tracker_path, 'w', encoding='utf-8') as f:
                json.dump(self.tracker, f, indent=2, default=str)
            logger.info(f"Saved tracker to {self.tracker_path}")
        except Exception as e:
            logger.error(f"Failed to save tracker: {e}")
            raise

    def _log_status(self) -> None:
        """Log current status of topic tracking."""
        for category in self.tracker["category_order"]:
            cat_data = self.tracker["topics"][category]
            total = self._get_total_topics_count(category)
            used = len(cat_data.get("used", []))
            logger.info(f"  {category}: {used}/{total} topics used")

        history_size = len(self.tracker.get("content_history", []))
        logger.info(f"  Content history: {history_size} entries")

    def _get_total_topics_count(self, category: str) -> int:
        """
        Get total number of topics in a category.

        Args:
            category: Category name

        Returns:
            Total count of all topics in category
        """
        cat_data = self.tracker["topics"][category]

        if category == "angel_numbers":
            return len(cat_data.get("high_priority", [])) + len(cat_data.get("interesting", []))
        elif category == "productivity":
            return len(cat_data.get("techniques", []))
        elif category == "manifestation":
            return len(cat_data.get("practices", []))
        elif category == "spiritual_growth":
            return len(cat_data.get("topics", []))
        else:
            return 0

    def _get_all_topics(self, category: str) -> List[str]:
        """
        Get all topics for a category.

        Args:
            category: Category name

        Returns:
            List of all topics in category
        """
        cat_data = self.tracker["topics"][category]

        if category == "angel_numbers":
            # High priority first, then interesting
            return cat_data.get("high_priority", []) + cat_data.get("interesting", [])
        elif category == "productivity":
            return cat_data.get("techniques", [])
        elif category == "manifestation":
            return cat_data.get("practices", [])
        elif category == "spiritual_growth":
            return cat_data.get("topics", [])
        else:
            return []

    def get_unused_topics(self, category: str) -> List[str]:
        """
        Get list of unused topics for a category.

        Args:
            category: Category name

        Returns:
            List of unused topics
        """
        all_topics = self._get_all_topics(category)
        used_topics = self.tracker["topics"][category].get("used", [])

        unused = [t for t in all_topics if t not in used_topics]
        return unused

    def check_90_day_history(self, topic: str) -> bool:
        """
        Check if topic was used within the last 90 days.

        Args:
            topic: Topic to check

        Returns:
            True if topic was used recently (within 90 days), False otherwise
        """
        history = self.tracker.get("content_history", [])
        cutoff_date = datetime.now() - timedelta(days=DAYS_BEFORE_REPEAT)

        for entry in history:
            if entry.get("topic") == topic:
                entry_date = datetime.fromisoformat(entry.get("date", "1900-01-01"))
                if entry_date > cutoff_date:
                    logger.info(f"Topic '{topic}' was used within 90 days (on {entry_date.date()})")
                    return True

        return False

    def reset_category_if_complete(self, category: str) -> bool:
        """
        Reset a category if all topics have been used.

        Args:
            category: Category name

        Returns:
            True if category was reset, False otherwise
        """
        unused = self.get_unused_topics(category)

        if len(unused) == 0:
            logger.info(f"Category '{category}' exhausted, resetting...")
            self.tracker["topics"][category]["used"] = []
            self.tracker["topics"][category]["last_used_date"] = None
            self._save_tracker()
            logger.info(f"Category '{category}' reset complete")
            return True

        return False

    def _get_next_category(self) -> str:
        """
        Get the next category in rotation.

        Returns:
            Next category name
        """
        category_order = self.tracker.get("category_order", [
            "angel_numbers", "productivity", "manifestation", "spiritual_growth"
        ])
        current_index = self.tracker.get("current_category_index", 0)

        # Get current category
        category = category_order[current_index]

        return category

    def _advance_category_index(self) -> None:
        """Advance to the next category in rotation."""
        category_order = self.tracker.get("category_order", [])
        current_index = self.tracker.get("current_category_index", 0)

        # Move to next category (wrap around)
        next_index = (current_index + 1) % len(category_order)
        self.tracker["current_category_index"] = next_index

    def get_next_topic(self) -> Dict[str, str]:
        """
        Get the next topic for content generation.

        This method:
        1. Gets the current category from rotation
        2. Finds an unused topic (prioritizing high-priority)
        3. Checks 90-day history to avoid recent repeats
        4. Returns the topic and advances rotation

        Returns:
            Dictionary with 'type' (category) and 'value' (topic)
            Example: {"type": "angel_numbers", "value": "717"}
        """
        category_order = self.tracker.get("category_order", [])
        attempts = 0
        max_attempts = len(category_order) * 2  # Safety limit

        while attempts < max_attempts:
            category = self._get_next_category()
            logger.info(f"Checking category: {category}")

            # Reset category if all topics used
            self.reset_category_if_complete(category)

            # Get unused topics
            unused = self.get_unused_topics(category)
            logger.info(f"  Unused topics in {category}: {len(unused)}")

            # Find a topic not used in last 90 days
            for topic in unused:
                if not self.check_90_day_history(topic):
                    logger.info(f"Selected topic: '{topic}' from category '{category}'")

                    # Advance to next category for next time
                    self._advance_category_index()
                    self._save_tracker()

                    return {
                        "type": category,
                        "value": topic
                    }

            # If all unused topics were recently used, try next category
            logger.warning(f"All unused topics in '{category}' were used within 90 days")
            self._advance_category_index()
            attempts += 1

        # Fallback: if somehow all topics exhausted, reset everything
        logger.warning("All topics exhausted across all categories! Resetting all...")
        for cat in category_order:
            self.tracker["topics"][cat]["used"] = []
        self.tracker["content_history"] = []
        self._save_tracker()

        # Return first topic from first category
        first_cat = category_order[0]
        first_topic = self._get_all_topics(first_cat)[0]
        return {"type": first_cat, "value": first_topic}

    def mark_topic_used(self, topic: str, category: str) -> None:
        """
        Mark a topic as used.

        Args:
            topic: The topic that was used
            category: The category of the topic
        """
        # Add to used list for category
        if topic not in self.tracker["topics"][category].get("used", []):
            self.tracker["topics"][category]["used"].append(topic)

        # Update last used date
        self.tracker["topics"][category]["last_used_date"] = datetime.now().isoformat()

        # Add to content history
        history_entry = {
            "topic": topic,
            "category": category,
            "date": datetime.now().isoformat()
        }
        self.tracker["content_history"].append(history_entry)

        # Trim history to last 365 days (keep some buffer beyond 90 days)
        self._trim_history(365)

        # Save changes
        self._save_tracker()

        logger.info(f"Marked topic '{topic}' as used in category '{category}'")

    def _trim_history(self, days: int) -> None:
        """
        Trim content history to entries within specified days.

        Args:
            days: Number of days to keep
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        history = self.tracker.get("content_history", [])

        trimmed = []
        for entry in history:
            try:
                entry_date = datetime.fromisoformat(entry.get("date", "1900-01-01"))
                if entry_date > cutoff_date:
                    trimmed.append(entry)
            except (ValueError, TypeError):
                # Keep entries with invalid dates (shouldn't happen)
                trimmed.append(entry)

        removed = len(history) - len(trimmed)
        if removed > 0:
            logger.info(f"Trimmed {removed} old entries from content history")

        self.tracker["content_history"] = trimmed

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of topic tracking.

        Returns:
            Dictionary with status information
        """
        status = {
            "categories": {},
            "history_size": len(self.tracker.get("content_history", [])),
            "current_category": self._get_next_category(),
            "last_reset_date": self.tracker.get("last_reset_date")
        }

        for category in self.tracker["category_order"]:
            total = self._get_total_topics_count(category)
            used = len(self.tracker["topics"][category].get("used", []))
            unused = self.get_unused_topics(category)

            status["categories"][category] = {
                "total": total,
                "used": used,
                "remaining": len(unused),
                "percentage_used": round((used / total) * 100, 1) if total > 0 else 0
            }

        return status


def main():
    """
    Main function for testing TopicManager locally.

    Usage:
        python src/topic_manager.py
    """
    try:
        print("\n" + "="*70)
        print("TESTING TOPIC MANAGER")
        print("="*70)

        # Initialize manager
        manager = TopicManager()

        # Get current status
        print("\n--- Current Status ---")
        status = manager.get_status()
        print(f"Current category in rotation: {status['current_category']}")
        print(f"Content history size: {status['history_size']}")

        for cat, info in status["categories"].items():
            print(f"  {cat}: {info['used']}/{info['total']} used ({info['percentage_used']}%)")

        # Get next topic
        print("\n--- Getting Next Topic ---")
        topic = manager.get_next_topic()
        print(f"Selected: {topic['value']} (category: {topic['type']})")

        # Simulate marking as used
        print("\n--- Marking Topic as Used ---")
        manager.mark_topic_used(topic["value"], topic["type"])
        print(f"Marked '{topic['value']}' as used")

        # Show updated status
        print("\n--- Updated Status ---")
        status = manager.get_status()
        for cat, info in status["categories"].items():
            print(f"  {cat}: {info['used']}/{info['total']} used ({info['percentage_used']}%)")

        # Get next few topics (preview)
        print("\n--- Preview: Next 5 Topics ---")
        for i in range(5):
            next_topic = manager.get_next_topic()
            print(f"  {i+1}. {next_topic['value']} ({next_topic['type']})")
            # Note: Not marking as used, just previewing

        print("\n" + "="*70)
        print("TOPIC MANAGER TEST COMPLETE")
        print("="*70)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
