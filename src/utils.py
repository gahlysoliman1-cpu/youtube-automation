"""
Utilities Module
Helper functions for the YouTube Shorts Automation
"""

import os
import sys
import json
import logging
import random
import string
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.config import *

def setup_logging(log_file: Optional[str] = None) -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger("YouTubeShorts")
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
    
    return logger

def validate_environment() -> bool:
    """Validate all required environment variables"""
    required_vars = [
        "YT_CLIENT_ID_1",
        "YT_CLIENT_SECRET_1", 
        "YT_REFRESH_TOKEN_1",
        "YT_CHANNEL_ID",
        "GEMINI_API_KEY"
    ]
    
    logger = logging.getLogger("YouTubeShorts")
    
    for var in required_vars:
        if not os.environ.get(var):
            logger.error(f"❌ Missing required environment variable: {var}")
            return False
    
    logger.info("✅ Environment variables validated")
    return True

def create_unique_id(prefix: str = "") -> str:
    """Create a unique identifier"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}{timestamp}_{random_str}"

def calculate_md5(file_path: str) -> str:
    """Calculate MD5 hash of a file"""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
            return file_hash.hexdigest()
    except Exception:
        return ""

def save_metadata(data: Dict, filename: str) -> bool:
    """Save metadata to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving metadata: {e}")
        return False

def load_metadata(filename: str) -> Optional[Dict]:
    """Load metadata from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading metadata: {e}")
    return None

def ensure_directory(path: str) -> bool:
    """Ensure directory exists"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {path}: {e}")
        return False

def cleanup_old_files(directory: str, days: int = 7):
    """Clean up files older than specified days"""
    try:
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for file_path in Path(directory).glob("*"):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    file_path.unlink()
                    logging.info(f"Cleaned up old file: {file_path}")
    except Exception as e:
        logging.error(f"Error cleaning up files: {e}")

def format_duration(seconds: float) -> str:
    """Format duration in seconds to readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes"""
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path) / (1024 * 1024)
    except Exception:
        pass
    return 0.0

def is_video_file(file_path: str) -> bool:
    """Check if file is a video"""
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm'}
    return Path(file_path).suffix.lower() in video_extensions

def is_audio_file(file_path: str) -> bool:
    """Check if file is an audio file"""
    audio_extensions = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'}
    return Path(file_path).suffix.lower() in audio_extensions

def validate_video_file(file_path: str) -> tuple[bool, str]:
    """Validate video file"""
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    if not is_video_file(file_path):
        return False, "Not a video file"
    
    file_size = get_file_size_mb(file_path)
    if file_size == 0:
        return False, "File is empty"
    
    if file_size > 128 * 1024:  # 128GB YouTube limit
        return False, f"File too large ({file_size:.1f}MB > 128GB)"
    
    return True, f"Valid video file ({file_size:.1f}MB)"

def generate_simple_thumbnail(question: str, output_path: str) -> bool:
    """Generate a simple thumbnail image"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create image
        img = Image.new('RGB', (1280, 720), color=(41, 128, 185))
        draw = ImageDraw.Draw(img)
        
        # Try to load font
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # Draw question (simplified)
        words = question.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= 1200:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw text
        y = 200
        for line in lines[:3]:  # Only first 3 lines
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (1280 - (bbox[2] - bbox[0])) // 2
            draw.text((x, y), line, font=font, fill="white")
            y += 70
        
        # Add watermark
        draw.text((50, 650), "Daily Quiz #shorts", font=font, fill="white")
        
        # Save
        img.save(output_path, "PNG")
        return True
        
    except Exception as e:
        logging.error(f"Error generating thumbnail: {e}")
        return False

def check_disk_space(min_space_gb: float = 1.0) -> bool:
    """Check if there's enough disk space"""
    try:
        stat = os.statvfs('/')
        free_space_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        return free_space_gb >= min_space_gb
    except Exception:
        return True  # Assume enough space if can't check
