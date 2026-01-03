"""
رفع الفيديوهات إلى YouTube
"""

import os
from typing import Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.config import config
from src.utils import logger, validate_file_exists
from src.constants import (
    YOUTUBE_CATEGORY_ID, YOUTUBE_PRIVACY_STATUS
)

class YouTubeUploader:
    """رفع الفيديوهات إلى YouTube"""
    
    def __init__(self):
        self.service = None
        self.initialize_service()
    
    def initialize_service(self):
        """تهيئة خدمة YouTube API"""
        try:
            credentials = Credentials(
                token=None,
                refresh_token=config.youtube_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=config.youtube_client_id,
                client_secret=config.youtube_client_secret,
                scopes=["https://www.googleapis.com/auth/youtube.upload"]
            )
            
            if credentials.expired:
                credentials.refresh(Request())
            
            self.service = build('youtube', 'v3', credentials=credentials)
            logger.info("YouTube API service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize YouTube service: {e}")
            self.service = None
    
    def upload_video(self, video_path: str, metadata: Dict[str, Any]) -> Optional[str]:
        """رفع فيديو إلى YouTube"""
        if not self.service or not validate_file_exists(video_path):
            logger.error("YouTube service not initialized or video file missing")
            return None
        
        try:
            # إعداد بيانات الفيديو
            body = {
                'snippet': {
                    'title': metadata.get('title', 'Daily Quiz Short'),
                    'description': metadata.get('description', ''),
                    'tags': metadata.get('tags', []),
                    'categoryId': YOUTUBE_CATEGORY_ID
                },
                'status': {
                    'privacyStatus': YOUTUBE_PRIVACY_STATUS,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # إنشاء طلب الرفع
            media = MediaFileUpload(
                video_path,
                mimetype='video/*',
                resumable=True,
                chunksize=1024 * 1024
            )
            
            # تنفيذ الرفع
            request = self.service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://youtube.com/shorts/{video_id}"
            
            logger.info(f"Video uploaded successfully: {video_url}")
            
            # إضافة الفيديو إلى قائمة التشغيل إذا كانت موجودة
            self._add_to_playlist(video_id)
            
            return video_url
            
        except Exception as e:
            logger.error(f"Failed to upload video: {e}")
            return None
    
    def _add_to_playlist(self, video_id: str):
        """إضافة الفيديو إلى قائمة التشغيل"""
        try:
            # البحث عن قائمة التشغيل اليومية
            playlists_response = self.service.playlists().list(
                part='snippet',
                mine=True,
                maxResults=50
            ).execute()
            
            playlist_id = None
            today_date = os.environ.get('RUN_DATE', 'Daily')
            
            for playlist in playlists_response.get('items', []):
                if f"Daily Quiz {today_date}" in playlist['snippet']['title']:
                    playlist_id = playlist['id']
                    break
            
            # إنشاء قائمة تشغيل جديدة إذا لم توجد
            if not playlist_id:
                playlist_response = self.service.playlists().insert(
                    part='snippet,status',
                    body={
                        'snippet': {
                            'title': f'Daily Quiz {today_date}',
                            'description': 'Daily quiz shorts compilation'
                        },
                        'status': {
                            'privacyStatus': 'public'
                        }
                    }
                ).execute()
                
                playlist_id = playlist_response['id']
                logger.info(f"Created new playlist: {playlist_id}")
            
            # إضافة الفيديو إلى قائمة التشغيل
            self.service.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            ).execute()
            
            logger.info(f"Added video {video_id} to playlist {playlist_id}")
            
        except Exception as e:
            logger.error(f"Failed to add to playlist: {e}")
    
    def upload_compilation(self, compilation_path: str, shorts_data: list) -> Optional[str]:
        """رفع فيديو التجميع الطويل"""
        if not validate_file_exists(compilation_path):
            logger.error("Compilation video file missing")
            return None
        
        # إنشاء وصف للتجميع
        description = "🎯 Daily Quiz Compilation 🎯\n\n"
        for i, data in enumerate(shorts_data, 1):
            description += f"{i}. {data.get('question', '')}\n"
        
        description += "\n🔔 Subscribe for daily quizzes!\n"
        description += "#shorts #quiz #compilation #dailyquiz"
        
        metadata = {
            'title': f'Daily Quiz Compilation - {os.environ.get("RUN_DATE", "Today")}',
            'description': description,
            'tags': ['compilation', 'quiz', 'shorts', 'daily', 'challenge']
        }
        
        return self.upload_video(compilation_path, metadata)
