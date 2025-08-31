# app.py
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from spaced_repetition import SpacedRepetition
import re
from functools import lru_cache

# -----------------------------
# Boot / Config
# -----------------------------
load_dotenv()

app = Flask(__name__)

# EDIT ME: Restrict to your real front-end origins for production
CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://your-frontend.example.com"
]}})

DEBUG_LOGS = os.getenv("DEBUG_LOGS", "1") == "1"
def log(msg: str):
    if DEBUG_LOGS:
        print(msg)

# Single shared HTTP session (connection reuse = faster)
SESSION = requests.Session()
DEFAULT_TIMEOUT = (5, 90)  # (connect, read)

# Spaced Repetition system
sr_system = SpacedRepetition()

# Ollama configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
# Fast CPU-friendly quant by default
DEFAULT_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b-instruct-q4_K_M')

# Per-request options for Ollama
OLLAMA_OPTIONS_CHAT = {
    'num_ctx': 2048,
    'num_thread': 10,
    'num_predict': 80,  # headroom for 1–2 short sentences
    'stop': ['\n\n', '\n- ', '\n• ', '— ', 'Translation:', 'Traduzione:'],
    'temperature': 0.7,
    'top_p': 0.9,
}
OLLAMA_OPTIONS_XLATE = {
    'num_ctx': 2048,
    'num_thread': 10,
    'num_predict': 32,  # single-word/short gloss
    'temperature': 0.0,  # deterministic
}

# Compact system prompts (short = faster + more consistent)
STRICT_SYS = (
    "Sei un tutor di italiano. Rispondi SOLO con parole nel vocabolario fornito. "
    "Massimo 10 parole. Sii naturale e incoraggiante."
)
LEARN_SYS = (
    "Sei un tutor di italiano. Risposte brevi (≤10 parole), principalmente dal vocabolario; "
    "introduci al massimo 5 parole nuove. Sii naturale e incoraggiante."
)

# Italian-ish word tokenizer (includes accents and apostrophes)
ITALIAN_WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ’']+", re.UNICODE)

def extract_words(text: str):
    return [w.lower() for w in ITALIAN_WORD_RE.findall(text or "")]

def check_words(text: str, vocab_lower_set: set):
    words = extract_words(text)
    new_words = [w for w in words if w not in vocab_lower_set]
    return words, new_words

def tidy(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    if s and s[-1] not in ".?!…":
        s += "."
    return s

# -----------------------------
# Views
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test')
def test():
    return jsonify({'status': 'ok', 'message': 'Backend is working'})

# -----------------------------
# Translation helpers
# -----------------------------
@lru_cache(maxsize=4096)
def google_translate_it_en_raw(word: str):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {'client': 'gtx', 'sl': 'it', 'tl': 'en', 'dt': 't', 'q': word}
    r = SESSION.get(url, params=params, timeout=(3, 8))
    r.raise_for_status()
    return r.json()

def get_ai_translation(word, context=""):
    """Get AI-powered translation for a word using Ollama"""
    try:
        log(f"🤖 Getting AI translation for: {word}")
        prompt = (
            f'Traduci questa parola italiana in inglese: "{word}"\n\n'
            f"Contesto: {context if context else 'Nessun contesto specifico'}\n\n"
            "Fornisci SOLO la traduzione in inglese, nient'altro."
        )
        ai_request = {
            'model': DEFAULT_MODEL,
            'messages': [
                {'role': 'system', 'content': "Sei un traduttore italiano-inglese. Rispondi solo con la traduzione."},
                {'role': 'user', 'content': prompt}
            ],
            'options': OLLAMA_OPTIONS_XLATE,
            'stream': False
        }
        resp = SESSION.post(f'{OLLAMA_BASE_URL}/api/chat', json=ai_request, timeout=DEFAULT_TIMEOUT)
        if resp.status_code == 200:
            ai_response = resp.json()
            ai_translation = (ai_response.get('message', {}) or {}).get('content', '').strip()
            ai_translation = ai_translation.replace('"', '').replace("'", "").strip()
            log(f"🤖 AI translation: {word} -> {ai_translation}")
            return ai_translation
        log(f"❌ AI translation failed: {resp.status_code} {resp.text}")
        return None
    except Exception as e:
        log(f"💥 AI translation error: {str(e)}")
        return None

# -----------------------------
# Spaced Repetition API
# -----------------------------
@app.route('/api/sr/words', methods=['GET'])
def get_words():
    try:
        words = sr_system.get_all_words()
        return jsonify({'words': words})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/words', methods=['POST'])
def add_word():
    try:
        data = request.get_json(force=True)
        word = (data.get('word') or '').strip()
        translation = (data.get('translation') or '').strip()
        example = (data.get('example') or '').strip()
        word_type = (data.get('word_type') or '').strip()
        notes = (data.get('notes') or '').strip()

        if not word or not translation:
            return jsonify({'error': 'Word and translation are required'}), 400

        word_data = sr_system.add_word(word, translation, example, word_type, notes)
        return jsonify({'word': word_data, 'message': 'Word added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/ai-translate', methods=['POST'])
def ai_translate():
    """Use Google Translate (free endpoint) with fallbacks"""
    try:
        data = request.get_json(force=True)
        word = (data.get('word') or '').strip()
        context = (data.get('context') or '').strip()
        if not word:
            return jsonify({'error': 'Word is required'}), 400

        # First try Google (quick)
        try:
            raw = google_translate_it_en_raw(word)
            all_translations = []
            if raw and len(raw) > 0 and isinstance(raw[0], list):
                for block in raw[0]:
                    if block and len(block) > 0 and isinstance(block[0], str):
                        eng = block[0]
                        if eng and eng.lower() != word.lower() and eng not in all_translations:
                            all_translations.append(eng)
            if all_translations:
                english_translation = ", ".join(all_translations[:3])

                # quick heuristic word type
                wt = 'noun'
                if word.endswith(('are', 'ere', 'ire', 'ato', 'uto', 'ito')):
                    wt = 'verb'
                elif word.endswith(('ante', 'ente')):
                    wt = 'adjective'
                elif any(word.endswith(p) for p in ['ti','mi','lo','la','li','le','ci','vi','si','ne']):
                    # verb + pronoun combos
                    wt = 'verb'
                elif word in ['di','a','da','in','con','su','per','tra','fra']:
                    wt = 'preposition'
                elif word in ['e','o','ma','se','che','perché']:
                    wt = 'conjunction'
                elif word in ['io','tu','lui','lei','noi','voi','loro','mi','ti','ci','vi']:
                    wt = 'pronoun'
                elif word in ['molto','poco','bene','male','qui','là','oggi','ieri']:
                    wt = 'adverb'
                elif word in ['ciao','ehi','oh','ah','ecco']:
                    wt = 'interjection'
                elif word.endswith(('o','a')):
                    wt = 'adjective'
                else:
                    wt = 'noun'

                if wt == 'verb':
                    if word.endswith(('ato','uto','ito')):
                        example = f"Ho {word} ieri."
                    elif word.endswith(('are','ere','ire')):
                        example = f"Voglio {word}."
                    elif any(word.endswith(p) for p in ['ti','mi','lo','la','li','le','ci','vi','si','ne']):
                        example = f"Posso {word}."
                    else:
                        example = f"Devo {word}."
                elif wt == 'noun':
                    example = f"Questo è un {word}."
                elif wt == 'adjective':
                    example = f"È molto {word}."
                else:
                    example = f"Uso {word} spesso."

                return jsonify({
                    'translation': english_translation,
                    'example': example,
                    'word_type': wt,
                    'success': True,
                    'all_translations': all_translations
                })

        except Exception as e:
            log(f"💥 Google Translate exception: {e}")

        # If Google fails, fallback AI or stub
        ai_translation = get_ai_translation(word, context)
        if ai_translation:
            return jsonify({
                'translation': ai_translation,
                'example': f"Esempio con {word}.",
                'word_type': 'noun',
                'success': True,
                'source': 'ai'
            })

        # final fallback
        return jsonify({
            'translation': f'[Italian: {word}]',
            'example': f'Esempio con {word}.',
            'word_type': 'noun',
            'success': False,
            'error': 'Translation failed'
        })

    except Exception as e:
        log(f"💥 Server error in ai_translate: {e}")
        return jsonify({'error': f'Server error: {e}'}), 500

@app.route('/api/sr/ai-translate-word', methods=['POST'])
def ai_translate_word():
    try:
        data = request.get_json(force=True)
        word = (data.get('word') or '').strip()
        context = (data.get('context') or '').strip()
        if not word:
            return jsonify({'error': 'Word is required'}), 400

        log(f"🤖 AI translation request for: {word}")
        ai_translation = get_ai_translation(word, context)
        if ai_translation:
            return jsonify({'translation': ai_translation, 'source': 'ai', 'success': True})
        return jsonify({'error': 'AI translation failed', 'success': False}), 500

    except Exception as e:
        log(f"💥 Server error in ai_translate_word: {e}")
        return jsonify({'error': f'Server error: {e}'}), 500

@app.route('/api/sr/words/<word_id>', methods=['DELETE'])
def delete_word(word_id):
    try:
        success = sr_system.delete_word(word_id)
        if success:
            return jsonify({'message': 'Word deleted successfully'})
        return jsonify({'error': 'Word not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/due', methods=['GET'])
def get_due_words():
    try:
        due_words = sr_system.get_due_words()
        return jsonify({'words': due_words})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/overdue', methods=['GET'])
def get_overdue_words():
    try:
        overdue_words = sr_system.get_overdue_words()
        return jsonify({'words': overdue_words})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/review', methods=['POST'])
def review_word():
    try:
        data = request.get_json(force=True)
        word_id = data.get('word_id')
        quality = data.get('quality')
        if word_id is None or quality is None:
            return jsonify({'error': 'word_id and quality are required'}), 400
        if not isinstance(quality, int) or quality < 0 or quality > 5:
            return jsonify({'error': 'Quality must be an integer between 0 and 5'}), 400

        word_data = sr_system.review_word(word_id, quality)
        return jsonify({'word': word_data, 'message': 'Review completed'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/stats', methods=['GET'])
def get_stats():
    try:
        stats = sr_system.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/upcoming', methods=['GET'])
def get_upcoming_reviews():
    try:
        days_ahead = request.args.get('days', 7, type=int)
        upcoming = sr_system.get_upcoming_reviews(days_ahead)
        return jsonify({'upcoming': upcoming})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/daily-upcoming', methods=['GET'])
def get_daily_upcoming_counts():
    try:
        days_ahead = request.args.get('days', 7, type=int)
        daily_counts = sr_system.get_daily_upcoming_counts(days_ahead)
        return jsonify({'daily_counts': daily_counts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/words/<word_id>/next-review', methods=['GET'])
def get_word_next_review(word_id):
    try:
        review_info = sr_system.get_next_review_info(word_id)
        return jsonify(review_info)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/words/<word_id>/review-preview', methods=['GET'])
def get_word_review_preview(word_id):
    try:
        preview = sr_system.get_review_preview(word_id)
        return jsonify({'preview': preview})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -----------------------------
# Chat endpoint (Ollama)
# -----------------------------
def validate_and_regenerate_response(initial_response: str, mode: str, message: str, system_content: str, current_vocabulary):
    """Two-pass validation; strict: enforce vocab, learning: limit new words."""
    response = initial_response or ""
    vocab_lower = {w.lower() for w in (current_vocabulary or [])}

    for attempt in range(2):
        words_in_response, new_words = check_words(response, vocab_lower)
        log(f"Validation attempt {attempt+1} ({mode}) | words={len(words_in_response)} | new={len(new_words)}")

        if mode == 'strict':
            if new_words:
                if attempt == 0:
                    regen_request = {
                        'model': DEFAULT_MODEL,
                        'messages': [
                            {'role': 'system', 'content': system_content + "\n\nRegola assoluta: usa solo parole del vocabolario."},
                            {'role': 'user', 'content': message}
                        ],
                        'options': OLLAMA_OPTIONS_CHAT,
                        'stream': False
                    }
                    resp = SESSION.post(f'{OLLAMA_BASE_URL}/api/chat', json=regen_request, timeout=DEFAULT_TIMEOUT)
                    if resp.ok:
                        response = (resp.json().get('message', {}) or {}).get('content', response)
                        continue
                # last resort: filter to allowed words (≤10)
                allowed = [w for w in words_in_response if w in vocab_lower][:10]
                response = " ".join(allowed) if allowed else "Non posso rispondere con altre parole."
            break

        else:  # learning
            if len(new_words) > 5:
                if attempt == 0:
                    regen_request = {
                        'model': DEFAULT_MODEL,
                        'messages': [
                            {'role': 'system', 'content': system_content + "\n\nMassimo 5 parole nuove."},
                            {'role': 'user', 'content': message}
                        ],
                        'options': OLLAMA_OPTIONS_CHAT,
                        'stream': False
                    }
                    resp = SESSION.post(f'{OLLAMA_BASE_URL}/api/chat', json=regen_request, timeout=DEFAULT_TIMEOUT)
                    if resp.ok:
                        response = (resp.json().get('message', {}) or {}).get('content', response)
                        continue
            break

    return tidy(response)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        log("Received chat request")
        data = request.get_json(force=True)
        log(f"Request data: {data}")

        message = (data.get('message') or '').strip()
        strict_mode = bool(data.get('strict_mode', False))
        current_vocabulary = data.get('current_vocabulary') or []

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        system_content = (STRICT_SYS if strict_mode else LEARN_SYS)
        if current_vocabulary:
            system_content += f"\nVocabolario: {', '.join(current_vocabulary)}"

        user_tail = '⚠️ Solo vocabolario!' if strict_mode else '⚠️ Max 5 parole nuove'
        ollama_request = {
            'model': DEFAULT_MODEL,
            'messages': [
                {'role': 'system', 'content': system_content},
                {'role': 'user', 'content': f"{message}\n\n{user_tail}"}
            ],
            'options': OLLAMA_OPTIONS_CHAT,
            'stream': False
        }

        log(f"Attempting to connect to Ollama at: {OLLAMA_BASE_URL}")
        resp = SESSION.post(f'{OLLAMA_BASE_URL}/api/chat', json=ollama_request, timeout=DEFAULT_TIMEOUT)
        log(f"Ollama response status: {resp.status_code}")

        if not resp.ok:
            return jsonify({'error': f'Ollama error: {resp.status_code} - {resp.text}'}), 500

        ai_message = (resp.json().get('message', {}) or {}).get('content', '') or ''
        final_response = validate_and_regenerate_response(
            ai_message,
            'strict' if strict_mode else 'learning',
            message,
            system_content,
            current_vocabulary
        )

        return jsonify({'response': final_response, 'model': DEFAULT_MODEL})

    except requests.exceptions.RequestException as e:
        log(f"Request exception: {e}")
        return jsonify({'error': f'Connection error: {e}'}), 502
    except Exception as e:
        log(f"General exception: {e}")
        return jsonify({'error': f'Server error: {e}'}), 500

# -----------------------------
# Entrypoint
# -----------------------------
if __name__ == '__main__':
    # For production, run with gunicorn instead:
    # gunicorn -w 4 -k gthread -b 0.0.0.0:5000 app:app
    app.run(debug=True, host='0.0.0.0', port=5000)
