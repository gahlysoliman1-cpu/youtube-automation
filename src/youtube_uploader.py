"""
YouTube Uploader Module
Handles authentication and upload to YouTube with proper error handling
"""

import os
import json
import time
import logging
from typing import Dict, Optional, List
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

from src.config import *

class YouTubeUploader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.service = None
        self.authenticate()
        
    def authenticate(self) -> bool:
        """Authenticate with YouTube API"""
        try:
            credentials = Credentials(
                token=None,
                refresh_token=YOUTUBE_CONFIG["refresh_token"],
                token_uri=YOUTUBE_CONFIG["token_uri"],
                client_id=YOUTUBE_CONFIG["client_id"],
                client_secret=YOUTUBE_CONFIG["client_secret"],
                scopes=YOUTUBE_CONFIG["scopes"]
            )
            
            # Refresh token if expired
            if credentials.expired:
                credentials.refresh(Request())
                self.logger.info("✅ YouTube token refreshed")
            
            # Build YouTube service
            self.service = build('youtube', 'v3', credentials=credentials)
            self.logger.info("✅ YouTube authentication successful")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ YouTube authentication failed: {e}")
            return False
    
    def upload_video(self, video_path: str, title: str, description: str, 
                    tags: List[str], privacy_status: str, is_short: bool = True) -> Optional[Dict]:
        """Upload video to YouTube"""
        if not self.service:
            self.logger.error("❌ YouTube service not initialized")
            return None
        
        try:
            # Validate video file
            if not os.path.exists(video_path):
                self.logger.error(f"❌ Video file not found: {video_path}")
                return None
            
            file_size = os.path.getsize(video_path)
            if file_size == 0:
                self.logger.error(f"❌ Video file is empty: {video_path}")
                return None
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': YOUTUBE_CONFIG["category_id"],
                    'defaultLanguage': YOUTUBE_CONFIG["default_language"]
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False,
                    'embeddable': True
                }
            }
            
            # Add #shorts to description if it's a short
            if is_short and '#shorts' not in description.lower():
                body['snippet']['description'] = description + '\n\n#shorts'
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True,
                chunksize=1024*1024  # 1MB chunks
            )
            
            self.logger.info(f"📤 Uploading video: {title}")
            start_time = time.time()
            
            # Execute upload request
            request = self.service.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    self.logger.info(f"📊 Upload progress: {progress}%")
            
            upload_time = time.time() - start_time
            
            # Extract video info
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            channel_id = response['snippet']['channelId']
            
            upload_result = {
                'success': True,
                'video_id': video_id,
                'video_url': video_url,
                'title': response['snippet']['title'],
                'description': response['snippet']['description'],
                'channel_id': channel_id,
                'channel_title': response['snippet']['channelTitle'],
                'privacy_status': response['status']['privacyStatus'],
                'upload_time': upload_time,
                'file_size': file_size,
                'upload_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'is_short': is_short
            }
            
            self.logger.info(f"✅ Upload completed in {upload_time:.1f} seconds")
            self.logger.info(f"🔗 Video URL: {video_url}")
            
            # Verify upload
            if self.verify_upload(video_id):
                self.logger.info(f"✅ Video verified on YouTube")
                upload_result['verified'] = True
            else:
                self.logger.warning(f"⚠️ Video verification failed")
                upload_result['verified'] = False
            
            # Save upload log
            self.save_upload_log(upload_result)
            
            return upload_result
            
        except HttpError as e:
            error_content = json.loads(e.content.decode())
            self.logger.error(f"❌ YouTube API error: {error_content}")
            return {
                'success': False,
                'error': error_content,
                'error_type': 'youtube_api'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Upload failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'general'
            }
    
    def verify_upload(self, video_id: str) -> bool:
        """Verify that video was successfully uploaded"""
        try:
            # Wait a bit for YouTube processing
            time.sleep(5)
            
            # Get video details
            request = self.service.videos().list(
                part='status,statistics',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                self.logger.error(f"❌ Video {video_id} not found after upload")
                return False
            
            video = response['items'][0]
            status = video['status']['uploadStatus']
            
            if status == 'processed':
                self.logger.info(f"✅ Video {video_id} is fully processed")
                return True
            elif status == 'uploaded':
                self.logger.info(f"⚠️ Video {video_id} is uploaded but not yet processed")
                return True  # Still consider successful
            else:
                self.logger.error(f"❌ Video {video_id} has status: {status}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Verification error: {e}")
            return False
    
    def save_upload_log(self, upload_data: Dict):
        """Save upload details to log file"""
        try:
            log_file = os.path.join(LOGS_DIR, 'upload_history.json')
            
            # Load existing logs
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Add new log
            logs.append(upload_data)
            
            # Keep only last 100 entries
            if len(logs) > 100:
                logs = logs[-100:]
            
            # Save logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            self.logger.info(f"✅ Upload log saved")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving upload log: {e}")
    
    def check_rate_limit(self):
        """Check and handle YouTube API rate limits"""
        # YouTube has quota limits, so we implement delays
        time.sleep(2)  # 2 seconds between API calls
    
    def update_video_metadata(self, video_id: str, title: str = None, 
                             description: str = None, tags: List[str] = None) -> bool:
        """Update video metadata after upload"""
        try:
            if not self.service:
                return False
            
            # Get current video details
            request = self.service.videos().list(
                part='snippet',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return False
            
            video = response['items'][0]
            snippet = video['snippet']
            
            # Update fields
            if title:
                snippet['title'] = title
            if description:
                snippet['description'] = description
            if tags:
                snippet['tags'] = tags
            
            # Execute update
            update_request = self.service.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            )
            
            update_request.execute()
            self.logger.info(f"✅ Video metadata updated: {video_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error updating metadata: {e}")
            return False
    
    def get_channel_info(self):
        """Get channel information"""
        try:
            if not self.service:
                return None
            
            request = self.service.channels().list(
                part='snippet,statistics,contentDetails',
                id=YOUTUBE_CONFIG["channel_id"]
            )
            
            response = request.execute()
            
            if response.get('items'):
                channel = response['items'][0]
                self.logger.info(f"📊 Channel: {channel['snippet']['title']}")
                self.logger.info(f"👥 Subscribers: {channel['statistics'].get('subscriberCount', 'N/A')}")
                return channel
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting channel info: {e}")
            return None
