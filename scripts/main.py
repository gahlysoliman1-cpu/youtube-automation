import os
import json
import random
import time
import logging
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from ai_utils import generate_question_with_fallback, generate_tts_with_fallback
from video_utils import create_short_video, create_compilation_video
from youtube_utils import upload_to_youtube, get_authenticated_service
from config import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_history():
    history_file = os.environ.get('HISTORY_FILE', 'history.json')
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"questions": [], "last_run": None}

def save_history(history):
    history_file = os.environ.get('HISTORY_FILE', 'history.json')
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def is_duplicate(question, history):
    return any(q['question'] == question for q in history['questions'])

def generate_unique_question(history):
    max_attempts = 10
    for attempt in range(max_attempts):
        result = generate_question_with_fallback()
        if not result:
            continue
            
        question = result['question'].strip()
        answer = result['answer'].strip()
        
        if not is_duplicate(question, history):
            return {'question': question, 'answer': answer}
        
        logger.warning(f"Duplicate question detected (attempt {attempt+1}/{max_attempts}): {question}")
        time.sleep(1)
    
    raise Exception(f"Failed to generate unique question after {max_attempts} attempts")

def process_shorts(config, history, shorts_dir):
    shorts = []
    for i in range(4):
        logger.info(f"Generating Short #{i+1}")
        short_data = generate_unique_question(history)
        
        tts_path = os.path.join(shorts_dir, f"tts_{i}.mp3")
        generate_tts_with_fallback(short_data['question'], tts_path)
        
        output_path = os.path.join(shorts_dir, f"short_{i}.mp4")
        create_short_video(
            short_data['question'],
            short_data['answer'],
            tts_path,
            output_path,
            config['background_image']
        )
        
        shorts.append({
            'path': output_path,
            'title': f"Can You Answer This? 😱 #{i+1}",
            'description': f"Question: {short_data['question']}\nAnswer revealed after 10 seconds!",
            'tags': ['quiz', 'riddle', 'brainteaser', 'shorts']
        })
        
        history['questions'].append({
            'question': short_data['question'],
            'answer': short_data['answer'],
            'timestamp': datetime.utcnow().isoformat()
        })
        
        time.sleep(2)  # Rate limiting
    
    return shorts

def main():
    try:
        config = load_config()
        history = load_history()
        
        # Anti-duplicate logic - skip if already ran today
        today = datetime.utcnow().date().isoformat()
        if history.get('last_run') == today:
            logger.info("Already ran today. Skipping execution.")
            return
        
        shorts_dir = os.environ.get('SHORTS_DIR', 'shorts')
        compilation_dir = os.environ.get('COMPILATION_DIR', 'compilations')
        os.makedirs(shorts_dir, exist_ok=True)
        os.makedirs(compilation_dir, exist_ok=True)
        
        shorts = process_shorts(config, history, shorts_dir)
        
        # Create compilation video
        compilation_path = os.path.join(compilation_dir, f"compilation_{today.replace('-', '')}.mp4")
        create_compilation_video([s['path'] for s in shorts], compilation_path)
        
        # Upload to YouTube
        youtube = get_authenticated_service()
        
        # Upload shorts
        for short in shorts:
            upload_to_youtube(
                youtube,
                short['path'],
                short['title'],
                short['description'],
                short['tags'],
                is_short=True
            )
            time.sleep(15)  # Avoid quota issues
        
        # Upload compilation
        upload_to_youtube(
            youtube,
            compilation_path,
            f"Daily Quiz Compilation - {today}",
            "Watch all today's quizzes in one video!",
            ['quiz', 'compilation', 'daily', 'brainteaser'],
            is_short=False
        )
        
        history['last_run'] = today
        save_history(history)
        
        logger.info("Successfully completed daily automation")
    except Exception as e:
        logger.exception(f"Critical failure: {str(e)}")
        raise

if __name__ == "__main__":
    main()
