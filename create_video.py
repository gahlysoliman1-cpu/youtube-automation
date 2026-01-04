#!/usr/bin/env python3
"""
Create a real test video for YouTube Shorts
"""

import os
import subprocess
import sys
from datetime import datetime

def create_test_video():
    """Create a test video with ffmpeg"""
    # Create videos directory if not exists
    os.makedirs("videos/shorts", exist_ok=True)
    
    output_file = "videos/shorts/test_video.mp4"
    
    # Create a more professional test video
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'color=c=0x1a1a2e:s=1080x1920:d=15',
        '-filter_complex', 
        f'''[0:v]drawtext=text='YouTube Shorts Test':fontcolor=white:fontsize=72:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:x=(w-text_w)/2:y=(h-text_h)/3,
        drawtext=text='{datetime.now().strftime("%Y-%m-%d %H:%M")}':fontcolor=0x00ff00:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2,
        drawtext=text='Uploaded via GitHub Actions':fontcolor=0xff9900:fontsize=36:x=(w-text_w)/2:y=(h-text_h)*2/3,
        drawtext=text='#shorts #test #automation':fontcolor=0xff66ff:fontsize=32:x=(w-text_w)/2:y=(h-text_h)*3/4[out]''',
        '-map', '[out]',
        '-map', '0:a?',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-t', '15',
        '-pix_fmt', 'yuv420p',
        output_file
    ]
    
    try:
        print(f"🎬 Creating test video: {output_file}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Test video created: {output_file}")
            
            # Check file size
            file_size = os.path.getsize(output_file) / (1024*1024)
            print(f"📊 File size: {file_size:.2f} MB")
            return True
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
            
            # Try simpler command
            return create_simple_video()
            
    except Exception as e:
        print(f"❌ Error creating video: {e}")
        return create_simple_video()

def create_simple_video():
    """Create a simple video as fallback"""
    output_file = "videos/shorts/test_video.mp4"
    
    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'color=c=blue:s=1080x1920:d=10',
        '-vf', "drawtext=text='Test Video':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2",
        '-c:v', 'libx264',
        '-t', '10',
        '-pix_fmt', 'yuv420p',
        output_file
    ]
    
    try:
        print("🔄 Trying simple video creation...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Simple video created: {output_file}")
            return True
        else:
            print(f"❌ Simple video failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error creating simple video: {e}")
        return False

if __name__ == "__main__":
    if create_test_video():
        sys.exit(0)
    else:
        sys.exit(1)
