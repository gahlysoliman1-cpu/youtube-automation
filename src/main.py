#!/usr/bin/env python3
"""
YouTube Shorts Automation - REAL PRODUCTION
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import *
from src.question_generator import QuestionGenerator
from src.video_generator import VideoGenerator
from src.youtube_uploader import YouTubeUploader

class YouTubeShortsAutomation:
    """Main controller for YouTube Shorts automation"""
    
    def __init__(self):
        # Initialize today FIRST
        self.today = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Setup logging (using self.today)
        self.setup_logging()
        
        # Initialize other components
        self.question_gen = QuestionGenerator()
        self.video_gen = VideoGenerator()
        self.uploader = YouTubeUploader()
        
        self.generated_shorts = []
        self.logger.info(f"🚀 YouTube Shorts Automation initialized - {self.today}")
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.join(LOGS_DIR, f"automation_{self.today}.log")
        
        # Create logs directory if not exists
        os.makedirs(LOGS_DIR, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_environment(self) -> bool:
        """Validate all required environment variables"""
        required = [
            "YT_CLIENT_ID_1", "YT_CLIENT_SECRET_1",
            "YT_REFRESH_TOKEN_1", "YT_CHANNEL_ID"
        ]
        
        for var in required:
            if not os.environ.get(var):
                self.logger.error(f"❌ Missing required environment variable: {var}")
                return False
        
        self.logger.info("✅ All environment variables validated")
        return True
    
    def generate_question(self, category: str) -> Optional[Dict]:
        """Generate a question"""
        try:
            self.logger.info(f"🤔 Generating {category} question...")
            
            # Try Gemini first
            question = self.question_gen.generate_with_model("gemini", category)
            
            if question:
                self.logger.info(f"✅ Question generated: {question['question'][:50]}...")
                return question
            else:
                # Use fallback
                self.logger.warning("⚠️ Using fallback question")
                return self.question_gen.generate_fallback_question(category)
                
        except Exception as e:
            self.logger.error(f"❌ Error generating question: {e}")
            return self.question_gen.generate_fallback_question(category)
    
    def create_video(self, question_data: Dict, index: int) -> Optional[str]:
        """Create YouTube Short video"""
        try:
            # Generate video filename
            timestamp = datetime.now().strftime("%H%M%S")
            output_video = os.path.join(SHORTS_DIR, f"short_{self.today}_{index}.mp4")
            
            self.logger.info(f"🎬 Creating video {index}...")
            
            # Try advanced video first
            success = self.video_gen.create_video_with_options(question_data, output_video)
            
            if not success:
                # Fallback to simple video
                self.logger.warning("🔄 Falling back to simple video")
                success = self.video_gen.create_simple_video(question_data, output_video)
            
            if success and os.path.exists(output_video):
                file_size = os.path.getsize(output_video) / (1024 * 1024)
                self.logger.info(f"✅ Video created: {output_video} ({file_size:.1f} MB)")
                
                # Save question data
                question_file = output_video.replace('.mp4', '.json')
                with open(question_file, 'w') as f:
                    json.dump(question_data, f, indent=2)
                
                return output_video
            
            self.logger.error(f"❌ Video creation failed for short {index}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error creating video {index}: {e}")
            return None
    
    def generate_title(self, question_data: Dict) -> str:
        """Generate YouTube title"""
        question = question_data.get('question', 'Can you answer this?')
        category = question_data.get('category', 'trivia')
        
        # قص السؤال إذا كان طويلاً
        if len(question) > 40:
            question = question[:40] + "..."
        
        # إضافة إيموجي حسب الفئة
        emoji_map = {
            "geography": "🌍",
            "culture": "🎭",
            "history": "⚔️",
            "science": "🔬",
            "entertainment": "🎬",
            "sports": "⚽",
            "technology": "💻",
            "music": "🎵"
        }
        
        emoji = emoji_map.get(category, "🤔")
        
        return f"{question} {emoji} #shorts"
    
    def generate_description(self, question_data: Dict) -> str:
        """Generate YouTube description"""
        question = question_data.get('question', 'Can you answer this?')
        category = question_data.get('category', 'trivia')
        options = question_data.get('options', ['A', 'B', 'C', 'D'])
        correct = question_data.get('correct_answer', 'A')
        
        description = f"""Can you answer this {category} question? 😊

{question}

Options:
A) {options[0]}
B) {options[1]}
C) {options[2]}
D) {options[3]}

👉 Write your answer in comments before the timer ends!

✅ Correct answer: {correct}

Subscribe for daily quizzes! 🔔
Like if you enjoy trivia! ❤️

