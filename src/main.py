"""
النموذج الرئيسي للتشغيل
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.config import config
from src.utils import logger, create_directories, cleanup_temp_files, save_metadata
from src.question_generator import QuestionGenerator
from src.audio_generator import AudioGenerator
from src.background_generator import BackgroundGenerator
from src.video_generator import VideoGenerator
from src.youtube_uploader import YouTubeUploader
from src.fallback_system import FallbackSystem

class YouTubeShortsAutomation:
    """الأتمتة الرئيسية لـ YouTube Shorts"""
    
    def __init__(self):
        self.question_gen = QuestionGenerator()
        self.audio_gen = AudioGenerator()
        self.background_gen = BackgroundGenerator()
        self.video_gen = VideoGenerator()
        self.youtube_uploader = YouTubeUploader()
        self.fallback = FallbackSystem()
        
        self.generated_shorts = []
        self.uploaded_urls = []
    
    def run_daily_cycle(self, shorts_count: int = 4) -> bool:
        """تشغيل دورة يومية كاملة"""
        try:
            logger.info("=" * 50)
            logger.info("Starting Daily YouTube Shorts Automation")
            logger.info(f"Time: {datetime.now()}")
            logger.info("=" * 50)
            
            # التحقق من المساحة
            if not check_disk_space():
                logger.error("Insufficient disk space")
                return False
            
            # إنشاء المجلدات
            create_directories()
            
            # توليد الشورتات اليومية
            for i in range(shorts_count):
                logger.info(f"\n{'='*30}")
                logger.info(f"Generating Short {i+1}/{shorts_count}")
                logger.info(f"{'='*30}")
                
                short_data = self._generate_single_short()
                if short_data:
                    self.generated_shorts.append(short_data)
            
            # إنشاء فيديو التجميع الطويل
            if len(self.generated_shorts) >= 2:
                compilation_path = self._create_compilation()
                if compilation_path:
                    self._upload_compilation(compilation_path)
            
            # تسجيل النتائج
            self._log_results()
            
            # تنظيف الملفات المؤقتة
            cleanup_temp_files()
            
            logger.info("\n" + "=" * 50)
            logger.info("Daily Cycle Completed Successfully!")
            logger.info("=" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"Fatal error in daily cycle: {e}")
            return False
    
    def _generate_single_short(self) -> Optional[Dict[str, Any]]:
        """توليد شورت واحد"""
        try:
            # 1. توليد المحتوى
            content_data = self.question_gen.generate_quiz_content()
            if not content_data:
                logger.error("Failed to generate content")
                return None
            
            # 2. توليد الخلفية
            background_path = self.background_gen.generate_background(
                content_data["category"]
            )
            if not background_path:
                logger.warning("Using fallback background")
                background_path = "assets/fallback_background.jpg"
            
            # 3. توليد الصوت
            audio_path = self.audio_gen.generate_question_audio(
                content_data["question"],
                content_data["encouragement"]
            )
            
            # 4. توليد صوت العد التنازلي
            countdown_audio_path = self.audio_gen.generate_countdown_beep()
            
            # 5. إنشاء الفيديو
            video_path = self.video_gen.create_short_video(
                content_data,
                background_path,
                audio_path,
                countdown_audio_path
            )
            
            if not video_path:
                logger.error("Failed to create video")
                return None
            
            # 6. رفع الفيديو إلى YouTube
            video_url = None
            if config.upload_to_youtube and self.youtube_uploader.service:
                video_url = self.youtube_uploader.upload_video(
                    video_path,
                    content_data["seo"]
                )
            
            # 7. حفظ البيانات
            short_data = {
                "content": content_data,
                "video_path": video_path,
                "video_url": video_url,
                "background_path": background_path,
                "audio_path": audio_path,
                "timestamp": datetime.now().isoformat()
            }
            
            # حفظ البيانات الوصفية
            save_metadata(short_data, f"short_{content_data['id']}")
            
            if video_url:
                self.uploaded_urls.append(video_url)
                logger.info(f"✅ Short uploaded: {video_url}")
            else:
                logger.info(f"✅ Short generated (not uploaded): {video_path}")
            
            return short_data
            
        except Exception as e:
            logger.error(f"Error generating short: {e}")
            return None
    
    def _create_compilation(self) -> Optional[str]:
        """إنشاء فيديو تجميعي طويل"""
        try:
            logger.info("\nCreating daily compilation...")
            
            short_paths = [s.get("video_path") for s in self.generated_shorts]
            short_paths = [p for p in short_paths if p and os.path.exists(p)]
            
            if len(short_paths) < 2:
                logger.warning("Not enough shorts for compilation")
                return None
            
            # تاريخ اليوم
            today_date = datetime.now().strftime("%Y%m%d")
            
            compilation_path = self.video_gen.create_long_compilation(
                short_paths,
                today_date
            )
            
            if compilation_path:
                logger.info(f"✅ Compilation created: {compilation_path}")
                
                # حفظ البيانات الوصفية للتجميع
                compilation_data = {
                    "date": today_date,
                    "shorts_count": len(short_paths),
                    "shorts_ids": [s["content"]["id"] for s in self.generated_shorts],
                    "compilation_path": compilation_path,
                    "timestamp": datetime.now().isoformat()
                }
                
                save_metadata(compilation_data, f"compilation_{today_date}")
            
            return compilation_path
            
        except Exception as e:
            logger.error(f"Error creating compilation: {e}")
            return None
    
    def _upload_compilation(self, compilation_path: str):
        """رفع فيديو التجميع"""
        try:
            if not config.upload_to_youtube or not self.youtube_uploader.service:
                logger.info("YouTube upload disabled")
                return
            
            logger.info("\nUploading compilation...")
            
            shorts_content = [s["content"] for s in self.generated_shorts]
            
            compilation_url = self.youtube_uploader.upload_compilation(
                compilation_path,
                shorts_content
            )
            
            if compilation_url:
                logger.info(f"✅ Compilation uploaded: {compilation_url}")
                self.uploaded_urls.append(compilation_url)
            
        except Exception as e:
            logger.error(f"Error uploading compilation: {e}")
    
    def _log_results(self):
        """تسجيل نتائج التشغيل"""
        results = {
            "date": datetime.now().isoformat(),
            "total_shorts_generated": len(self.generated_shorts),
            "total_uploads": len(self.uploaded_urls),
            "uploaded_urls": self.uploaded_urls,
            "shorts_details": [
                {
                    "id": s["content"]["id"],
                    "question": s["content"]["question"][:50],
                    "category": s["content"]["category"],
                    "url": s.get("video_url", "not_uploaded")
                }
                for s in self.generated_shorts
            ]
        }
        
        save_metadata(results, f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # طباعة النتائج
        logger.info("\n" + "=" * 50)
        logger.info("FINAL RESULTS:")
        logger.info(f"Shorts Generated: {len(self.generated_shorts)}")
        logger.info(f"Uploads Successful: {len(self.uploaded_urls)}")
        
        for url in self.uploaded_urls:
            logger.info(f"  - {url}")
        
        logger.info("=" * 50)
    
    def run_immediate_short(self) -> bool:
        """تشغيل وتنزيل شورت واحد فوري"""
        try:
            logger.info("Generating immediate short...")
            
            short_data = self._generate_single_short()
            
            if short_data and short_data.get("video_url"):
                logger.info(f"✅ IMMEDIATE SUCCESS: Short uploaded to {short_data['video_url']}")
                return True
            elif short_data:
                logger.info(f"✅ Short generated at: {short_data.get('video_path')}")
                return True
            else:
                logger.error("❌ Failed to generate immediate short")
                return False
                
        except Exception as e:
            logger.error(f"Error in immediate short: {e}")
            return False

def check_disk_space() -> bool:
    """التحقق من مساحة القرص (نسخة مبسطة)"""
    import shutil
    
    try:
        stat = shutil.disk_usage(".")
        free_gb = stat.free / (1024 ** 3)
        return free_gb >= 1.0
    except:
        return True
