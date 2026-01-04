"""
Utility functions for YouTube Shorts Automation
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List

def setup_logging(log_file: str = None):
    """Setup logging configuration"""
    if log_file is None:
        log_file = f"logs/automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def validate_environment(required_vars: List[str]) -> bool:
    """Validate required environment variables"""
    logger = logging.getLogger(__name__)
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info(f"✅ All environment variables validated ({len(required_vars)} vars)")
    return True

def save_metadata(data: Dict[str, Any], filename: str):
    """Save metadata to JSON file"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return True
    except Exception as e:
        logging.error(f"❌ Error saving metadata: {e}")
        return False

def load_metadata(filename: str) -> Dict[str, Any]:
    """Load metadata from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logging.error(f"❌ Error loading metadata: {e}")
        return {}

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def cleanup_old_files(directory: str, max_files: int = 50):
    """Cleanup old files in directory"""
    try:
        if not os.path.exists(directory):
            return
        
        files = []
        for f in os.listdir(directory):
            filepath = os.path.join(directory, f)
            if os.path.isfile(filepath):
                files.append((filepath, os.path.getmtime(filepath)))
        
        # Sort by modification time (oldest first)
        files.sort(key=lambda x: x[1])
        
        # Remove oldest files if we exceed max_files
        if len(files) > max_files:
            for i in range(len(files) - max_files):
                try:
                    os.remove(files[i][0])
                    logging.info(f"🧹 Cleaned up old file: {os.path.basename(files[i][0])}")
                except:
                    pass
                    
    except Exception as e:
        logging.error(f"❌ Error cleaning up files: {e}")

def retry_operation(operation, max_attempts: int = 3, delay: float = 1.0, **kwargs):
    """Retry an operation with exponential backoff"""
    logger = logging.getLogger(__name__)
    
    for attempt in range(max_attempts):
        try:
            return operation(**kwargs)
        except Exception as e:
            if attempt == max_attempts - 1:
                logger.error(f"❌ Operation failed after {max_attempts} attempts: {e}")
                raise
            
            wait_time = delay * (2 ** attempt)  # Exponential backoff
            logger.warning(f"⚠️ Attempt {attempt + 1} failed. Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)
    
    return None
