import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz

class SpacedRepetition:
    def __init__(self, data_file: str = "vocabulary.json"):
        self.data_file = data_file
        self.vocabulary = self.load_vocabulary()
        # Melbourne timezone
        self.melbourne_tz = pytz.timezone('Australia/Melbourne')
        
    def load_vocabulary(self) -> Dict:
        """Load vocabulary from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    def save_vocabulary(self):
        """Save vocabulary to JSON file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.vocabulary, f, ensure_ascii=False, indent=2)
    
    def add_word(self, word: str, translation: str, example: str = "", word_type: str = "", notes: str = "") -> Dict:
        """Add a new word to the vocabulary"""
        word_id = str(int(time.time() * 1000))  # Unique ID based on timestamp
        
        now = datetime.now(self.melbourne_tz)
        word_data = {
            "id": word_id,
            "word": word,
            "translation": translation,
            "example": example,
            "word_type": word_type,
            "notes": notes,
            "created": now.isoformat(),
            "last_reviewed": None,
            "next_review": now.isoformat(),
            "interval": 0,  # Days until next review
            "ease_factor": 2.5,  # Anki's default ease factor
            "review_count": 0,
            "correct_count": 0,
            "incorrect_count": 0
        }
        
        self.vocabulary[word_id] = word_data
        self.save_vocabulary()
        return word_data
    
    def delete_word(self, word_id: str) -> bool:
        """Delete a word from vocabulary"""
        if word_id in self.vocabulary:
            del self.vocabulary[word_id]
            self.save_vocabulary()
            return True
        return False
    
    def get_due_words(self) -> List[Dict]:
        """Get words that are due for review"""
        now = datetime.now(self.melbourne_tz)
        due_words = []
        
        for word_data in self.vocabulary.values():
            next_review = datetime.fromisoformat(word_data["next_review"])
            if next_review <= now:
                due_words.append(word_data)
        
        # Sort by how overdue they are (most overdue first)
        due_words.sort(key=lambda x: datetime.fromisoformat(x["next_review"]))
        return due_words
    
    def get_all_words(self) -> List[Dict]:
        """Get all vocabulary words"""
        return list(self.vocabulary.values())
    
    def review_word(self, word_id: str, quality: int) -> Dict:
        """
        Review a word with quality rating (0-5)
        0: Complete blackout
        1: Incorrect response
        2: Hard response
        3: Good response
        4: Easy response
        5: Very easy response
        """
        if word_id not in self.vocabulary:
            raise ValueError("Word not found")
        
        word_data = self.vocabulary[word_id]
        now = datetime.now(self.melbourne_tz)
        
        # Update review statistics
        word_data["last_reviewed"] = now.isoformat()
        word_data["review_count"] += 1
        
        if quality >= 3:
            word_data["correct_count"] += 1
        else:
            word_data["incorrect_count"] += 1
        
        # Calculate new interval using improved SuperMemo 2 algorithm
        if quality < 3:
            # Incorrect response - reset interval
            word_data["interval"] = 0
            word_data["ease_factor"] = max(1.3, word_data["ease_factor"] - 0.2)
        else:
            # Correct response
            if word_data["interval"] == 0:
                word_data["interval"] = 1
            elif word_data["interval"] == 1:
                word_data["interval"] = 6
            else:
                word_data["interval"] = int(word_data["interval"] * word_data["ease_factor"])
            
            # Adjust ease factor
            if quality == 3:
                word_data["ease_factor"] = word_data["ease_factor"] + 0.1
            elif quality == 4:
                word_data["ease_factor"] = word_data["ease_factor"] + 0.15
            elif quality == 5:
                word_data["ease_factor"] = word_data["ease_factor"] + 0.2
            
            # Cap ease factor
            word_data["ease_factor"] = min(2.5, word_data["ease_factor"])
        
        # Calculate next review date with improved intervals
        if quality == 0 or quality == 1 or quality == 2:
            # Again - review in 4 hours (same day)
            next_review = now + timedelta(hours=4)
        elif quality == 3:
            # Hard - review in 1 day
            next_review = now + timedelta(days=1)
        else:
            # Good/Easy - use calculated interval
            next_review = now + timedelta(days=word_data["interval"])
        
        word_data["next_review"] = next_review.isoformat()
        
        self.save_vocabulary()
        return word_data
    
    def get_stats(self) -> Dict:
        """Get overall statistics"""
        total_words = len(self.vocabulary)
        due_words = len(self.get_due_words())
        total_reviews = sum(word["review_count"] for word in self.vocabulary.values())
        total_correct = sum(word["correct_count"] for word in self.vocabulary.values())
        
        accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0
        
        return {
            "total_words": total_words,
            "due_words": due_words,
            "total_reviews": total_reviews,
            "accuracy": round(accuracy, 1)
        }
    
    def get_upcoming_reviews(self, days_ahead: int = 7) -> List[Dict]:
        """Get words that will be due for review in the next X days"""
        now = datetime.now(self.melbourne_tz)
        end_date = now + timedelta(days=days_ahead)
        upcoming = []
        
        for word_data in self.vocabulary.values():
            next_review = datetime.fromisoformat(word_data["next_review"])
            if now < next_review <= end_date:
                time_until = next_review - now
                upcoming.append({
                    **word_data,
                    "time_until": time_until,
                    "human_readable": self._format_time_interval(time_until)
                })
        
        # Sort by when they're due
        upcoming.sort(key=lambda x: x["time_until"])
        return upcoming

    def get_daily_upcoming_counts(self, days_ahead: int = 7) -> List[Dict]:
        """Get count of words due for review each day in the next X days (Anki-style)"""
        now = datetime.now(self.melbourne_tz)
        daily_counts = []
        
        for day_offset in range(days_ahead + 1):
            target_date = now + timedelta(days=day_offset)
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            count = 0
            for word_data in self.vocabulary.values():
                next_review = datetime.fromisoformat(word_data["next_review"])
                if start_of_day <= next_review < end_of_day:
                    count += 1
            
            # Format the date for display
            if day_offset == 0:
                date_label = "Today"
            elif day_offset == 1:
                date_label = "Tomorrow"
            else:
                date_label = target_date.strftime("%A, %b %d")
            
            daily_counts.append({
                "day_offset": day_offset,
                "date": target_date.isoformat(),
                "date_label": date_label,
                "count": count
            })
        
        return daily_counts
    
    def _format_time_interval(self, time_delta: timedelta) -> str:
        """Convert timedelta to human-readable format"""
        total_seconds = int(time_delta.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds} seconds"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''}"
        elif total_seconds < 604800:  # 7 days
            days = total_seconds // 86400
            return f"{days} day{'s' if days != 1 else ''}"
        elif total_seconds < 2592000:  # 30 days
            weeks = total_seconds // 604800
            return f"{weeks} week{'s' if weeks != 1 else ''}"
        else:
            months = total_seconds // 2592000
            return f"{months} month{'s' if months != 1 else ''}"
    
    def get_next_review_info(self, word_id: str) -> Dict:
        """Get detailed information about when a word will be reviewed next"""
        if word_id not in self.vocabulary:
            raise ValueError("Word not found")
        
        word_data = self.vocabulary[word_id]
        now = datetime.now(self.melbourne_tz)
        next_review = datetime.fromisoformat(word_data["next_review"])
        time_until = next_review - now
        
        return {
            "word": word_data["word"],
            "translation": word_data["translation"],
            "next_review": word_data["next_review"],
            "human_readable": self._format_time_interval(time_until),
            "interval": word_data["interval"],
            "ease_factor": word_data["ease_factor"],
            "review_count": word_data["review_count"],
            "correct_count": word_data["correct_count"],
            "incorrect_count": word_data["incorrect_count"]
        }
    

    
    def search_words(self, query: str) -> List[Dict]:
        """Search words by word, translation, or notes"""
        query = query.lower()
        results = []
        
        for word_data in self.vocabulary.values():
            if (query in word_data["word"].lower() or 
                query in word_data["translation"].lower() or
                query in word_data["notes"].lower()):
                results.append(word_data)
        
        return results
