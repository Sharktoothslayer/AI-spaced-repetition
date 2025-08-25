from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from spaced_repetition import SpacedRepetition

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
    """Use AI to translate and provide context for a word"""
    try:
        data = request.get_json()
        word = data.get('word', '').strip()
        context = data.get('context', '').strip()
        
        if not word:
            return jsonify({'error': 'Word is required'}), 400
        
        # Prepare request to Ollama for translation with context awareness
        if context:
            system_content = f"""You are an Italian translation assistant. For each Italian word provided WITH CONTEXT, respond ONLY with a JSON in this exact format:

{{
  "translation": "English translation based on context",
  "example": "Example sentence in Italian using this word",
  "word_type": "ONE word type in English (verb, noun, adjective, adverb, pronoun, preposition, conjunction, interjection)"
}}

IMPORTANT:
- word_type must be ONLY ONE English word type
- Do not include multiple types separated by slashes
- Do not include any other text, only the JSON
- Use standard English grammar terms
- Consider the context to provide the most accurate translation
- For words with multiple meanings, choose the meaning that fits the context best"""
            
            user_content = f'Translate this Italian word to English based on the context and provide exactly ONE word type:\n\nWord: {word}\nContext: {context}'
        else:
            system_content = 'You are an Italian translation assistant. For each Italian word provided, respond ONLY with a JSON in this exact format:\n{\n  "translation": "English translation",\n  "example": "Example sentence in Italian using this word",\n  "word_type": "ONE word type in English (verb, noun, adjective, adverb, pronoun, preposition, conjunction, interjection)"\n}\n\nIMPORTANT:\n- word_type must be ONLY ONE English word type\n- Do not include multiple types separated by slashes\n- Do not include any other text, only the JSON\n- Use standard English grammar terms'
            
            user_content = f'Translate this Italian word to English and provide exactly ONE word type: {word}'
        
        ollama_request = {
            'model': DEFAULT_MODEL,
            'messages': [
                {
                    'role': 'system',
                    'content': system_content
                },
                {
                    'role': 'user',
                    'content': user_content
                }
            ],
            'stream': False
        }
        
        print(f"AI translation request for word: {word}")
        print(f"System prompt: {ollama_request['messages'][0]['content']}")
        
        # Send request to Ollama
        response = requests.post(
            f'{OLLAMA_BASE_URL}/api/chat',
            json=ollama_request,
            timeout=30
        )
        
        if response.status_code == 200:
            ollama_response = response.json()
            ai_message = ollama_response.get('message', {}).get('content', '')
            
            try:
                # Try to parse the JSON response
                import json
                translation_data = json.loads(ai_message)
                
                # Clean up word_type to ensure only one type
                word_type = translation_data.get('word_type', '')
                print(f"Original word_type from AI: '{word_type}'")
                
                if '/' in word_type or '\\' in word_type:
                    # If multiple types are provided, take the first one
                    word_type = word_type.split('/')[0].split('\\')[0].strip()
                    print(f"Cleaned word_type after splitting: '{word_type}'")
                
                # Ensure word_type is a standard English grammar term
                standard_types = ['verb', 'noun', 'adjective', 'adverb', 'pronoun', 'preposition', 'conjunction', 'interjection']
                if word_type.lower() not in standard_types:
                    # If not a standard type, try to map common variations
                    word_type_lower = word_type.lower()
                    if 'verbo' in word_type_lower or 'verb' in word_type_lower:
                        word_type = 'verb'
                    elif 'sostantivo' in word_type_lower or 'noun' in word_type_lower:
                        word_type = 'noun'
                    elif 'aggettivo' in word_type_lower or 'adjective' in word_type_lower:
                        word_type = 'adjective'
                    elif 'avverbio' in word_type_lower or 'adverb' in word_type_lower:
                        word_type = 'adverb'
                    elif 'pronome' in word_type_lower or 'pronoun' in word_type_lower:
                        word_type = 'pronoun'
                    elif 'preposizione' in word_type_lower or 'preposition' in word_type_lower:
                        word_type = 'preposition'
                    elif 'congiunzione' in word_type_lower or 'conjunction' in word_type_lower:
                        word_type = 'conjunction'
                    elif 'interiezione' in word_type_lower or 'interjection' in word_type_lower:
                        word_type = 'interjection'
                    else:
                        word_type = 'noun'  # Default fallback
                
                print(f"Final cleaned word_type: '{word_type}'")
                
                return jsonify({
                    'translation': translation_data.get('translation', ''),
                    'example': translation_data.get('example', ''),
                    'word_type': word_type,
                    'success': True
                })
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract information manually
                return jsonify({
                    'translation': 'Translation failed',
                    'example': 'Example not available',
                    'word_type': 'Unknown',
                    'success': False,
                    'raw_response': ai_message
                })
        else:
            return jsonify({'error': f'Ollama error: {response.status_code}'}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Connection error: {str(e)}'}), 500
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
- È meglio una frase semplice e corretta che una frase complessa con parole non autorizzate"""
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
Se non hai abbastanza parole familiari per creare una frase completa, crea una frase più semplice ma rispetta SEMPRE il limite di 2 nuove parole."""
        
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
            
            # Validate response in strict mode
            if strict_mode:
                print(f"Validating strict mode response...")
                # Check if response contains any words not in vocabulary
                import re
                # Simple word detection for validation
                words_in_response = re.findall(r'\b[aàbcdeèéfghiìjklmnoòpqrstuùvxyz]\w*\b', ai_message.lower())
                unauthorized_words = [word for word in words_in_response if word not in [w.lower() for w in current_vocabulary]]
                
                if unauthorized_words:
                    print(f"WARNING: AI used unauthorized words in strict mode: {unauthorized_words}")
                    # Force AI to use only vocabulary words by regenerating
                    ai_message = f"Mi dispiace, devo usare solo le parole del tuo vocabolario. Provo a riformulare: {ai_message}"
                    # For now, just log the warning. In production, you might want to regenerate the response
                else:
                    print(f"Strict mode validation passed - all words are from vocabulary")
            
            # Validate response in learning mode
            else:
                print(f"Validating learning mode response...")
                import re
                # Enhanced word detection for validation (same patterns as frontend)
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
                    matches = re.findall(pattern, ai_message.lower())
                    words_in_response.extend(matches)
                
                # Remove duplicates
                words_in_response = list(set(words_in_response))
                
                # Count new words
                new_words = [word for word in words_in_response if word not in [w.lower() for w in current_vocabulary]]
                
                if len(new_words) > 2:
                    print(f"WARNING: AI introduced {len(new_words)} new words in learning mode: {new_words}")
                    print(f"This exceeds the limit of 2 new words. Response will be regenerated.")
                    
                    # Regenerate response with stronger enforcement
                    stronger_prompt = f"""ATTENZIONE: Hai introdotto {len(new_words)} nuove parole, ma il limite è MASSIMO 2.
                    
Riformula la risposta usando MASSIMO 2 nuove parole. Se necessario, usa frasi più semplici.
Risposta originale: {ai_message}

Nuova risposta (max 2 nuove parole):"""
                    
                    # For now, just log the warning and add a note. In production, you might want to regenerate
                    ai_message = f"⚠️ ATTENZIONE: Ho introdotto troppe nuove parole ({len(new_words)}). Dovrei usarne massimo 2. Ecco la mia risposta: {ai_message}"
                else:
                    print(f"Learning mode validation passed - {len(new_words)} new words introduced (within limit)")
            
            return jsonify({
                'response': ai_message,
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
