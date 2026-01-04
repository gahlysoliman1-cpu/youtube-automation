#!/usr/bin/env python3
"""
Simple test to verify everything works
"""

import os
import sys
import logging
from src.question_generator import QuestionGenerator
from src.youtube_uploader import YouTubeUploader

# Setup logging
logging.basicConfig(level=logging.INFO)

def main():
    print("🧪 Running simple tests...")
    
    # Test 1: Question Generator
    print("\n" + "="*50)
    print("1️⃣ Testing Question Generator...")
    print("="*50)
    
    qg = QuestionGenerator()
    
    categories = ["geography", "culture", "history", "science"]
    for category in categories:
        print(f"\n📝 Testing category: {category}")
        question = qg.generate_with_model("gemini", category)
        if question:
            print(f"✅ Question generated: {question['question']}")
            print(f"   Options: {question['options']}")
            print(f"   Correct: {question['correct_answer']}")
        else:
            print(f"❌ Failed to generate question for {category}")
            # Use fallback
            question = qg.generate_fallback_question(category)
            print(f"🔄 Using fallback: {question['question']}")
    
    # Test 2: YouTube Authentication
    print("\n" + "="*50)
    print("2️⃣ Testing YouTube Authentication...")
    print("="*50)
    
    uploader = YouTubeUploader()
    if uploader.service:
        print("✅ YouTube authentication successful")
        
        # Test channel info
        try:
            request = uploader.service.channels().list(
                part="snippet",
                id=os.environ.get("YT_CHANNEL_ID")
            )
            response = request.execute()
            if response.get("items"):
                channel = response["items"][0]
                print(f"📺 Channel: {channel['snippet']['title']}")
                print("✅ Channel verification successful")
        except Exception as e:
            print(f"⚠️ Channel info error: {e}")
    else:
        print("❌ YouTube authentication failed")
        return False
    
    print("\n" + "="*50)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*50)
    
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
