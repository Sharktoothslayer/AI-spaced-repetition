# Spaced Repetition System

This app now includes a complete spaced repetition system similar to Anki, designed specifically for language learning.

## Features

### 📚 **Vocabulary Management**
- **Add Words**: Click the "+ Add Word" button to add new vocabulary
- **Delete Words**: Remove words you no longer need
- **Search**: Find words quickly using the search bar
- **Examples & Notes**: Add context and personal notes to each word

### 🔄 **Review System**
- **Anki-style Cards**: Review words with front/back card interface
- **Quality Ratings**: Rate your recall from 0-3 (Again, Hard, Good, Easy)
- **Smart Scheduling**: Uses SuperMemo 2 algorithm for optimal intervals
- **Due Words**: Shows how many words are ready for review

### 📊 **Statistics**
- **Total Words**: Track your vocabulary size
- **Words Due**: See how many need review
- **Total Reviews**: Monitor your study activity
- **Accuracy**: Track your learning progress

## How It Works

### **Spaced Repetition Algorithm**
The system uses the **SuperMemo 2 algorithm**:
- **Correct answers** increase intervals (1 day → 6 days → 12+ days)
- **Incorrect answers** reset intervals and adjust difficulty
- **Ease factor** adapts to your learning pace

### **Quality Rating System**
- **0 (Again)**: Complete blackout - reset to 1 day
- **1 (Hard)**: Difficult but remembered - reset to 1 day
- **2 (Good)**: Correct response - normal progression
- **3 (Easy)**: Very easy - faster progression

## Usage

### **Adding Words**
1. Go to **Vocabulary** tab
2. Click **"+ Add Word"**
3. Enter: word, translation, example (optional), notes (optional)

### **Reviewing Words**
1. Go to **Review** tab
2. Click **"Show Answer"** to see translation
3. Rate your recall with quality buttons
4. System automatically schedules next review

### **Tracking Progress**
1. Go to **Stats** tab
2. View your learning statistics
3. Monitor accuracy and review counts

## Data Storage

- **Vocabulary**: Stored in `vocabulary.json`
- **Progress**: Automatically saved after each review
- **Backup**: Data persists between app restarts

## Future Integration

This spaced repetition system is designed to integrate with the AI tutor:
- **AI can suggest new words** based on conversations
- **Context-aware learning** from chat interactions
- **Personalized vocabulary building** based on your interests

## Technical Details

- **Backend**: Python Flask with spaced repetition algorithms
- **Frontend**: Modern HTML/CSS/JavaScript with tabbed interface
- **Storage**: JSON-based with automatic persistence
- **API**: RESTful endpoints for all CRUD operations

---

**Ready to start learning?** Add your first word and begin building your Italian vocabulary! 🇮🇹
