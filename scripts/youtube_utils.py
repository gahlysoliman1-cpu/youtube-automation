import os
import logging
import httplib2
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from oauth2client.client import OAuth2Credentials

logger = logging.getLogger(__name__)

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
MAX_RETRIES = 3
RETRY_DELAY = 5

def get_authenticated_service():
    client_id = os.environ.get('YT_CLIENT_ID')
    client_secret = os.environ.get('YT_CLIENT_SECRET')
    refresh_token = os.environ.get('YT_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing YouTube OAuth credentials in environment variables")
    
    credentials = OAuth2Credentials(
        access_token=None,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        token_expiry=None,
        token_uri='https://oauth2.googleapis.com/token',
        user_agent='YouTube Shorts Automation'
    )
    
    http = httplib2.Http()
    http = credentials.authorize(http)
    
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=http, cache_discovery=False)

def upload_to_youtube(youtube, file_path, title, description, tags, is_short=True):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video file not found: {file_path}")
    
    body = {
        'snippet': {
            'title': title[:100],  # YouTube title limit
            'description': description[:5000],
            'tags': tags[:500],
            'categoryId': '24'  # Entertainment category
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    
    if is_short:
        body['status']['embeddable'] = True
        body['snippet']['description'] += "\n\n#shorts #quiz #brainteaser #viral"
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Uploading {'Short' if is_short else 'Long'} video: {title}")
            insert_request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
            )
            
            response = None
            while response is None:
                status, response = insert_request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            if 'id' in response:
                video_id = response['id']
                logger.info(f"Successfully uploaded video ID: {video_id}")
                return video_id
            else:
                raise ValueError("Upload response missing video ID")
                
        except Exception as e:
            logger.error(f"Upload attempt {attempt+1} failed: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise
