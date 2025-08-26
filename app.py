from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from spaced_repetition import SpacedRepetition
import re
import json

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["*"], methods=["GET", "POST"], allow_headers=["Content-Type"])

# Initialize spaced repetition system
sr_system = SpacedRepetition("vocabulary.json")  # Use relative path for Docker volume persistence

# Check if vocabulary file exists and initialize if needed
def ensure_vocabulary_file():
    """Ensure vocabulary file exists and has basic structure"""
    try:
        import os
        if not os.path.exists("vocabulary.json"):
            print("📝 Creating new vocabulary.json file")
            with open("vocabulary.json", "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            print("✅ Vocabulary file created successfully")
        else:
            print(f"📁 Vocabulary file exists: {os.path.getsize('vocabulary.json')} bytes")
    except Exception as e:
        print(f"❌ Error ensuring vocabulary file: {e}")

# Initialize vocabulary file
ensure_vocabulary_file()

# Ollama configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
DEFAULT_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')

# Free translation API (LibreTranslate)
LIBRE_TRANSLATE_URL = "https://libretranslate.de/translate"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test')
def test():
    return jsonify({'status': 'ok', 'message': 'Backend is working'})

@app.route('/api/debug/vocabulary')
def debug_vocabulary():
    """Debug endpoint to check vocabulary status"""
    try:
        import os
        file_exists = os.path.exists("vocabulary.json")
        file_size = os.path.getsize("vocabulary.json") if file_exists else 0
        
        words = sr_system.get_all_words()
        word_count = len(words)
        
        return jsonify({
            'status': 'ok',
            'file_exists': file_exists,
            'file_size': file_size,
            'word_count': word_count,
            'sample_words': [w['word'] for w in words[:10]] if words else [],
            'data_file_path': sr_system.data_file
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

# Spaced Repetition API endpoints
@app.route('/api/sr/words', methods=['GET'])
def get_words():
    """Get all vocabulary words"""
    try:
        print(f"🔍 Loading vocabulary from: {sr_system.data_file}")
        words = sr_system.get_all_words()
        print(f"📚 Loaded {len(words)} words from vocabulary")
        print(f"📝 First few words: {[w['word'] for w in words[:5]] if words else 'None'}")
        return jsonify({'words': words})
    except Exception as e:
        print(f"❌ Error loading vocabulary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/words', methods=['POST'])
def add_word():
    """Add a new word to vocabulary"""
    try:
        data = request.get_json()
        word = data.get('word', '').strip()
        translation = data.get('translation', '').strip()
        example = data.get('example', '').strip()
        word_type = data.get('word_type', '').strip()
        notes = data.get('notes', '').strip()
        
        if not word or not translation:
            return jsonify({'error': 'Word and translation are required'}), 400
        
        word_data = sr_system.add_word(word, translation, example, word_type, notes)
        return jsonify({'word': word_data, 'message': 'Word added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/ai-translate', methods=['POST'])
def ai_translate():
    """Use free translation API to translate and provide context for a word"""
    try:
        data = request.get_json()
        word = data.get('word', '').strip()
        context = data.get('context', '').strip()
        
        if not word:
            return jsonify({'error': 'Word is required'}), 400
        
        # Use LibreTranslate (free) instead of AI
        try:
            # First, get the English translation
            translation_response = requests.post(
                LIBRE_TRANSLATE_URL,
                json={
                    'q': word,
                    'source': 'it',
                    'target': 'en',
                    'format': 'text'
                },
                timeout=10
            )
            
            if translation_response.status_code == 200:
                translation_data = translation_response.json()
                english_translation = translation_data.get('translatedText', '')
                
                # Simple word type detection based on common patterns
                word_type = 'noun'  # default
                
                # Common Italian word endings and patterns
                if word.endswith(('are', 'ere', 'ire')):
                    word_type = 'verb'
                elif word.endswith(('o', 'a', 'e', 'i')):
                    if word.endswith(('o', 'a')):
                        word_type = 'adjective'
                    else:
                        word_type = 'noun'
                elif word in ['di', 'a', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra']:
                    word_type = 'preposition'
                elif word in ['e', 'o', 'ma', 'se', 'che', 'perché']:
                    word_type = 'conjunction'
                elif word in ['io', 'tu', 'lui', 'lei', 'noi', 'voi', 'loro', 'mi', 'ti', 'ci', 'vi']:
                    word_type = 'pronoun'
                elif word in ['molto', 'poco', 'bene', 'male', 'qui', 'là', 'oggi', 'ieri']:
                    word_type = 'adverb'
                elif word in ['ciao', 'ehi', 'oh', 'ah', 'ecco']:
                    word_type = 'interjection'
                
                # Generate a simple example sentence
                if word_type == 'verb':
                    example = f"Voglio {word}." if word.endswith('are') else f"Devo {word}."
                elif word_type == 'noun':
                    example = f"Questo è un {word}."
                elif word_type == 'adjective':
                    example = f"È molto {word}."
                else:
                    example = f"Uso {word} spesso."
                
                return jsonify({
                    'translation': english_translation,
                    'example': example,
                    'word_type': word_type,
                    'success': True
                })
            else:
                return jsonify({
                    'translation': 'Translation failed',
                    'example': 'Example not available',
                    'word_type': 'noun',
                    'success': False,
                    'error': 'Translation service unavailable'
                })
                
        except requests.exceptions.RequestException:
            # Fallback to basic translation
            return jsonify({
                'translation': f'[Italian: {word}]',
                'example': f'Esempio con {word}.',
                'word_type': 'noun',
                'success': False,
                'error': 'Translation service unavailable'
            })
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/sr/words/<word_id>', methods=['DELETE'])
def delete_word(word_id):
    """Delete a word from vocabulary"""
    try:
        success = sr_system.delete_word(word_id)
        if success:
            return jsonify({'message': 'Word deleted successfully'})
        else:
            return jsonify({'error': 'Word not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/due', methods=['GET'])
def get_due_words():
    """Get words that are due for review (including overdue)"""
    try:
        due_words = sr_system.get_due_words()
        return jsonify({'words': due_words})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/overdue', methods=['GET'])
def get_overdue_words():
    """Get only overdue words"""
    try:
        overdue_words = sr_system.get_overdue_words()
        return jsonify({'words': overdue_words})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/review', methods=['POST'])
def review_word():
    """Review a word with quality rating"""
    try:
        data = request.get_json()
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
    """Get spaced repetition statistics"""
    try:
        stats = sr_system.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/upcoming', methods=['GET'])
def get_upcoming_reviews():
    """Get upcoming reviews in the next 7 days"""
    try:
        days_ahead = request.args.get('days', 7, type=int)
        upcoming = sr_system.get_upcoming_reviews(days_ahead)
        return jsonify({'upcoming': upcoming})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/daily-upcoming', methods=['GET'])
def get_daily_upcoming_counts():
    """Get daily counts of upcoming reviews (Anki-style)"""
    try:
        days_ahead = request.args.get('days', 7, type=int)
        daily_counts = sr_system.get_daily_upcoming_counts(days_ahead)
        return jsonify({'daily_counts': daily_counts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/words/<word_id>/next-review', methods=['GET'])
def get_word_next_review(word_id):
    """Get detailed information about when a word will be reviewed next"""
    try:
        review_info = sr_system.get_next_review_info(word_id)
        return jsonify(review_info)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/words/<word_id>/review-preview', methods=['GET'])
def get_word_review_preview(word_id):
    """Get preview of what each review option will do"""
    try:
        preview = sr_system.get_review_preview(word_id)
        return jsonify({'preview': preview})
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sr/search', methods=['GET'])
def search_words():
    """Search words by query"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        results = sr_system.search_words(query)
        return jsonify({'words': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        print(f"Received chat request")
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        message = data.get('message', '')
        strict_mode = data.get('strict_mode', False)
        current_vocabulary = data.get('current_vocabulary', [])
        
        print(f"Message: {message}")
        print(f"Strict mode: {strict_mode}")
        print(f"Current vocabulary size: {len(current_vocabulary)}")
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Prepare the system prompt based on mode
        if strict_mode:
            # Strict mode: ONLY use vocabulary words - NO EXCEPTIONS
            system_content = f"""Sei un tutor di italiano in modalità VOCABOLARIO STRETTO. 

REGOLE ASSOLUTE E INVIOLABILI:
1. Rispondi SEMPRE in italiano, usando un linguaggio naturale ma corretto
2. Mantieni le risposte brevi (1-2 frasi massimo) e conversazionali
3. Puoi usare SOLO e ESCLUSIVAMENTE queste parole: {', '.join(current_vocabulary)}
4. Sii incoraggiante e non troppo formale, ma sempre grammaticalmente corretto

VOCABOLARIO DISPONIBILE: {', '.join(current_vocabulary)}

IMPORTANTE: 
- NON puoi usare NESSUNA parola che non sia in questa lista
- Se devi esprimere qualcosa ma non hai le parole giuste, riformula usando SOLO il vocabolario fornito
- Se non riesci a esprimere un concetto con le parole disponibili, usa sinonimi o riformula completamente
- NON introdurre mai nuove parole in modalità stretta
- Se la frase non può essere completata con le parole disponibili, usa frasi più semplici o incomplete
- È meglio una frase semplice e corretta che una frase complessa con parole non autorizzate

RICORDA: SOLO le parole fornite. NESSUNA eccezione."""
        else:
            # Learning mode: MAX 2 new words per sentence, prioritize word limits over sentence completion
            system_content = f"""Sei un tutor di italiano in modalità APPRENDIMENTO. Il tuo ruolo è:
1. Rispondi sempre in italiano, usando un linguaggio naturale ma corretto
2. Mantieni le risposte brevi (1-2 frasi massimo) e conversazionali
3. Usa PRINCIPALMENTE parole dal vocabolario dello studente: {', '.join(current_vocabulary)}
4. Introduci MASSIMO 2 NUOVE parole italiane per risposta che NON sono nel vocabolario
5. Sii incoraggiante e non troppo formale, ma sempre grammaticalmente corretto

REGOLE ASSOLUTE E INVIOLABILI:
- MASSIMO 2 nuove parole per risposta - NON MAI DI PIÙ
- Se non puoi completare una frase con solo 2 nuove parole, usa frasi più semplici
- È meglio una frase semplice e corretta che una frase complessa con troppe parole nuove
- Priorità ASSOLUTA: Rispetta il limite di 2 nuove parole > Completare la frase
- Se devi scegliere tra una frase completa con 3+ nuove parole o una frase semplice con 2 nuove parole, scegli SEMPRE la seconda opzione
- Usa principalmente parole familiari dal vocabolario fornito

Strategia: Usa principalmente parole familiari, ma introduci naturalmente 1-2 nuove parole per risposta.
Rendi le nuove parole contestualmente chiare così lo studente può capirle dal contesto.
Se non hai abbastanza parole familiari per creare una frase completa, crea una frase più semplice ma rispetta SEMPRE il limite di 2 nuove parole.

RICORDA: MASSIMO 2 nuove parole. NESSUNA eccezione."""
        
        # Function to validate and potentially regenerate response
        def validate_and_regenerate_response(initial_response, mode, max_attempts=3):
            """Validate response and regenerate if it violates rules"""
            print(f"🔍 Validating response in {mode} mode: {initial_response}")
            
            # Count Italian words in response
            italian_words = []
            # Comprehensive Italian word detection patterns
            patterns = [
                r'\b[aàeèéiìoòuù][aàeèéiìoòuù]*\b',  # Single vowels
                r'\b[aàeèéiìoòuù][bcdfghjklmnpqrstvwxyz][aàeèéiìoòuù]*\b',  # Vowel-consonant-vowel
                r'\b[bcdfghjklmnpqrstvwxyz][aàeèéiìoòuù][bcdfghjklmnpqrstvwxyz]*\b',  # Consonant-vowel-consonant
                r'\b[bcdfghjklmnpqrstvwxyz][aàeèéiìoòuù][aàeèéiìoòuù]*\b',  # Consonant-vowel-vowel
                r'\b[aàeèéiìoòuù][bcdfghjklmnpqrstvwxyz][bcdfghjklmnpqrstvwxyz]*\b',  # Vowel-consonant-consonant
                r'\b[bcdfghjklmnpqrstvwxyz][bcdfghjklmnpqrstvwxyz][aàeèéiìoòuù]*\b'  # Consonant-consonant-vowel
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, initial_response, re.IGNORECASE)
                italian_words.extend(matches)
            
            # Remove duplicates and filter out very short words
            italian_words = list(set([word.lower() for word in italian_words if len(word) >= 2]))
            
            print(f"🔍 Found {len(italian_words)} Italian words: {italian_words}")
            
            if mode == 'strict':
                # In strict mode, ALL words must be in vocabulary
                unauthorized_words = [word for word in italian_words if word not in [w.lower() for w in current_vocabulary]]
                if unauthorized_words:
                    print(f"❌ Strict mode violation: {unauthorized_words} not in vocabulary")
                    if max_attempts > 1:
                        print(f"🔄 Regenerating response (attempts left: {max_attempts-1})")
                        return "regenerate"
                    else:
                        print("⚠️ Final attempt failed, adding warning")
                        return f"⚠️ ATTENZIONE: Non sono riuscito a rispettare la modalità vocabolario stretto. Ecco la mia risposta: {initial_response}"
                
            elif mode == 'learning':
                # In learning mode, MAX 2 new words per response
                new_words = [word for word in italian_words if word not in [w.lower() for w in current_vocabulary]]
                if len(new_words) > 2:
                    print(f"❌ Learning mode violation: {len(new_words)} new words (max 2 allowed)")
                    if max_attempts > 1:
                        print(f"🔄 Regenerating response (attempts left: {max_attempts-1})")
                        return "regenerate"
                    else:
                        print("⚠️ Final attempt failed, adding warning")
                        return f"⚠️ ATTENZIONE: Non sono riuscito a rispettare il limite di 2 nuove parole. Ecco la mia risposta: {initial_response}"
            
            print("✅ Response validation passed")
            return initial_response
        
        # Prepare request to Ollama with vocabulary-aware system prompt
        ollama_request = {
            'model': DEFAULT_MODEL,
            'messages': [
                {
                    'role': 'system',
                    'content': system_content
                },
                {
                    'role': 'user',
                    'content': f"{message}\n\n{'⚠️ RICORDA: Usa SOLO le parole del vocabolario fornito!' if strict_mode else '⚠️ RICORDA: MASSIMO 2 nuove parole per risposta! Se necessario, usa frasi più semplici.'}"
                }
            ],
            'stream': False
        }
        
        print(f"Ollama request: {ollama_request}")
        print(f"Attempting to connect to Ollama at: {OLLAMA_BASE_URL}")
        
        # Send request to Ollama
        response = requests.post(
            f'{OLLAMA_BASE_URL}/api/chat',
            json=ollama_request,
            timeout=30
        )
        
        print(f"Ollama response status: {response.status_code}")
        print(f"Ollama response: {response.text}")
        
        if response.status_code == 200:
            ollama_response = response.json()
            ai_message = ollama_response.get('message', {}).get('content', 'Sorry, I could not generate a response.')
            
            # Validate and potentially regenerate response
            final_response = validate_and_regenerate_response(
                ai_message, 
                'strict' if strict_mode else 'learning'
            )
            
            # If validation suggests regeneration, try again
            if final_response == "regenerate":
                print("🔄 Attempting to regenerate response...")
                # Try one more time with stronger prompt
                stronger_prompt = f"""ATTENZIONE CRITICA: 

REGOLE ASSOLUTE E INVIOLABILI:
{'Usa SOLO queste parole: ' + ', '.join(current_vocabulary) if strict_mode else 'MASSIMO 2 nuove parole per risposta. Priorità ASSOLUTA: Rispetta il limite > Completare la frase'}

Se necessario, usa frasi più semplici o riformula completamente.

Rispondi di nuovo:"""
                
                regen_request = {
                    'model': DEFAULT_MODEL,
                    'messages': [
                        {'role': 'system', 'content': system_content},
                        {'role': 'user', 'content': f"{message}\n\n{stronger_prompt}"}
                    ],
                    'stream': False
                }
                
                try:
                    regen_response = requests.post(
                        f'{OLLAMA_BASE_URL}/api/chat',
                        json=regen_request,
                        timeout=30
                    )
                    
                    if regen_response.status_code == 200:
                        regen_data = regen_response.json()
                        final_response = regen_data.get('message', {}).get('content', ai_message)
                        print("✅ Response regenerated successfully")
                    else:
                        print(f"❌ Failed to regenerate: {regen_response.status_code}")
                        final_response = ai_message
                except Exception as e:
                    print(f"❌ Error during regeneration: {e}")
                    final_response = ai_message
            
            return jsonify({
                'response': final_response,
                'model': DEFAULT_MODEL
            })
        else:
            return jsonify({'error': f'Ollama error: {response.status_code} - {response.text}'}), 500
            
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {str(e)}")
        return jsonify({'error': f'Connection error: {str(e)}'}), 500
    except Exception as e:
        print(f"General exception: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
