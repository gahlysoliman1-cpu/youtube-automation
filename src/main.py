#!/usr/bin/env python3
"""
YouTube Shorts Automation - Main Controller
Production ready system for daily shorts generation and upload
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
from src.audio_generator import AudioGenerator
from src.video_generator import VideoGenerator
from src.youtube_uploader import YouTubeUploader
from src.fallback_system import FallbackSystem
from src.utils import validate_environment, setup_logging, save_metadata

class YouTubeShortsAutomation:
    """Main controller for YouTube Shorts automation"""
    
    def __init__(self):
        self.setup_logging()
        self.fallback = FallbackSystem()
        self.question_gen = QuestionGenerator()
        self.audio_gen = AudioGenerator()
        self.video_gen = VideoGenerator()
        self.uploader = YouTubeUploader()
        
        self.generated_shorts = []
        self.today = datetime.now().strftime("%Y%m%d")
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.join(LOGS_DIR, f"automation_{self.today}.log")
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
            "YT_REFRESH_TOKEN_1", "YT_CHANNEL_ID",
            "GEMINI_API_KEY"
        ]
        
        for var in required:
            if not os.environ.get(var):
                self.logger.error(f"❌ Missing required environment variable: {var}")
                return False
        
        self.logger.info("✅ All environment variables validated")
        return True
    
    def generate_question(self, category: str) -> Optional[Dict]:
        """Generate a question with fallback"""
        for model in AI_CONFIG["primary"]["fallback_order"]:
            try:
                self.logger.info(f"🔄 Generating question using {model}...")
                question = self.question_gen.generate_with_model(model, category)
                
                if question and self.validate_question(question):
                    self.logger.info(f"✅ Question generated: {question['question'][:50]}...")
                    return question
                    
            except Exception as e:
                self.logger.warning(f"⚠️ {model} failed: {e}. Trying next model...")
                continue
        
        self.logger.error("❌ All question generation models failed")
        return None
    
    def validate_question(self, question: Dict) -> bool:
        """Validate generated question"""
        required_fields = ["question", "options", "correct_answer", "explanation"]
        
        for field in required_fields:
            if field not in question:
                self.logger.error(f"❌ Question missing field: {field}")
                return False
        
        if len(question["options"]) != 4:
            self.logger.error("❌ Question must have exactly 4 options")
            return False
        
        if question["correct_answer"] not in ["A", "B", "C", "D"]:
            self.logger.error("❌ Invalid correct answer format")
            return False
        
        return True
    
    def generate_audio(self, text: str, output_path: str) -> bool:
        """Generate audio with fallback"""
        return self.audio_gen.generate_with_fallback(text, output_path)
    
    def create_short_video(self, question_data: Dict, index: int) -> Optional[str]:
        """Create a Short video with all elements"""
        try:
            # 1. Generate audio for question
            question_audio = os.path.join(SHORTS_DIR, f"question_{index}.mp3")
            question_text = f"{question_data['question']}. Write your answer before the timer ends!"
            
            if not self.generate_audio(question_text, question_audio):
                self.logger.error(f"❌ Failed to generate audio for question {index}")
                return None
            
            # 2. Generate audio for countdown
            countdown_audio = os.path.join(SHORTS_DIR, f"countdown_{index}.mp3")
            countdown_text = "10, 9, 8, 7, 6, 5, 4, 3, 2, 1"
            
            if not self.generate_audio(countdown_text, countdown_audio):
                self.logger.warning(f"⚠️ Countdown audio failed for short {index}")
            
            # 3. Create video
            output_video = os.path.join(SHORTS_DIR, f"short_{self.today}_{index}.mp4")
            
            self.logger.info(f"🎬 Creating video {index}...")
            success = self.video_gen.create_short_video(
                question_data=question_data,
                question_audio_path=question_audio,
                countdown_audio_path=countdown_audio,
                output_path=output_video
            )
            
            if success and os.path.exists(output_video):
                self.logger.info(f"✅ Video created: {output_video}")
                return output_video
            
            self.logger.error(f"❌ Video creation failed for short {index}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error creating short {index}: {e}")
            return None
    
    def upload_short(self, video_path: str, question_data: Dict) -> Optional[Dict]:
        """Upload short to YouTube"""
        try:
            # Generate title and description
            title = f"{question_data['question'][:40]}... 🤔 #shorts"
            description = self.generate_description(question_data)
            
            # Upload video
            result = self.uploader.upload_video(
                video_path=video_path,
                title=title,
                description=description,
                tags=["quiz", "trivia", "challenge", "shorts", question_data.get("category", "general")],
                privacy_status=YOUTUBE_CONFIG["privacy_status"],
                is_short=True
            )
            
            if result and result.get("success"):
                self.logger.info(f"✅ Short uploaded: {result.get('video_url')}")
                return result
            
            self.logger.error("❌ Short upload failed")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Upload error: {e}")
            return None
    
    def generate_description(self, question_data: Dict) -> str:
        """Generate YouTube description"""
        category = question_data.get("category", "trivia")
        question = question_data.get("question", "")
        
        description = f"""Can you answer this {category} question? 😊

{question}

👉 Write your answer in comments before the timer ends!

Subscribe for daily quizzes!
Watch our other shorts!
Like if you enjoy quizzes!

