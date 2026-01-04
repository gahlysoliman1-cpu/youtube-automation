"""
أداة تشخيص للمشاكل
"""

import os
import sys
import json
from datetime import datetime

def main():
    print("=" * 60)
    print("🔧 YouTube Shorts Debug Tool")
    print("=" * 60)
    
    # 1. التحقق من البيئة
    print("\n1️⃣ Checking environment...")
    
    # التحقق من المتغيرات البيئية
    env_vars = [
        'GEMINI_API_KEY',
        'YOUTUBE_API_KEY',
        'YT_CHANNEL_ID',
        'YT_REFRESH_TOKEN_1'
    ]
    
    print("📋 Environment Variables:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {'*' * 10}{value[-4:] if len(value) > 4 else '***'}")
        else:
            print(f"   ❌ {var}: MISSING")
    
    # 2. التحقق من الملفات والمجلدات
    print("\n2️⃣ Checking files and directories...")
    
    directories = [
        'assets/backgrounds',
        'output/shorts',
        'temp/audio',
        'temp/video'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            files = os.listdir(directory)
            print(f"   ✅ {directory}: {len(files)} files")
            if files:
                for file in files[:3]:  # أول 3 ملفات فقط
                    print(f"      - {file}")
                if len(files) > 3:
                    print(f"      ... and {len(files)-3} more")
        else:
            print(f"   ❌ {directory}: NOT FOUND")
    
    # 3. التحقق من الفيديوهات المنشأة
    print("\n3️⃣ Checking generated videos...")
    
    if os.path.exists('output/shorts'):
        video_files = [f for f in os.listdir('output/shorts') if f.endswith('.mp4')]
        if video_files:
            print(f"   ✅ Found {len(video_files)} video(s):")
            for video in video_files:
                path = os.path.join('output/shorts', video)
                size = os.path.getsize(path) if os.path.exists(path) else 0
                print(f"      - {video} ({size:,} bytes)")
        else:
            print("   ❌ No video files found in output/shorts")
    else:
        print("   ❌ output/shorts directory not found")
    
    # 4. التحقق من بيانات YouTube
    print("\n4️⃣ Checking YouTube configuration...")
    
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        credentials = Credentials(
            token=None,
            refresh_token=os.getenv('YT_REFRESH_TOKEN_1'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv('YT_CLIENT_ID_1'),
            client_secret=os.getenv('YT_CLIENT_SECRET_1'),
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )
        
        # محاولة إنشاء خدمة
        service = build('youtube', 'v3', credentials=credentials)
        
        # التحقق من القناة
        request = service.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        response = request.execute()
        
        if response.get('items'):
            channel = response['items'][0]
            print(f"   ✅ YouTube channel: {channel['snippet']['title']}")
            print(f"      Channel ID: {channel['id']}")
            print(f"      Subscribers: {channel['statistics'].get('subscriberCount', 'N/A')}")
        else:
            print("   ❌ No YouTube channel found")
    
    except Exception as e:
        print(f"   ❌ YouTube API error: {str(e)[:100]}")
    
    # 5. إنشاء تقرير
    print("\n5️⃣ Creating debug report...")
    
    debug_data = {
        "timestamp": datetime.now().isoformat(),
        "environment_variables": {var: bool(os.getenv(var)) for var in env_vars},
        "directories": {},
        "videos_found": video_files if 'video_files' in locals() else [],
        "system_info": {
            "python_version": sys.version,
            "platform": sys.platform
        }
    }
    
    for directory in directories:
        debug_data["directories"][directory] = {
            "exists": os.path.exists(directory),
            "file_count": len(os.listdir(directory)) if os.path.exists(directory) else 0
        }
    
    with open('debug_report.json', 'w') as f:
        json.dump(debug_data, f, indent=2)
    
    print(f"\n📄 Debug report saved to: debug_report.json")
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Check debug_report.json for details")
    print("2. Make sure YouTube API is enabled")
    print("3. Verify OAuth credentials are correct")
    print("4. Run: python test_upload.py")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    main()
