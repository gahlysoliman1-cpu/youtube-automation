"""
Configuration file for YouTube Shorts Automation
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
    "scopes": ["https://www.googleapis.com/auth/youtube.upload"],
    "privacy_status": "private",  # private/public/unlisted
    "category_id": "22",  # People & Blogs
    "default_language": "en",
}

# ==================== AI Models Config ====================
AI_CONFIG = {
    "primary": {
        "name": "gemini",
        "api_key": os.environ.get("GEMINI_API_KEY"),
        "model": "gemini-1.5-pro",
        "fallback_order": ["gemini", "groq", "openai"]
    },
    "secondary": {
        "name": "groq",
        "api_key": os.environ.get("GROQ_API_KEY"),
        "model": "mixtral-8x7b-32768",
    },
    "tertiary": {
        "name": "openai",
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "model": "gpt-3.5-turbo",
    }
}

# ==================== TTS Config ====================
TTS_CONFIG = {
    "primary": {
        "name": "elevenlabs",
        "api_key": os.environ.get("ELEVEN_API_KEY"),
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
        "fallback_order": ["elevenlabs", "gtts"]
    },
    "secondary": {
        "name": "gtts",
        "language": "en",
        "tld": "com"
    }
}

# ==================== Video Config ====================
VIDEO_CONFIG = {
    "short": {
        "duration": 15,  # seconds
        "resolution": (1080, 1920),  # 9:16 for Shorts
        "fps": 30,
        "background_blur": 10,
        "text_duration": 10,
        "countdown_duration": 10,
        "answer_duration": 2
    },
    "long": {
        "duration": 60,  # seconds (compilation)
        "resolution": (1920, 1080),
        "fps": 30
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
    "difficulty": "medium",
    "language": "English",
    "max_questions_per_day": 4,
    "question_formats": [
        "Which {thing} is {description}?",
        "What is the {attribute} of {subject}?",
        "Can you name {number} {things}?",
        "Guess the {subject} from {hint}",
        "What {thing} is known for {characteristic}?"
    ]
}

# ==================== URLs for Media Fallback ====================
MEDIA_FALLBACK_URLS = {
    "backgrounds": [
        "https://images.pexels.com/photos",
        "https://images.unsplash.com/photo",
        "https://cdn.pixabay.com/photo"
    ],
    "sounds": [
        "https://freesound.org/data/previews",
        "https://assets.mixkit.co/music/preview"
    ]
}

# ==================== Prompts ====================
PROMPTS = {
    "question_generation": """
    Generate an engaging multiple-choice trivia question with the following requirements:
    
    1. Category: {category}
    2. Difficulty: {difficulty}
    3. Question should be clear and concise
    4. Include 4 options (A, B, C, D)
    5. Mark the correct answer
    6. Add a brief interesting fact about the answer
    
    Format:
    Question: [Your question here]
    Options:
    A) [Option 1]
    B) [Option 2]
    C) [Option 3]
    D) [Option 4]
    Correct Answer: [Letter]
    Explanation: [Brief explanation]
    
    Make it fun and educational!
    """,
    
    "title_generation": """
    Generate a catchy YouTube Shorts title for this trivia question:
    Question: {question}
    
    Requirements:
    - Under 60 characters
    - Include emoji
    - Encourage engagement
    - Add #shorts hashtag
    
    Example: "Can you answer this? 🌍 #shorts"
    """,
    
    "description_generation": """
    Write a YouTube description for this trivia short:
    
    Question: {question}
    Correct Answer: {correct_answer}
    
    Include:
    - Challenge text
    - Call to comment
    - Subscribe prompt
    - Relevant hashtags
    
    Format:
    Can you answer this {category} question? 😊
    
    {question}
    
    👉 Write your answer in comments before the timer ends!
    
    Subscribe for daily quizzes!
    #shorts #quiz #trivia #challenge #{category}
    """
}

# ==================== Logging ====================
LOG_FILE = os.path.join(LOGS_DIR, f"youtube_shorts_{datetime.now().strftime('%Y%m%d')}.log")