#shorts #quiz #trivia #challenge #{category} #funquiz"""
        
        return description
    
    def compile_long_video(self, shorts_paths: List[str]) -> Optional[str]:
        """Compile shorts into a long video"""
        if len(shorts_paths) < 4:
            self.logger.warning("⚠️ Not enough shorts to compile long video")
            return None
        
        try:
            output_path = os.path.join(LONG_VIDEOS_DIR, f"compilation_{self.today}.mp4")
            success = self.video_gen.compile_shorts(shorts_paths, output_path)
            
            if success:
                self.logger.info(f"✅ Long video compiled: {output_path}")
                return output_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error compiling long video: {e}")
            return None
    
    def run_daily_automation(self) -> bool:
        """Run daily automation process"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 STARTING DAILY YOUTUBE SHORTS AUTOMATION")
        self.logger.info("=" * 60)
        
        # Validate environment
        if not self.validate_environment():
            return False
        
        uploaded_shorts = []
        
        # Generate and upload 4 shorts
        for i in range(4):
            self.logger.info(f"\n📦 Processing Short {i+1}/4")
            
            # Select category
            category = CONTENT_CONFIG["categories"][i % len(CONTENT_CONFIG["categories"])]
            
            # Generate question
            question_data = self.generate_question(category)
            if not question_data:
                self.logger.error(f"❌ Failed to generate question for short {i+1}")
                continue
            
            # Create video
            video_path = self.create_short_video(question_data, i+1)
            if not video_path:
                continue
            
            # Upload to YouTube
            upload_result = self.upload_short(video_path, question_data)
            if upload_result:
                uploaded_shorts.append({
                    "video_path": video_path,
                    "upload_data": upload_result,
                    "question_data": question_data
                })
                
                # Wait between uploads to avoid rate limits
                if i < 3:
                    self.logger.info("⏳ Waiting 30 seconds before next upload...")
                    time.sleep(30)
        
        # Create summary
        self.create_summary(uploaded_shorts)
        
        # Compile and upload long video if we have at least 2 shorts
        if len(uploaded_shorts) >= 2:
            self.upload_long_video(uploaded_shorts)
        
        self.logger.info("=" * 60)
        self.logger.info(f"✅ DAILY AUTOMATION COMPLETED: {len(uploaded_shorts)} shorts uploaded")
        self.logger.info("=" * 60)
        
        return len(uploaded_shorts) > 0
    
    def upload_long_video(self, shorts_data: List[Dict]):
        """Upload compilation video"""
        try:
            shorts_paths = [item["video_path"] for item in shorts_data]
            compilation_path = self.compile_long_video(shorts_paths)
            
            if compilation_path:
                title = f"Daily Trivia Compilation {datetime.now().strftime('%B %d')} 🎬"
                description = self.generate_long_video_description(shorts_data)
                
                result = self.uploader.upload_video(
                    video_path=compilation_path,
                    title=title,
                    description=description,
                    tags=["compilation", "trivia", "quiz", "shorts", "daily"],
                    privacy_status=YOUTUBE_CONFIG["privacy_status"],
                    is_short=False
                )
                
                if result:
                    self.logger.info(f"✅ Long video uploaded: {result.get('video_url')}")
            
        except Exception as e:
            self.logger.error(f"❌ Error uploading long video: {e}")
    
    def generate_long_video_description(self, shorts_data: List[Dict]) -> str:
        """Generate description for long compilation video"""
        description = f"""📅 Daily Trivia Compilation - {datetime.now().strftime('%B %d, %Y')}

Test your knowledge with today's trivia challenges!
Can you answer all of them correctly? 🤔

"""
        
        for i, short in enumerate(shorts_data, 1):
            question = short["question_data"]["question"]
            description += f"\n{i}. {question}"
        
        description += """

👇 Answers in the individual shorts!

Subscribe for daily quizzes!
Turn on notifications so you don't miss any!

#trivia #quiz #compilation #dailyquiz #knowledge"""
        
        return description
    
    def create_summary(self, uploaded_shorts: List[Dict]):
        """Create summary markdown file"""
        try:
            summary_file = os.path.join(BASE_DIR, "upload_summary.md")
            
            with open(summary_file, "w") as f:
                f.write("# 📊 Daily Upload Summary\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Shorts Uploaded:** {len(uploaded_shorts)}/4\n\n")
                
                if uploaded_shorts:
                    f.write("## 📺 Uploaded Videos\n\n")
                    for i, short in enumerate(uploaded_shorts, 1):
                        upload_data = short["upload_data"]
                        question_data = short["question_data"]
                        
                        f.write(f"### Short #{i}\n")
                        f.write(f"- **Question:** {question_data['question']}\n")
                        f.write(f"- **Category:** {question_data.get('category', 'N/A')}\n")
                        f.write(f"- **Video URL:** {upload_data.get('video_url', 'N/A')}\n")
                        f.write(f"- **Video ID:** {upload_data.get('video_id', 'N/A')}\n")
                        f.write(f"- **Status:** {upload_data.get('status', 'N/A')}\n\n")
                
                f.write("---\n")
                f.write("*Generated by YouTube Shorts Automation*")
            
            self.logger.info(f"✅ Summary created: {summary_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Error creating summary: {e}")

def main():
    """Main entry point"""
    automation = YouTubeShortsAutomation()
    
    # Check command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Shorts Automation")
    parser.add_argument("--mode", choices=["daily", "single"], default="daily")
    args = parser.parse_args()
    
    if args.mode == "daily":
        success = automation.run_daily_automation()
        sys.exit(0 if success else 1)
    else:
        automation.logger.info("Single mode not implemented yet")
        sys.exit(1)

if __name__ == "__main__":
    main()
