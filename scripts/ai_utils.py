import os
import json
import requests
import logging
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

API_TIMEOUT = 30
MAX_RETRIES = 3

class AIFailure(Exception):
    pass

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type((requests.exceptions.RequestException, AIFailure)))
def call_groq_api(prompt):
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        raise AIFailure("GROQ_API_KEY not set")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
    response.raise_for_status()
    
    data = response.json()
    if 'choices' not in data or not data['choices']:
        raise AIFailure("Invalid Groq response structure")
    
    content = data['choices'][0]['message']['content'].strip()
    return parse_qa_response(content)

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type((requests.exceptions.RequestException, AIFailure)))
def call_gemini_api(prompt):
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise AIFailure("GEMINI_API_KEY not set")
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 150,
            "topP": 0.8,
            "topK": 40
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
    response.raise_for_status()
    
    data = response.json()
    if 'candidates' not in data or not data['candidates']:
        raise AIFailure("Invalid Gemini response structure")
    
    content = data['candidates'][0]['content']['parts'][0]['text'].strip()
    return parse_qa_response(content)

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type((requests.exceptions.RequestException, AIFailure)))
def call_openrouter_api(prompt):
    api_key = os.environ.get('OPENROUTER_KEY')
    if not api_key:
        raise AIFailure("OPENROUTER_KEY not set")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/yourusername/yt-automation",
        "X-Title": "YouTube Shorts Automation",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "anthropic/claude-3-haiku",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
    response.raise_for_status()
    
    data = response.json()
    if 'choices' not in data or not data['choices']:
        raise AIFailure("Invalid OpenRouter response structure")
    
    content = data['choices'][0]['message']['content'].strip()
    return parse_qa_response(content)

def parse_qa_response(content):
    try:
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if len(lines) < 2:
            raise ValueError("Response has fewer than 2 lines")
        
        question = lines[0].replace("Question:", "").strip()
        answer = lines[1].replace("Answer:", "").strip()
        
        if not question or not answer:
            raise ValueError("Missing question or answer")
        
        return {"question": question, "answer": answer}
    except Exception as e:
        logger.error(f"Parsing error: {str(e)} | Content: {content}")
        raise AIFailure(f"Failed to parse response: {str(e)}")

def generate_question_with_fallback():
    prompt = """Generate one challenging general knowledge question for a YouTube Short. 
    Format EXACTLY as:
    Question: [Your question here]
    Answer: [Correct answer here]
    
    Requirements:
    - Question must be culturally neutral and suitable for international audience
    - Answer must be 1-3 words maximum
    - NO additional text or explanations
    - Examples:
        Question: What is the capital of Australia?
        Answer: Canberra
        Question: How many players are on a standard soccer team?
        Answer: 11
    """
    
    models = [
        ("groq", call_groq_api),
        ("gemini", call_gemini_api),
        ("openrouter", call_openrouter_api)
    ]
    
    for model_name, api_call in models:
        try:
            logger.info(f"Trying {model_name} for question generation")
            return api_call(prompt)
        except Exception as e:
            logger.warning(f"{model_name} failed: {str(e)}")
            time.sleep(1)
    
    logger.error("All AI models failed for question generation")
    raise AIFailure("All question generation models failed")

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type((requests.exceptions.RequestException, AIFailure)))
def generate_elevenlabs_tts(text, output_path):
    api_key = os.environ.get('ELEVEN_API_KEY')
    if not api_key:
        raise AIFailure("ELEVEN_API_KEY not set")
    
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": f"{text}\nIf you know the answer before the 10 seconds end, write it in the comments!",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        },
        "model_id": "eleven_multilingual_v2"
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    return output_path

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type((requests.exceptions.RequestException, AIFailure)))
def generate_openai_tts(text, output_path):
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise AIFailure("OPENAI_API_KEY not set")
    
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "tts-1-hd",
        "voice": "alloy",
        "input": f"{text}\nIf you know the answer before the 10 seconds end, write it in the comments!",
        "response_format": "mp3"
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=API_TIMEOUT)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    return output_path

def generate_tts_with_fallback(text, output_path):
    tts_services = [
        ("elevenlabs", lambda: generate_elevenlabs_tts(text, output_path)),
        ("openai", lambda: generate_openai_tts(text, output_path))
    ]
    
    for service_name, tts_call in tts_services:
        try:
            logger.info(f"Trying {service_name} for TTS")
            result = tts_call()
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                return result
        except Exception as e:
            logger.warning(f"{service_name} TTS failed: {str(e)}")
            if os.path.exists(output_path):
                os.remove(output_path)
            time.sleep(1)
    
    logger.error("All TTS services failed")
    raise AIFailure("All text-to-speech services failed")
