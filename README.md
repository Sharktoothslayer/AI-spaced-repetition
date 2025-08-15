# AI Language Learning Chat

A minimal, clean web interface for chatting with AI models via Ollama, designed as the foundation for a spaced repetition language learning system.

## Features

- Clean, modern chat interface
- Integration with Ollama AI models
- Responsive design
- Docker support for easy deployment

## Prerequisites

- Docker and Docker Compose installed
- Ollama running locally (or accessible via network)
- A language model pulled in Ollama (e.g., `llama3.2`)

## Quick Start

1. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```

2. **Pull a model** (if not already done):
   ```bash
   ollama pull llama3.2
   ```

3. **Build and run the application**:
   ```bash
   docker-compose up --build
   ```

4. **Access the chat interface** at `http://localhost:5000`

## Configuration

The application can be configured via environment variables:

- `OLLAMA_BASE_URL`: URL where Ollama is running (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: Model name to use (default: `llama3.2`)

## Development

To run locally without Docker:

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Flask app:
   ```bash
   python app.py
   ```

## Docker Deployment

The application is containerized and ready for deployment on Unraid or any Docker-compatible system. The Dockerfile uses Python 3.11 slim image for optimal size and performance.

## Next Steps

This is the foundation for your AI-powered spaced repetition system. Future enhancements could include:

- User authentication and session management
- Vocabulary database integration
- Spaced repetition algorithms
- Progress tracking
- Multiple language support

## Architecture

- **Frontend**: Pure HTML/CSS/JavaScript with modern design
- **Backend**: Flask Python server
- **AI Integration**: Ollama API for model communication
- **Containerization**: Docker for easy deployment 