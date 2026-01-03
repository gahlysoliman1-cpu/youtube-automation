"""
الثوابت والمتغيرات العامة للمشروع - مُحدث
"""

# إعدادات الفيديو
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_DURATION = 12  # ثانية
BACKGROUND_BLUR_INTENSITY = 15
TEXT_COLOR = (255, 255, 255)  # أبيض
TEXT_SHADOW_COLOR = (0, 0, 0)  # أسود

# إعدادات التوقيت
QUESTION_DISPLAY_TIME = 8  # ثانية
COUNTDOWN_START = 10
ANSWER_DISPLAY_TIME = 2  # ثانية
AUDIO_PROMPT_DELAY = 1  # ثانية

# إعدادات المحتوى
QUESTION_CATEGORIES = [
    "general_knowledge",
    "culture",
    "entertainment",
    "geography",
    "music",
    "history",
    "science"
]

# نماذج الذكاء الاصطناعي بترتيب الأفضلية
AI_MODELS_PRIORITY = [
    "gemini"
]

# عبارات التشجيع
ENCOURAGEMENT_PHRASES = [
    "If you know the answer before the 10 seconds end, write it in the comments!",
    "Think fast! Answer in the comments before time runs out!",
    "Challenge yourself! Comment your answer before the timer ends!",
    "Test your knowledge! Write the answer in comments in 10 seconds!"
]

# إعدادات الرفع على YouTube
YOUTUBE_CATEGORY_ID = "22"  # People & Blogs
YOUTUBE_PRIVACY_STATUS = "public"
YOUTUBE_TAGS_BASE = ["quiz", "shorts", "trivia", "challenge", "test", "knowledge"]

# مسارات الملفات
TEMP_DIR = "temp"
OUTPUT_DIR = "output"
ASSETS_DIR = "assets"
BACKGROUNDS_DIR = f"{ASSETS_DIR}/backgrounds"
FONTS_DIR = f"{ASSETS_DIR}/fonts"
AUDIO_DIR = f"{TEMP_DIR}/audio"
VIDEO_DIR = f"{TEMP_DIR}/video"

# خطوط افتراضية
DEFAULT_FONTS = [
    "Arial",
    "Arial-Bold",
    "DejaVu-Sans",
    "Liberation-Sans",
    "FreeSans"
]
