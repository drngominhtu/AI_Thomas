# AI Thomas Assistant

An AI-powered desktop assistant with speech recognition and weather information features.

## Features
- Voice interaction
- Weather information
- Real-time chat with AI
- Text-to-speech responses
- Dynamic AI face expressions

## Setup
1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Copy `config.example.py` to `config.py` and add your API keys
4. Run: `python ai_assistant.py`

## Build
To create standalone executable:
```bash
pyinstaller --onefile --windowed ai_assistant.py
```

## Configuration
You need to obtain API keys for:
- DeepSeekr API
- Weather API

## Author
Dr.ngominhtu