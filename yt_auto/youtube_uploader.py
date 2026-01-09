from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from yt_auto.config import YouTubeOAuth
from yt_auto.utils import RetryPolicy, backoff_sleep_s


@dataclass(frozen=True)
class UploadResult:
    video_id: str


class YouTubeUploader:
    def __init__(self, oauth_list: list[YouTubeOAuth]) -> None:
        if not oauth_list:
            raise RuntimeError("missing_youtube_oauth_credentials")
        self.oauth_list = oauth_list

    def _service_for(self, oauth: YouTubeOAuth):
        creds = Credentials(
            token=None,
            refresh_token=oauth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=oauth.client_id,
            client_secret=oauth.client_secret,
            scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"],
        )
        creds.refresh(Request())
        return build("youtube", "v3", credentials=creds, cache_discovery=False)

    def upload_video(
        self,
        file_path: Path,
        title: str,
        description: str,
        tags: list[str],
        category_id: str,
        privacy_status: str,
        made_for_kids: bool,
        default_language: str = "en",
        default_audio_language: str = "en",
    ) -> UploadResult:
        policy = RetryPolicy(max_attempts=5, base_sleep_s=1.2, max_sleep_s=12.0)
        last_err: Exception | None = None

        for oauth in self.oauth_list:
            service = self._service_for(oauth)
            for attempt in range(1, policy.max_attempts + 1):
                try:
                    body: dict[str, Any] = {
                        "snippet": {
                            "title": title,
                            "description": description,
                            "tags": tags,
                            "categoryId": category_id,
                            "defaultLanguage": default_language,
                            "defaultAudioLanguage": default_audio_language,
                        },
                        "status": {
                            "privacyStatus": privacy_status,
                            "selfDeclaredMadeForKids": bool(made_for_kids),
                        },
                    }

                    media = MediaFileUpload(str(file_path), chunksize=-1, resumable=True)
                    req = service.videos().insert(part="snippet,status", body=body, media_body=media)
                    resp = None
                    while resp is None:
                        status, resp = req.next_chunk()
                        if status:
                            _ = status.progress()

                    vid = resp.get("id") if isinstance(resp, dict) else None
                    if not isinstance(vid, str) or not vid.strip():
                        raise RuntimeError("youtube_upload_missing_video_id")

                    return UploadResult(video_id=vid.strip())
                except HttpError as e:
                    last_err = e
                    time.sleep(backoff_sleep_s(attempt, policy))
                except Exception as e:
                    last_err = e
                    time.sleep(backoff_sleep_s(attempt, policy))

        raise RuntimeError(f"youtube_upload_failed: {last_err!r}")

    def set_thumbnail(self, video_id: str, thumbnail_path: Path) -> None:
        policy = RetryPolicy(max_attempts=4, base_sleep_s=1.0, max_sleep_s=10.0)
        last_err: Exception | None = None

        for oauth in self.oauth_list:
            service = self._service_for(oauth)
            for attempt in range(1, policy.max_attempts + 1):
                try:
                    media = MediaFileUpload(str(thumbnail_path))
                    req = service.thumbnails().set(videoId=video_id, media_body=media)
                    req.execute()
                    return
                except Exception as e:
                    last_err = e
                    time.sleep(backoff_sleep_s(attempt, policy))

        raise RuntimeError(f"youtube_set_thumbnail_failed: {last_err!r}")