#shorts #quiz #trivia #challenge #{category} #funquiz"""
        
        return description
    
    def upload_video(self, video_path: str, question_data: Dict) -> Optional[Dict]:
        """Upload video to YouTube"""
        try:
            # Generate metadata
            title = self.generate_title(question_data)
            description = self.generate_description(question_data)
            category = question_data.get('category', 'general')
            
            tags = [
                "shorts", "quiz", "trivia", "challenge",
                "test", "knowledge", category,
                "viral", "fun", "education"
            ]
            
            self.logger.info(f"📤 Uploading: {title}")
            
            # Upload video
            result = self.uploader.upload_video(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags,
                privacy_status=YOUTUBE_CONFIG["privacy_status"],  # ستكون 'public'
                is_short=True
            )
            
            if result and result.get('success'):
                video_url = result.get('video_url', 'N/A')
                self.logger.info(f"✅ Upload successful! URL: {video_url}")
                return result
            else:
                self.logger.error(f"❌ Upload failed: {result}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Upload error: {e}")
            return None
    
    def run_single_upload(self) -> bool:
        """Run single upload for testing"""
        self.logger.info("=" * 60)
        self.logger.info("🎬 SINGLE YOUTUBE SHORT UPLOAD")
        self.logger.info("=" * 60)
        
        # Validate environment
        if not self.validate_environment():
            return False
        
        # Select category
        category = random.choice(CONTENT_CONFIG["categories"])
        self.logger.info(f"📝 Selected category: {category}")
        
        # Generate question
        question_data = self.generate_question(category)
        if not question_data:
            self.logger.error("❌ Failed to generate question")
            return False
        
        # Create video
        video_path = self.create_video(question_data, 1)
        if not video_path:
            self.logger.error("❌ Failed to create video")
            return False
        
        # Upload video
        upload_result = self.upload_video(video_path, question_data)
        if not upload_result:
            self.logger.error("❌ Failed to upload video")
            return False
        
        # Create summary
        self.create_summary([{
            "video_path": video_path,
            "upload_data": upload_result,
            "question_data": question_data
        }])
        
        self.logger.info("=" * 60)
        self.logger.info("✅ SINGLE UPLOAD COMPLETED SUCCESSFULLY!")
        self.logger.info("=" * 60)
        
        return True
    
    def run_daily_automation(self) -> bool:
        """Run daily automation - upload 4 shorts"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 DAILY YOUTUBE SHORTS AUTOMATION")
        self.logger.info("=" * 60)
        
        if not self.validate_environment():
            return False
        
        uploaded_shorts = []
        
        for i in range(1, 5):
            self.logger.info(f"\n📦 Processing Short {i}/4")
            
            # Select category
            category = CONTENT_CONFIG["categories"][(i-1) % len(CONTENT_CONFIG["categories"])]
            
            # Generate question
            question_data = self.generate_question(category)
            if not question_data:
                self.logger.error(f"❌ Failed to generate question for short {i}")
                continue
            
            # Create video
            video_path = self.create_video(question_data, i)
            if not video_path:
                self.logger.error(f"❌ Failed to create video for short {i}")
                continue
            
            # Upload video
            upload_result = self.upload_video(video_path, question_data)
            if upload_result:
                uploaded_shorts.append({
                    "video_path": video_path,
                    "upload_data": upload_result,
                    "question_data": question_data
                })
                
                # Wait between uploads
                if i < 4:
                    wait_time = 60  # انتظر دقيقة بين الرفعات
                    self.logger.info(f"⏳ Waiting {wait_time} seconds before next upload...")
                    time.sleep(wait_time)
        
        # Create summary
        self.create_summary(uploaded_shorts)
        
        success_count = len(uploaded_shorts)
        self.logger.info("=" * 60)
        self.logger.info(f"✅ DAILY AUTOMATION COMPLETED: {success_count}/4 shorts uploaded")
        self.logger.info("=" * 60)
        
        return success_count > 0
    
    def create_summary(self, uploaded_shorts: List[Dict]):
        """Create summary markdown file"""
        try:
            summary_file = os.path.join(BASE_DIR, "upload_summary.md")
            
            with open(summary_file, "w") as f:
                f.write("# 📊 YouTube Shorts Upload Summary\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Shorts Uploaded:** {len(uploaded_shorts)}\n\n")
                
                if uploaded_shorts:
                    f.write("## 📺 Uploaded Videos\n\n")
                    for i, short in enumerate(uploaded_shorts, 1):
                        upload_data = short["upload_data"]
                        question_data = short["question_data"]
                        
                        f.write(f"### Short #{i}\n")
                        f.write(f"- **Category:** {question_data.get('category', 'N/A')}\n")
                        f.write(f"- **Question:** {question_data.get('question', 'N/A')}\n")
                        f.write(f"- **Video ID:** {upload_data.get('video_id', 'N/A')}\n")
                        f.write(f"- **Video URL:** {upload_data.get('video_url', 'N/A')}\n")
                        f.write(f"- **Title:** {upload_data.get('title', 'N/A')}\n")
                        f.write(f"- **Privacy:** {upload_data.get('privacy_status', 'N/A')}\n")
                        f.write("\n")
                
                f.write("---\n")
                f.write("*Generated by YouTube Shorts Automation*")
            
            self.logger.info(f"✅ Summary created: {summary_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Error creating summary: {e}")
