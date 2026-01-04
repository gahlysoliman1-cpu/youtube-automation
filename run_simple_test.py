#!/usr/bin/env python3
"""
Simple test to verify everything works
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.youtube_uploader import YouTubeUploader
from src.question_generator import QuestionGenerator
from src.audio_generator import AudioGenerator
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("🧪 Running simple test...")
    
    # Test 1: Question Generator
    print("\n1️⃣ Testing Question Generator...")
    qg = QuestionGenerator()
    question = qg.generate_with_model("gemini", "geography")
    if question:
        print(f"✅ Question generated: {question['question']}")
    else:
        print("❌ Question generation failed")
    
    # Test 2: YouTube Authentication
    print("\n2️⃣ Testing YouTube Authentication...")
    uploader = YouTubeUploader()
    if uploader.service:
        print("✅ YouTube authentication successful")
    else:
        print("❌ YouTube authentication failed")
        return False
    
    # Test 3: Create test video
    print("\n3️⃣ Creating test video...")
    from create_video import create_test_video
    if create_test_video():
        print("✅ Test video created")
        
        # Test 4: Upload video
        print("\n4️⃣ Testing YouTube Upload...")
        result = uploader.upload_video(
            video_path="videos/shorts/test_video.mp4",
            title="Test Short - YouTube Automation 🚀",
            description="Testing automated YouTube Shorts upload system\n\n#shorts #test #automation",
            tags=["test", "automation", "youtube", "shorts"],
            privacy_status="private",
            is_short=True
        )
        
        if result and result.get('success'):
            print(f"✅ UPLOAD SUCCESSFUL!")
            print(f"🎬 Video ID: {result.get('video_id')}")
            print(f"🔗 Video URL: {result.get('video_url')}")
            return True
        else:
            print(f"❌ Upload failed: {result}")
            return False
    else:
        print("❌ Test video creation failed")
        return False

if __name__ == "__main__":
    if main():
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n💥 TESTS FAILED!")
        sys.exit(1)
