#!/usr/bin/env python3
"""
Test script for YouTube upload functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.youtube_uploader import YouTubeUploader
import subprocess

def create_test_video():
    """Create a test video for upload"""
    output_file = "videos/shorts/test_video.mp4"
    
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'color=c=0x2a2a4a:s=1080x1920:d=15',
        '-vf', "drawtext=text='YouTube Short Test':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        '-c:v', 'libx264',
        '-t', '15',
        '-pix_fmt', 'yuv420p',
        output_file
    ]
    
    print("🎬 Creating test video...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and os.path.exists(output_file):
        print(f"✅ Test video created: {output_file}")
        return output_file
    else:
        print(f"❌ Failed to create test video: {result.stderr}")
        return None

def main():
    """Main test function"""
    print("🧪 Testing YouTube Upload...")
    
    # Create test video
    video_path = create_test_video()
    if not video_path:
        print("❌ Cannot proceed without test video")
        sys.exit(1)
    
    # Initialize uploader
    uploader = YouTubeUploader()
    if not uploader.service:
        print("❌ YouTube service not available")
        sys.exit(1)
    
    # Upload video
    result = uploader.upload_video(
        video_path=video_path,
        title="YouTube Shorts Automation Test 🚀",
        description="Testing automated YouTube Shorts upload system\n\nThis video is uploaded automatically via GitHub Actions\n\n#shorts #test #automation #github",
        tags=["test", "automation", "youtube", "shorts", "github"],
        privacy_status="public",  # فيديو عام
        is_short=True
    )
    
    if result and result.get('success'):
        print(f"\n✅ UPLOAD SUCCESSFUL!")
        print(f"🎬 Video ID: {result.get('video_id')}")
        print(f"🔗 Video URL: {result.get('video_url')}")
        print(f"📺 Title: {result.get('title')}")
        print(f"🔒 Privacy: {result.get('privacy_status')}")
        
        # Save results
        with open('test_results.txt', 'w') as f:
            f.write(f"Status: SUCCESS\n")
            f.write(f"Video URL: {result.get('video_url')}\n")
            f.write(f"Video ID: {result.get('video_id')}\n")
        
        sys.exit(0)
    else:
        print(f"\n❌ UPLOAD FAILED!")
        print(f"Error: {result}")
        sys.exit(1)

if __name__ == "__main__":
    main()
