# AI Spaced Repetition Language Learning System

A sophisticated language learning application that combines AI-powered conversation with spaced repetition algorithms to help users learn Italian (or any language) effectively.

## 🚀 Features

### Core Functionality
- **AI Language Tutor**: Interactive chat with Ollama-powered AI that adapts to your vocabulary level
- **Spaced Repetition System**: Implements SuperMemo 2 algorithm for optimal learning intervals
- **Vocabulary Management**: Add, edit, and organize words with automatic translation
- **Review System**: Scheduled reviews with quality-based interval adjustments
- **Learning Modes**: 
  - **Strict Mode**: AI uses only words you've already learned
  - **Learning Mode**: AI introduces 1-5 new words per conversation

### Advanced Features
- **Smart Translation**: AI + Google Translate fallback with context awareness
- **Progress Tracking**: Comprehensive statistics and learning analytics
- **Review Forecasting**: 7-day preview of upcoming reviews
- **Word Type Detection**: Automatic categorization of words (noun, verb, adjective, etc.)
- **Example Generation**: Context-aware example sentences for new words

## 🏗️ Architecture

### Backend (Flask)
- **Flask Web Framework**: RESTful API with CORS support
- **Ollama Integration**: Local AI model for language tutoring
- **JSON Storage**: Simple file-based vocabulary persistence
- **Modular Design**: Separated concerns for maintainability

### Frontend (Vanilla JavaScript)
- **Single Page Application**: Tab-based navigation
- **Responsive Design**: Mobile-first approach with modern UI
- **Real-time Updates**: Dynamic content loading and state management
- **Component-based**: Modular JavaScript for each feature

### Spaced Repetition Algorithm
- **SuperMemo 2 Implementation**: Industry-standard spaced repetition
- **Adaptive Intervals**: Adjusts based on user performance
- **Quality-based Scheduling**: 0-5 rating system with intelligent intervals
- **Timezone Support**: Melbourne timezone handling for accurate scheduling

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Ollama installed and running locally
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd AI-spaced-repetition
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your settings
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2:3b-instruct-q4_K_M
   DEBUG_LOGS=1
   ```

4. **Start Ollama and load your model**
   ```bash
   ollama serve
   ollama pull llama3.2:3b-instruct-q4_K_M
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open `http://localhost:5000` in your browser
   - The AI tutor will greet you in Italian!

### Docker Setup (Alternative)
```bash
docker-compose up -d
```

## 📖 Usage Guide

### Getting Started

1. **First Conversation**
   - Start with Learning Mode (default)
   - Chat naturally in Italian
   - AI will introduce new words gradually

2. **Adding New Words**
   - When new words appear (highlighted in red), click "Add New Words"
   - Review translations and examples
   - Confirm to add to your vocabulary

3. **Review System**
   - Navigate to the Review tab
   - Review words when they're due
   - Rate your performance (0-5) to adjust intervals

### Learning Modes

#### Learning Mode (Default)
- AI introduces 1-5 new words per conversation
- Best for expanding vocabulary
- New words are highlighted and can be added

#### Strict Mode
- AI uses only words you've already learned
- Perfect for practicing known vocabulary
- No new words introduced

### Vocabulary Management

#### Adding Words
- **Automatic**: From AI conversations
- **Manual**: Use the Vocabulary tab
- **AI-Assisted**: Automatic translation and example generation

#### Word Information
- **Translation**: English equivalent
- **Example**: Context sentence
- **Word Type**: Part of speech
- **Notes**: Additional information
- **Review Schedule**: Next review date

### Review System

#### Quality Ratings
- **0-1 (Again)**: Review in 4 hours
- **2 (Hard)**: Review in 1 day  
- **3 (Good)**: Use calculated interval
- **4-5 (Easy)**: Extended intervals

