#!/usr/bin/env python3
"""
YouTube Video Uploader - Real Production Script
"""

import os
import sys
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def main():
    print("=" * 50)
    print("🚀 YouTube Video Upload - PRODUCTION")
    print("=" * 50)
    
    try:
        # 1. التحقق من المتغيرات
        required = ['YT_CLIENT_ID_1', 'YT_CLIENT_SECRET_1', 
                   'YT_REFRESH_TOKEN_1', 'YT_CHANNEL_ID']
        
        for var in required:
            if not os.environ.get(var):
                print(f"❌ Error: Missing {var}")
                sys.exit(1)
        
        # 2. بيانات الفيديو من الـ inputs
        video_path = os.environ.get('VIDEO_PATH', 'videos/video.mp4')
        video_title = os.environ.get('VIDEO_TITLE', f'Video {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        video_description = os.environ.get('VIDEO_DESCRIPTION', 'Uploaded via GitHub Actions')
        video_tags = os.environ.get('VIDEO_TAGS', '').split(',')
        privacy_status = os.environ.get('VIDEO_PRIVACY', 'private')
        
        print(f"📁 Video: {video_path}")
        print(f"📝 Title: {video_title}")
        print(f"🔒 Privacy: {privacy_status}")
        
        # 3. التحقق من وجود الفيديو
        if not os.path.exists(video_path):
            print(f"❌ Error: Video file not found: {video_path}")
            sys.exit(1)
        
        # 4. إنشاء Credentials
        print("🔐 Creating credentials...")
        credentials = Credentials(
            token=None,
            refresh_token=os.environ.get('YT_REFRESH_TOKEN_1'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.environ.get('YT_CLIENT_ID_1'),
            client_secret=os.environ.get('YT_CLIENT_SECRET_1'),
            scopes=['https://www.googleapis.com/auth/youtube.upload']
        )
        
        # 5. Refresh الـ token إذا لزم
        if credentials.expired:
            credentials.refresh(Request())
            print("✅ Token refreshed")
        
        # 6. بناء خدمة YouTube
        youtube = build('youtube', 'v3', credentials=credentials)
        print("✅ YouTube service ready")
        
        # 7. تحضير metadata الفيديو
        request_body = {
            'snippet': {
                'title': video_title,
                'description': video_description,
                'tags': [tag.strip() for tag in video_tags if tag.strip()],
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # 8. رفع الفيديو
        print("📤 Uploading video...")
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True
        )
        
        start_time = time.time()
        request = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media
        )
        
        response = request.execute()
        upload_time = time.time() - start_time
        
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print("\n" + "=" * 50)
        print("✅ UPLOAD SUCCESSFUL!")
        print("=" * 50)
        print(f"🎬 Video ID: {video_id}")
        print(f"🔗 Video URL: {video_url}")
        print(f"⏱️  Upload time: {upload_time:.1f} seconds")
        print(f"📊 Privacy: {response['status']['privacyStatus']}")
        print(f"👤 Channel: {response['snippet']['channelTitle']}")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"📝 Details: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
