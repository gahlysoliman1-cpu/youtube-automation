"""
أدوات مساعدة
"""

import os
import json
import logging
import tempfile
import shutil
from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib

# إعدادات التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    dirs = [
        "temp/audio",
        "temp/video", 
        "temp/images",
        "output/shorts",
        "output/long_videos",
        "assets/backgrounds",
        "assets/fonts"
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def cleanup_temp_files():
    """تنظيف الملفات المؤقتة"""
    if os.path.exists("temp"):
        shutil.rmtree("temp")
        logger.info("Cleaned up temp directory")

def save_metadata(metadata: Dict[str, Any], filename: str):
    """حفظ البيانات الوصفية"""
    metadata_path = f"output/metadata/{filename}.json"
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Metadata saved to {metadata_path}")

def load_metadata(filename: str) -> Optional[Dict[str, Any]]:
    """تحميل البيانات الوصفية"""
    metadata_path = f"output/metadata/{filename}.json"
    
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def generate_unique_id(content: str) -> str:
    """إنشاء معرّف فريد للمحتوى"""
    return hashlib.md5(content.encode()).hexdigest()[:8]

def format_time(seconds: int) -> str:
    """تنسيق الوقت"""
    return f"{seconds:02d}"

def validate_file_exists(filepath: str) -> bool:
    """التحقق من وجود الملف"""
    return os.path.exists(filepath) and os.path.getsize(filepath) > 0

def get_timestamp() -> str:
    """الحصول على الطابع الزمني الحالي"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def check_disk_space(min_space_gb: float = 1.0) -> bool:
    """التحقق من مساحة القرص المتاحة"""
    stat = shutil.disk_usage(".")
    free_gb = stat.free / (1024 ** 3)
    return free_gb >= min_space_gb
