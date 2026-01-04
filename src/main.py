#!/usr/bin/env python3
"""
YouTube Shorts Automation - FINAL PRODUCTION VERSION
"""

import os
import sys
import time
import json
import logging
import random
from datetime import datetime

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import *
from src.question_generator import QuestionGenerator
from src.video_generator import VideoGenerator
from src.youtube_uploader import YouTubeUploader

class YouTubeShortsAutomation:
    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.setup_logging()
        
        self.question_gen = QuestionGenerator()
        self.video_gen = VideoGenerator()
        self.uploader = YouTubeUploader()
        
        self.generated_shorts = []
        
    def setup_logging(self):
        """Setup logging"""
        log_file = os.path.join(LOGS_DIR, f"automation_{self.today}.log")
        os.makedirs(LOGS_DIR, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_environment(self):
        """Validate environment variables"""
        required = [
            "YT_CLIENT_ID_1", "YT_CLIENT_SECRET_1",
            "YT_REFRESH_TOKEN_1", "YT_CHANNEL_ID"
        ]
        
        for var in required:
            if not os.environ.get(var):
                self.logger.error(f"❌ Missing: {var}")
                return False
        
        self.logger.info("✅ Environment validated")
        return True
    
    def generate_question(self, category):
        """Generate a question"""
        try:
            self.logger.info(f"🤔 Generating {category} question...")
            
            # Use Gemini or fallback
            question = self.question_gen.generate_with_model("gemini", category)
            
            if not question:
                question = self.question_gen.generate_fallback_question(category)
            
            if question:
                self.logger.info(f"✅ Question: {question['question'][:50]}...")
                return question
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error generating question: {e}")
            return self.question_gen.generate_fallback_question(category)
    
    def create_video(self, question_data, index):
        """Create video"""
        try:
            timestamp = datetime.now().strftime("%H%M%S")
            output_video = os.path.join(SHORTS_DIR, f"short_{self.today}_{index}.mp4")
            
            self.logger.info(f"🎬 Creating video {index}...")
            
            # Create video
            success = self.video_gen.create_short_video(question_data, output_video)
            
            if success and os.path.exists(output_video):
                file_size = os.path.getsize(output_video) / (1024 * 1024)
                self.logger.info(f"✅ Video created ({file_size:.1f} MB)")
                return output_video
            
            self.logger.error(f"❌ Video creation failed")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error creating video: {e}")
            return None
    
    def generate_title(self, question_data):
        """Generate YouTube title"""
        question = question_data.get('question', 'Can you answer this?')
        category = question_data.get('category', 'trivia')
        
        if len(question) > 40:
            question = question[:37] + "..."
        
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
    
    def generate_description(self, question_data):
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

👉 Write your answer before the timer ends!

✅ Correct answer: {correct}

Subscribe for daily quizzes! 🔔
Like if you enjoy trivia! ❤️

#shorts #quiz #trivia #{category}"""
        
        return description
    
    def upload_video(self, video_path, question_data):
        """Upload video to YouTube"""
        try:
            title = self.generate_title(question_data)
            description = self.generate_description(question_data)
            category = question_data.get('category', 'general')
            
            tags = [
                "shorts", "quiz", "trivia", "challenge",
                "test", "knowledge", category,
                "fun", "education", "viral"
            ]
            
            self.logger.info(f"📤 Uploading: {title}")
            
            result = self.uploader.upload_video(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags,
                privacy_status="public",  # فيديو عام
                is_short=True
            )
            
            if result and result.get('success'):
                video_url = result.get('video_url', 'N/A')
                self.logger.info(f"✅ Upload successful! URL: {video_url}")
                return result
            else:
                self.logger.error(f"❌ Upload failed")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Upload error: {e}")
            return None
    
    def run_single_upload(self):
        """Run single upload"""
        self.logger.info("=" * 60)
        self.logger.info("🎬 SINGLE YOUTUBE SHORT UPLOAD")
        self.logger.info("=" * 60)
        
        if not self.validate_environment():
            return False
        
        category = random.choice(CONTENT_CONFIG["categories"])
        self.logger.info(f"📝 Category: {category}")
        
        question_data = self.generate_question(category)
        if not question_data:
            self.logger.error("❌ No question generated")
            return False
        
        video_path = self.create_video(question_data, 1)
        if not video_path:
            self.logger.error("❌ No video created")
            return False
        
        upload_result = self.upload_video(video_path, question_data)
        if not upload_result:
            self.logger.error("❌ Upload failed")
            return False
        
        self.create_summary([{
            "video_path": video_path,
            "upload_data": upload_result,
            "question_data": question_data
        }])
        
        self.logger.info("=" * 60)
        self.logger.info("✅ SINGLE UPLOAD COMPLETED!")
        self.logger.info("=" * 60)
        
        return True
    
    def run_daily_automation(self):
        """Run daily automation"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 DAILY AUTOMATION (4 shorts)")
        self.logger.info("=" * 60)
        
        if not self.validate_environment():
            return False
        
        uploaded_shorts = []
        
        for i in range(1, 5):
            self.logger.info(f"\n📦 Short {i}/4")
            
            category = CONTENT_CONFIG["categories"][(i-1) % len(CONTENT_CONFIG["categories"])]
            
            question_data = self.generate_question(category)
            if not question_data:
                self.logger.error(f"❌ No question for short {i}")
                continue
            
            video_path = self.create_video(question_data, i)
            if not video_path:
                self.logger.error(f"❌ No video for short {i}")
                continue
            
            upload_result = self.upload_video(video_path, question_data)
            if upload_result:
                uploaded_shorts.append({
                    "video_path": video_path,
                    "upload_data": upload_result,
                    "question_data": question_data
                })
                
                if i < 4:
                    wait = 60
                    self.logger.info(f"⏳ Waiting {wait}s...")
                    time.sleep(wait)
        
        self.create_summary(uploaded_shorts)
        
        success_count = len(uploaded_shorts)
        self.logger.info("=" * 60)
        self.logger.info(f"✅ COMPLETED: {success_count}/4 shorts")
        self.logger.info("=" * 60)
        
        return success_count > 0
    
    def create_summary(self, uploaded_shorts):
        """Create summary file"""
        try:
            summary_file = "upload_summary.md"
            
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
                        f.write(f"- **Question:** {question_data.get('question', 'N/A')}\n")
                        f.write(f"- **Video URL:** {upload_data.get('video_url', 'N/A')}\n")
                        f.write(f"- **Status:** {upload_data.get('privacy_status', 'N/A')}\n\n")
                
                f.write("---\n")
                f.write("*Automated YouTube Shorts System*")
            
            self.logger.info(f"✅ Summary created")
            
        except Exception as e:
            self.logger.error(f"❌ Error creating summary: {e}")
