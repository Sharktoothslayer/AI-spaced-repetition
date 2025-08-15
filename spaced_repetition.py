import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class SpacedRepetition:
    def __init__(self, data_file: str = "vocabulary.json"):
        self.data_file = data_file
        self.vocabulary = self.load_vocabulary()
        
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
    
    def add_word(self, word: str, translation: str, example: str = "", notes: str = "") -> Dict:
        """Add a new word to the vocabulary"""
        word_id = str(int(time.time() * 1000))  # Unique ID based on timestamp
        
        word_data = {
            "id": word_id,
            "word": word,
            "translation": translation,
            "example": example,
            "notes": notes,
            "created": datetime.now().isoformat(),
            "last_reviewed": None,
            "next_review": datetime.now().isoformat(),
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
        now = datetime.now()
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
        now = datetime.now()
        
        # Update review statistics
        word_data["last_reviewed"] = now.isoformat()
        word_data["review_count"] += 1
        
        if quality >= 3:
            word_data["correct_count"] += 1
        else:
            word_data["incorrect_count"] += 1
        
        # Calculate new interval using SuperMemo 2 algorithm
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
        
        # Calculate next review date
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
