from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Ollama configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
DEFAULT_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Prepare request to Ollama
        ollama_request = {
            'model': DEFAULT_MODEL,
            'messages': [
                {
                    'role': 'user',
                    'content': message
                }
            ],
            'stream': False
        }
        
        # Send request to Ollama
        response = requests.post(
            f'{OLLAMA_BASE_URL}/api/chat',
            json=ollama_request,
            timeout=30
        )
        
        if response.status_code == 200:
            ollama_response = response.json()
            ai_message = ollama_response.get('message', {}).get('content', 'Sorry, I could not generate a response.')
            
            return jsonify({
                'response': ai_message,
                'model': DEFAULT_MODEL
            })
        else:
            return jsonify({'error': f'Ollama error: {response.status_code}'}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Connection error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 