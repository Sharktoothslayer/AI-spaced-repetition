from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from spaced_repetition import SpacedRepetition
import re

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["*"], methods=["GET", "POST"], allow_headers=["Content-Type"])

# Initialize spaced repetition system
sr_system = SpacedRepetition()

# Ollama configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
DEFAULT_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test')
def test():
    return jsonify({'status': 'ok', 'message': 'Backend is working'})

# Spaced Repetition API endpoints
@app.route('/api/sr/words', methods=['GET'])
def get_words():
    """Get all vocabulary words"""
    try:
        words = sr_system.get_all_words()
        return jsonify({'words': words})
    except Exception as e:
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
        
        # Use free Google Translate (no API key required)
        try:
            google_url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'it',
                'tl': 'en',
                'dt': 't',
                'q': word
            }
            
            response = requests.get(google_url, params=params, timeout=15)
            if response.status_code == 200:
                # Parse Google Translate response
                data = response.json()
                if data and len(data) > 0 and len(data[0]) > 0:
                    english_translation = data[0][0][0]
                    if english_translation and english_translation != word:
                        print(f"  🌐 Google Translate: {word} -> {english_translation}")
                        
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
            
            # If Google Translate fails, fall back to basic translation
            return jsonify({
                'translation': f'[Italian: {word}]',
                'example': f'Esempio con {word}.',
                'word_type': 'noun',
                'success': False,
                'error': 'Translation failed'
            })
                
        except Exception as e:
            # Fallback to basic translation
            return jsonify({
                'translation': f'[Italian: {word}]',
                'example': f'Esempio con {word}.',
                'word_type': 'noun',
                'success': False,
                'error': f'Translation service unavailable: {str(e)}'
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
            system_content = f"""Sei un tutor di italiano amichevole. Rispondi SEMPRE in italiano usando SOLO le parole che lo studente conosce già: {', '.join(current_vocabulary)}

Regole semplici:
- Risposte brevi (massimo 10 parole)
- Usa SOLO parole dal vocabolario fornito
- Se non puoi esprimere qualcosa, usa frasi più semplici
- Sii naturale e incoraggiante"""
        else:
            # Learning mode: MAX 5 new words per sentence, prioritize word limits over sentence completion
            system_content = f"""Sei un tutor di italiano amichevole. Aiuta lo studente a imparare parlando naturalmente.

Regole semplici:
- Risposte brevi (massimo 10 parole)
- Usa principalmente parole che lo studente conosce: {', '.join(current_vocabulary)}
- Introduci 0-5 nuove parole quando necessario
- Sii naturale e incoraggiante
- Frasi semplici sono meglio di frasi complesse"""
        
        # Function to validate and potentially regenerate response
        def validate_and_regenerate_response(initial_response, mode, max_attempts=3):
            for attempt in range(max_attempts):
                print(f"Validation attempt {attempt + 1} for {mode} mode")
                
                # Enhanced word detection patterns (same as frontend)
                patterns = [
                    r'\b[aàbcdeèéfghiìjklmnoòpqrstuùvxyz]\w*\b',
                    r'\b[aàbcdeèéfghiìjklmnoòpqrstuùvxyz]\b',
                    r'\b[aàbcdeèéfghiìjklmnoòpqrstuùvxyz]\'[aàbcdeèéfghiìjklmnoòpqrstuùvxyz]\w*\b',
                    r'\b[aàbcdeèéfghiìjklmnoòpqrstuùvxyz][aàbcdeèéfghiìjklmnoòpqrstuùvxyz]\b',
                    r'\b[àèéìòù]\b',
                    r'\b[aàbcdeèéfghiìjklmnoòpqrstuùvxyz]{1,2}\b'
                ]
                
                words_in_response = []
                for pattern in patterns:
                    matches = re.findall(pattern, initial_response.lower())
                    words_in_response.extend(matches)
                
                # Remove duplicates and filter out very short words that might be false positives
                words_in_response = list(set([w for w in words_in_response if len(w) >= 2]))
                
                if mode == 'strict':
                    # Check for unauthorized words
                    unauthorized_words = [word for word in words_in_response if word not in [w.lower() for w in current_vocabulary]]
                    
                    if unauthorized_words:
                        print(f"WARNING: Found {len(unauthorized_words)} unauthorized words: {unauthorized_words}")
                        if attempt < max_attempts - 1:
                            # Regenerate with stronger enforcement
                            stronger_prompt = f"""Rispondi di nuovo in italiano, massimo 10 parole, usando SOLO parole autorizzate: {', '.join(current_vocabulary)}"""
                            
                            # Send regeneration request
                            regen_request = {
                                'model': DEFAULT_MODEL,
                                'messages': [
                                    {'role': 'system', 'content': system_content},
                                    {'role': 'user', 'content': f"{message}\n\n{stronger_prompt}"}
                                ],
                                'stream': False
                            }
                            
                            regen_response = requests.post(
                                f'{OLLAMA_BASE_URL}/api/chat',
                                json=regen_request,
                                timeout=30
                            )
                            
                            if regen_response.status_code == 200:
                                regen_data = regen_response.json()
                                initial_response = regen_data.get('message', {}).get('content', initial_response)
                                print(f"Regenerated response attempt {attempt + 1}")
                                continue
                            else:
                                print(f"Failed to regenerate response: {regen_response.status_code}")
                                break
                        else:
                            # Final attempt failed, return original response without warning
                            break
                    else:
                        print(f"Strict mode validation passed - all words are from vocabulary")
                        break
                        
                else:  # Learning mode
                    # Count new words
                    new_words = [word for word in words_in_response if word not in [w.lower() for w in current_vocabulary]]
                    
                    if len(new_words) > 5:
                        print(f"WARNING: AI introduced {len(new_words)} new words: {new_words}")
                        if attempt < max_attempts - 1:
                            # Regenerate with stronger enforcement
                            stronger_prompt = f"""Rispondi di nuovo in italiano, massimo 10 parole, massimo 5 nuove parole:"""
                            
                            # Send regeneration request
                            regen_request = {
                                'model': DEFAULT_MODEL,
                                'messages': [
                                    {'role': 'system', 'content': system_content},
                                    {'role': 'user', 'content': f"{message}\n\n{stronger_prompt}"}
                                ],
                                'stream': False
                            }
                            
                            regen_response = requests.post(
                                f'{OLLAMA_BASE_URL}/api/chat',
                                json=regen_request,
                                timeout=30
                            )
                            
                            if regen_response.status_code == 200:
                                regen_data = regen_response.json()
                                initial_response = regen_data.get('message', {}).get('content', initial_response)
                                print(f"Regenerated response attempt {attempt + 1}")
                                continue
                            else:
                                print(f"Failed to regenerate response: {regen_response.status_code}")
                                break
                        else:
                            # Final attempt failed, return original response without warning
                            break
                    else:
                        print(f"Learning mode validation passed - {len(new_words)} new words introduced (within limit)")
                        break
            
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
                    'content': f"{message}\n\n{'⚠️ Usa SOLO parole dal vocabolario!' if strict_mode else '⚠️ Massimo 5 nuove parole per risposta'}"
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
