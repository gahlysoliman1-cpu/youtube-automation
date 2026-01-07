from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import KEYS


@dataclass(frozen=True)
class UploadRequest:
    title: str
    description: str
    tags: list[str]
    file_path: Path
    privacy_status: str = "public"
    is_short: bool = True


def _build_credentials() -> Credentials:
    if not (KEYS.yt_client_id and KEYS.yt_client_secret and KEYS.yt_refresh_token):
        raise RuntimeError("Missing YouTube OAuth credentials")
    return Credentials(
        None,
        refresh_token=KEYS.yt_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=KEYS.yt_client_id,
        client_secret=KEYS.yt_client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )


def upload_video(request: UploadRequest) -> str:
    credentials = _build_credentials()
    youtube = build("youtube", "v3", credentials=credentials)

    body: dict[str, Any] = {
        "snippet": {
            "title": request.title,
            "description": request.description,
            "tags": request.tags,
            "categoryId": "24",
        },
        "status": {"privacyStatus": request.privacy_status},
    }
    media = MediaFileUpload(str(request.file_path), chunksize=-1, resumable=True)
    response = (
        youtube.videos()
        .insert(part=",".join(body.keys()), body=body, media_body=media)
        .execute()
    )
    return response["id"]
