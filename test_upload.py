"""
اختبار رفع فيديو مباشر إلى YouTube
"""

import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime

def test_youtube_upload():
    """اختبار رفع فيديو إلى YouTube"""
    print("=" * 60)
    print("🎬 Testing YouTube Upload")
    print("=" * 60)
    
    try:
        # 1. التحقق من المتغيرات البيئية
        required_envs = [
            'YT_CLIENT_ID_1',
            'YT_CLIENT_SECRET_1',
            'YT_REFRESH_TOKEN_1',
            'YT_CHANNEL_ID'
        ]
        
        missing = []
        for env in required_envs:
            if not os.getenv(env):
                missing.append(env)
        
        if missing:
            print(f"❌ Missing environment variables: {missing}")
            return False
        
        print("✅ All required environment variables found")
        
        # 2. إنشاء Credentials
        credentials = Credentials(
            token=None,
            refresh_token=os.getenv('YT_REFRESH_TOKEN_1'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv('YT_CLIENT_ID_1'),
            client_secret=os.getenv('YT_CLIENT_SECRET_1'),
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )
        
        print("✅ Credentials created")
        
        # 3. تحديث Token إذا لزم الأمر
        if credentials.expired:
            print("🔄 Refreshing token...")
            credentials.refresh(None)
            print("✅ Token refreshed")
        
        # 4. إنشاء خدمة YouTube
        service = build('youtube', 'v3', credentials=credentials)
        print("✅ YouTube service created")
        
        # 5. التحقق من القناة
        request = service.channels().list(
            part="snippet",
            mine=True
        )
        response = request.execute()
        
        if response.get('items'):
            channel = response['items'][0]
            print(f"✅ Connected to channel: {channel['snippet']['title']}")
            print(f"   Channel ID: {channel['id']}")
        else:
            print("❌ No channel found")
            return False
        
        # 6. إنشاء فيديو اختبار بسيط
        print("\n🎥 Creating test video...")
        
        # استخدام MoviePy لإنشاء فيديو اختبار بسيط
        try:
            from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
            
            # إنشاء فيديو بسيط
            background = ColorClip(
                size=(1080, 1920),
                color=(41, 128, 185),
                duration=5
            )
            
            text = TextClip(
                "YouTube Shorts Test\n" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                fontsize=60,
                color='white',
                size=(1000, 400),
                method='caption'
            ).set_position('center').set_duration(5)
            
            video = CompositeVideoClip([background, text])
            
            # حفظ الفيديو
            test_video_path = 'test_short.mp4'
            video.write_videofile(
                test_video_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                logger=None
            )
            
            print(f"✅ Test video created: {test_video_path}")
            
            # 7. رفع الفيديو
            print("\n⬆️ Uploading to YouTube...")
            
            body = {
                'snippet': {
                    'title': f'Test Short - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                    'description': 'This is a test video from YouTube Shorts Automation System.',
                    'tags': ['test', 'shorts', 'automation'],
                    'categoryId': '22'
                },
                'status': {
                    'privacyStatus': 'private',  # private للاختبار
                    'selfDeclaredMadeForKids': False
                }
            }
            
            media = MediaFileUpload(
                test_video_path,
                mimetype='video/*',
                resumable=True
            )
            
            request = service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_id = response['id']
            
            print(f"✅ Video uploaded successfully!")
            print(f"   Video ID: {video_id}")
            print(f"   URL: https://youtube.com/watch?v={video_id}")
            
            # 8. تنظيف الملف المؤقت
            os.remove(test_video_path)
            print("✅ Cleaned up test file")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating/uploading video: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_youtube_upload()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST COMPLETED SUCCESSFULLY!")
        print("Your YouTube upload is working correctly.")
        print("Check your YouTube Studio for the private test video.")
    else:
        print("❌ TEST FAILED")
        print("Please check the error messages above.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
