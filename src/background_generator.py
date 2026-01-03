"""
مولد الخلفيات للفيديو
"""

import os
import random
from typing import Optional, Tuple
import requests
from PIL import Image, ImageFilter
from io import BytesIO
from src.config import config
from src.utils import logger, validate_file_exists
from src.constants import BACKGROUNDS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, BACKGROUND_BLUR_INTENSITY

class BackgroundGenerator:
    """مولد خلفيات الفيديو"""
    
    def __init__(self):
        self.api_priority = ["pexels", "unsplash", "fallback"]
        self.cache_dir = BACKGROUNDS_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def generate_background(self, category: str = "abstract") -> Optional[str]:
        """توليد خلفية للفيديو"""
        background_path = None
        
        for api_name in self.api_priority:
            if background_path:
                break
            
            if api_name == "pexels" and config.pexels_api_key:
                background_path = self._get_from_pexels(category)
            elif api_name == "unsplash" and config.unsplash_access_key:
                background_path = self._get_from_unsplash(category)
            elif api_name == "fallback":
                background_path = self._get_fallback_background(category)
        
        if background_path:
            # تطبيق تأثير البلور
            blurred_path = self._apply_blur(background_path)
            return blurred_path
        
        return None
    
    def _get_from_pexels(self, category: str) -> Optional[str]:
        """الحصول على خلفية من Pexels"""
        try:
            # ترجمة الفئة إلى كلمات مفتاحية
            keywords = self._translate_category(category)
            
            url = "https://api.pexels.com/v1/search"
            headers = {
                "Authorization": config.pexels_api_key
            }
            params = {
                "query": keywords,
                "per_page": 1,
                "page": random.randint(1, 10),
                "orientation": "portrait",
                "size": "large"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("photos"):
                photo = random.choice(data["photos"])
                photo_url = photo["src"]["original"]
                
                # تحميل الصورة
                img_response = requests.get(photo_url, timeout=30)
                img_response.raise_for_status()
                
                # حفظ الصورة
                background_path = os.path.join(self.cache_dir, f"pexels_{os.urandom(4).hex()}.jpg")
                
                with open(background_path, "wb") as f:
                    f.write(img_response.content)
                
                if validate_file_exists(background_path):
                    logger.info(f"Downloaded background from Pexels: {background_path}")
                    return background_path
        
        except Exception as e:
            logger.error(f"Pexels API failed: {e}")
        
        return None
    
    def _get_from_unsplash(self, category: str) -> Optional[str]:
        """الحصول على خلفية من Unsplash"""
        try:
            keywords = self._translate_category(category)
            
            url = "https://api.unsplash.com/photos/random"
            headers = {
                "Authorization": f"Client-ID {config.unsplash_access_key}"
            }
            params = {
                "query": keywords,
                "orientation": "portrait"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("urls"):
                photo_url = data["urls"]["regular"]
                
                # تحميل الصورة
                img_response = requests.get(photo_url, timeout=30)
                img_response.raise_for_status()
                
                # حفظ الصورة
                background_path = os.path.join(self.cache_dir, f"unsplash_{os.urandom(4).hex()}.jpg")
                
                with open(background_path, "wb") as f:
                    f.write(img_response.content)
                
                if validate_file_exists(background_path):
                    logger.info(f"Downloaded background from Unsplash: {background_path}")
                    return background_path
        
        except Exception as e:
            logger.error(f"Unsplash API failed: {e}")
        
        return None
    
    def _get_fallback_background(self, category: str) -> Optional[str]:
        """الحصول على خلفية احتياطية"""
        try:
            # ألوان خلفية افتراضية
            colors = {
                "general_knowledge": [(41, 128, 185), (52, 152, 219)],  # أزرق
                "culture": [(142, 68, 173), (155, 89, 182)],  # بنفسجي
                "entertainment": [(230, 126, 34), (243, 156, 18)],  # برتقالي
                "geography": [(39, 174, 96), (46, 204, 113)],  # أخضر
                "music": [(192, 57, 43), (231, 76, 60)],  # أحمر
                "history": [(127, 140, 141), (149, 165, 166)],  # رمادي
                "science": [(22, 160, 133), (26, 188, 156)],  # تركواز
                "abstract": [(52, 73, 94), (44, 62, 80)]  # أزرق داكن
            }
            
            color_pair = colors.get(category, colors["abstract"])
            
            # إنشاء تدرج لوني
            from PIL import ImageDraw
            
            img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), color=color_pair[0])
            draw = ImageDraw.Draw(img)
            
            # رسم تدرج لوني بسيط
            for i in range(VIDEO_HEIGHT):
                ratio = i / VIDEO_HEIGHT
                r = int(color_pair[0][0] * (1 - ratio) + color_pair[1][0] * ratio)
                g = int(color_pair[0][1] * (1 - ratio) + color_pair[1][1] * ratio)
                b = int(color_pair[0][2] * (1 - ratio) + color_pair[1][2] * ratio)
                draw.line([(0, i), (VIDEO_WIDTH, i)], fill=(r, g, b))
            
            # إضافة بعض الأشكال العشوائية
            for _ in range(20):
                x = random.randint(0, VIDEO_WIDTH)
                y = random.randint(0, VIDEO_HEIGHT)
                size = random.randint(50, 300)
                color = (255, 255, 255, random.randint(10, 30))
                draw.ellipse([x, y, x + size, y + size], fill=color)
            
            background_path = os.path.join(self.cache_dir, f"fallback_{category}.jpg")
            img.save(background_path, quality=95)
            
            logger.info(f"Created fallback background: {background_path}")
            return background_path
        
        except Exception as e:
            logger.error(f"Fallback background generation failed: {e}")
        
        return None
    
    def _translate_category(self, category: str) -> str:
        """ترجمة الفئة إلى كلمات مفتاحية"""
        translations = {
            "general_knowledge": "knowledge education facts",
            "culture": "culture world countries traditions",
            "entertainment": "entertainment movies music celebrities",
            "geography": "geography earth map landscape",
            "music": "music instruments concert",
            "history": "history ancient vintage",
            "science": "science technology space",
            "abstract": "abstract colorful background"
        }
        
        return translations.get(category, "abstract background")
    
    def _apply_blur(self, image_path: str) -> Optional[str]:
        """تطبيق تأثير البلور على الصورة"""
        try:
            img = Image.open(image_path)
            
            # تغيير الحجم إذا لزم الأمر
            if img.size != (VIDEO_WIDTH, VIDEO_HEIGHT):
                img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
            
            # تطبيق البلور
            blurred_img = img.filter(ImageFilter.GaussianBlur(BACKGROUND_BLUR_INTENSITY))
            
            # حفظ الصورة المخففة
            blurred_path = image_path.replace(".jpg", "_blurred.jpg")
            blurred_img.save(blurred_path, quality=95)
            
            logger.info(f"Applied blur to background: {blurred_path}")
            return blurred_path
        
        except Exception as e:
            logger.error(f"Failed to apply blur: {e}")
            return image_path
