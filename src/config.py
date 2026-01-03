"""
إعدادات التكوين والمتغيرات البيئية - النسخة المطورة
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class Config:
    """فئة تخزين إعدادات التكوين"""
    
    # API Keys الأساسية
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    eleven_api_key: Optional[str] = None
    
    # API Keys للخلفيات
    pexels_api_key: Optional[str] = None
    unsplash_access_key: Optional[str] = None
    
    # YouTube API Keys
    youtube_api_key: Optional[str] = None
    youtube_channel_id: Optional[str] = None
    youtube_client_id: Optional[str] = None
    youtube_client_secret: Optional[str] = None
    youtube_refresh_token: Optional[str] = None
    
    # APIs احتياطية
    camb_ai_key: Optional[str] = None
    replicate_api_token: Optional[str] = None
    hf_api_token: Optional[str] = None
    
    # إعدادات التشغيل
    max_retries: int = 3
    timeout: int = 30
    daily_shorts_count: int = 4
    enable_fallback: bool = True
    upload_to_youtube: bool = True
    debug_mode: bool = False
    
    # إعدادات الدقة
    use_low_quality: bool = False  # لتقليل استخدام الموارد
    
    @classmethod
    def from_env(cls):
        """تحميل الإعدادات من متغيرات البيئة مع قيم افتراضية"""
        return cls(
            # الأساسية
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            eleven_api_key=os.getenv("ELEVEN_API_KEY", ""),
            
            # الخلفيات
            pexels_api_key=os.getenv("PEXELS_API_KEY", ""),
            unsplash_access_key=os.getenv("UNSPLASH_ACCESS_KEY", ""),
            
            # YouTube
            youtube_api_key=os.getenv("YOUTUBE_API_KEY", ""),
            youtube_channel_id=os.getenv("YT_CHANNEL_ID", ""),
            youtube_client_id=os.getenv("YT_CLIENT_ID_1", ""),
            youtube_client_secret=os.getenv("YT_CLIENT_SECRET_1", ""),
            youtube_refresh_token=os.getenv("YT_REFRESH_TOKEN_1", ""),
            
            # الاحتياطية
            camb_ai_key=os.getenv("CAMB_AI_KEY_1", ""),
            replicate_api_token=os.getenv("REPLICATE_API_TOKEN", ""),
            hf_api_token=os.getenv("HF_API_TOKEN", ""),
            
            # إعدادات خاصة بـ GitHub Actions
            use_low_quality=os.getenv("GITHUB_ACTIONS", "false") == "true"
        )
    
    def validate_apis(self) -> dict:
        """التحقق من توفر APIs"""
        available_apis = {
            "gemini": bool(self.gemini_api_key),
            "groq": bool(self.groq_api_key),
            "openai": bool(self.openai_api_key),
            "elevenlabs": bool(self.eleven_api_key),
            "pexels": bool(self.pexels_api_key),
            "unsplash": bool(self.unsplash_access_key),
            "youtube": bool(self.youtube_api_key and self.youtube_refresh_token),
            "camb_ai": bool(self.camb_ai_key),
        }
        return available_apis

config = Config.from_env()