#### Scheduling Algorithm
- **SuperMemo 2**: Industry-standard spaced repetition
- **Adaptive**: Adjusts based on your performance
- **Ease Factor**: Tracks word difficulty over time

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2:3b-instruct-q4_K_M` | AI model to use |
| `DEBUG_LOGS` | `1` | Enable debug logging |

### Ollama Settings

#### Chat Options
```python
OLLAMA_OPTIONS_CHAT = {
    'num_ctx': 2048,        # Context window
    'num_thread': 10,       # CPU threads
    'num_predict': 80,      # Response length
    'temperature': 0.7,     # Creativity level
    'top_p': 0.9,          # Nucleus sampling
}
```

#### Translation Options
```python
OLLAMA_OPTIONS_XLATE = {
    'num_ctx': 2048,
    'num_thread': 10,
    'num_predict': 32,      # Shorter for translations
    'temperature': 0.0,     # Deterministic
}
```

## 🏛️ Modularization Guide

### Current Structure Issues
- **`app.py`**: 548 lines - too large, mixed concerns
- **`spaced_repetition.py`**: 412 lines - manageable but could be split
- **`templates/index.html`**: 2835 lines - extremely large, needs separation

### Recommended Modular Structure

#### Backend Modules
```
src/
├── main.py                 # Entry point (50 lines)
├── config/
│   ├── settings.py         # Configuration (100 lines)
│   └── constants.py        # Constants (50 lines)
├── api/routes/
│   ├── chat.py             # Chat endpoints (150 lines)
│   ├── spaced_repetition.py # SR endpoints (200 lines)
│   └── translation.py      # Translation endpoints (100 lines)
├── services/
│   ├── chat_service.py     # Chat logic (120 lines)
│   ├── translation_service.py # Translation logic (80 lines)
│   └── ollama_service.py   # Ollama integration (60 lines)
└── utils/
    ├── text_processing.py  # Text utilities (40 lines)
    └── logging.py          # Logging (30 lines)
```

#### Frontend Modules
```
static/
├── css/
│   ├── main.css           # Base styles (200 lines)
│   ├── components/        # Component styles (4 files, ~300 lines each)
│   └── layout/            # Layout styles (2 files, ~150 lines each)
├── js/
│   ├── main.js            # Main initialization (100 lines)
│   ├── modules/           # Feature modules (5 files, ~200 lines each)
│   └── utils/             # Utilities (2 files, ~100 lines each)
└── templates/              # HTML components (5 files, ~200 lines each)
```

### Modularization Benefits
- **Maintainability**: Easier to find and fix issues
- **Testability**: Individual modules can be tested separately
- **Collaboration**: Multiple developers can work on different modules
- **Reusability**: Components can be reused across projects
- **Performance**: Better code splitting and caching

## 🧪 Testing

### Backend Testing
```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

### Frontend Testing
```bash
# Run JavaScript tests
npm test

# Run with coverage
npm run test:coverage
```

## 🚀 Deployment

### Production Setup
```bash
# Use Gunicorn for production
gunicorn -w 2 -k gthread -b 0.0.0.0:5000 src.main:app

# Or use Docker
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Configuration
```bash
# Production environment
export FLASK_ENV=production
export DEBUG_LOGS=0
export OLLAMA_BASE_URL=https://your-ollama-server.com
```

## 📊 Performance Considerations

### Backend Optimization
- **Connection Pooling**: Reuse HTTP sessions
- **Caching**: LRU cache for translations
- **Async Processing**: Background Ollama warmup
- **Response Validation**: Two-pass AI response validation

### Frontend Optimization
- **Lazy Loading**: Load tab content on demand
- **Debounced Search**: Optimize vocabulary search
- **Efficient DOM**: Minimal DOM manipulation
- **Memory Management**: Clear unused references

## 🔒 Security Features

- **CORS Protection**: Configurable origin restrictions
- **Input Validation**: Sanitized user inputs
- **Rate Limiting**: Built-in request throttling
- **Error Handling**: Secure error messages

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Follow the modular structure
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- **Python**: PEP 8 compliance
- **JavaScript**: ESLint configuration
- **CSS**: BEM methodology
- **Documentation**: Inline and README updates

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama**: Local AI model hosting
- **SuperMemo**: Spaced repetition algorithm
- **Flask**: Web framework
- **Italian Language Community**: Testing and feedback

## 📞 Support

For questions, issues, or contributions:
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: [Your Email]

---

**Happy Learning! 🎓🇮🇹**
