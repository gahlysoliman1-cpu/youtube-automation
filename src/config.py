"""
Configuration file for YouTube Shorts Automation - UPDATED
"""

import os
from datetime import datetime

# ==================== PATHS ====================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
SHORTS_DIR = os.path.join(VIDEOS_DIR, "shorts")
LONG_VIDEOS_DIR = os.path.join(VIDEOS_DIR, "long_videos")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Create directories
for dir_path in [VIDEOS_DIR, SHORTS_DIR, LONG_VIDEOS_DIR, LOGS_DIR, TEMPLATES_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# ==================== YouTube Config ====================
YOUTUBE_CONFIG = {
    "client_id": os.environ.get("YT_CLIENT_ID_1"),
    "client_secret": os.environ.get("YT_CLIENT_SECRET_1"),
    "refresh_token": os.environ.get("YT_REFRESH_TOKEN_1"),
    "channel_id": os.environ.get("YT_CHANNEL_ID"),
    "token_uri": "https://oauth2.googleapis.com/token",
    "scopes": ["https://www.googleapis.com/auth/youtube.upload"],
    "privacy_status": "public",  # CHANGED FROM 'private' TO 'public'
    "category_id": "22",  # People & Blogs
    "default_language": "en",
}

# ==================== AI Models Config ====================
AI_CONFIG = {
    "gemini_api_key": os.environ.get("GEMINI_API_KEY"),
    "groq_api_key": os.environ.get("GROQ_API_KEY"),
    "openai_api_key": os.environ.get("OPENAI_API_KEY"),
}

# ==================== TTS Config ====================
TTS_CONFIG = {
    "elevenlabs_api_key": os.environ.get("ELEVEN_API_KEY"),
}

# ==================== Video Config ====================
VIDEO_CONFIG = {
    "short": {
        "duration": 22,  # إجمالي مدة الفيديو: 22 ثانية
        "resolution": (1080, 1920),  # 9:16 for Shorts
        "fps": 30,
        "question_duration": 10,  # مدة السؤال
        "countdown_duration": 10,  # مدة العد التنازلي
        "answer_duration": 2,  # مدة ظهور الإجابة
        "background_color": (30, 30, 46),  # لون الخلفية الداكن
        "text_color": (255, 255, 255),  # لون النص الأبيض
        "accent_color": (0, 150, 255),  # لون التمييز الأزرق
    }
}

# ==================== Content Config ====================
CONTENT_CONFIG = {
    "categories": [
        "geography",
        "culture", 
        "history",
        "science",
        "entertainment",
        "sports",
        "technology",
        "music"
    ],
    "fallback_questions": {
        "geography": {
            "question": "Which river is the longest in the world? 🌍",
            "options": ["Amazon River", "Nile River", "Yangtze River", "Mississippi River"],
            "correct_answer": "B",
            "explanation": "The Nile River is approximately 6,650 km long!"
        },
        "culture": {
            "question": "What is the traditional dress of Scotland called? 🏴󠁧󠁢󠁳󠁣󠁴󠁿",
            "options": ["Kilt", "Kimono", "Sari", "Dirndl"],
            "correct_answer": "A",
            "explanation": "The kilt is a knee-length skirt with pleats!"
        },
        "history": {
            "question": "In which year did World War II end? ⚔️",
            "options": ["1943", "1944", "1945", "1946"],
            "correct_answer": "C",
            "explanation": "WWII ended in 1945!"
        },
        "science": {
            "question": "What is the chemical symbol for gold? ⚛️",
            "options": ["Go", "Gd", "Au", "Ag"],
            "correct_answer": "C",
            "explanation": "Au comes from 'aurum' meaning gold!"
        }
    }
}

# ==================== Prompts ====================
PROMPTS = {
    "question_generation": """
    Generate ONE engaging multiple-choice trivia question for YouTube Shorts.
    
    REQUIREMENTS:
    - Category: {category}
    - Make it FUN and ENGAGING
    - Add relevant emoji to the question
    - Include 4 clear options (A, B, C, D)
    - Mark ONE correct answer
    - Add short exciting explanation (max 10 words)
    
    FORMAT:
    Question: [Question with emoji]
    A) [Option 1]
    B) [Option 2]
    C) [Option 3]
    D) [Option 4]
    Correct: [Letter]
    Explanation: [Short exciting explanation with emoji!]
    
    Example:
    Question: Which planet is known as the Red Planet? 🪐
    A) Venus
    B) Mars
    C) Jupiter
    D) Saturn
    Correct: B
    Explanation: Mars is red due to iron oxide! 🔴
    """,
    
    "title_generation": """
    Create a VIRAL YouTube Shorts title for this trivia:
    Question: {question}
    
    Requirements:
    - MAX 50 characters
    - Include 1-2 relevant emojis
    - Make it clickable and engaging
    - Add #shorts at the end
    
    Examples:
    "Can you answer this? 🤔 #shorts"
    "Geography quiz challenge! 🌍 #shorts"
    "Test your knowledge! 🧠 #shorts"
    """,
    
    "description_generation": """
    Create YouTube description for this Short:
    
    Question: {question}
    Category: {category}
    
    Include:
    - Engaging challenge text
    - Call to comment
    - Subscribe reminder
    - Relevant hashtags
    
    Format:
    Can you answer this {category} question? 😊
    
    {question}
    
    👉 Write your answer in comments before the timer ends!
    
    Subscribe for daily quizzes!
    Like if you enjoy trivia! ❤️
    
    #shorts #quiz #trivia #challenge #{category}
    """
}
