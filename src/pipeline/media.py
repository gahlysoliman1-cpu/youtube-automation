from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import requests
from moviepy.editor import AudioFileClip, CompositeVideoClip, ImageClip, TextClip, VideoFileClip, concatenate_videoclips
from moviepy.video.fx.all import resize
from PIL import Image, ImageFilter

from config import KEYS
from pipeline.fallback import try_chain


@dataclass(frozen=True)
class BackgroundAsset:
    image_path: Path
    source: str


def _fetch_unsplash() -> BackgroundAsset:
    if not KEYS.unsplash_access_key:
        raise RuntimeError("Missing UNSPLASH_ACCESS_KEY")
    url = "https://api.unsplash.com/photos/random"
    params = {"query": "abstract texture", "orientation": "portrait"}
    headers = {"Authorization": f"Client-ID {KEYS.unsplash_access_key}"}
    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    image_url = response.json()["urls"]["regular"]
    image_data = requests.get(image_url, timeout=30)
    image_data.raise_for_status()
    path = Path("output") / "background.jpg"
    path.write_bytes(image_data.content)
    return BackgroundAsset(path, "unsplash")


def _fetch_pexels() -> BackgroundAsset:
    if not KEYS.pexels_api_key:
        raise RuntimeError("Missing PEXELS_API_KEY")
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": KEYS.pexels_api_key}
    params = {"query": "abstract", "orientation": "portrait", "per_page": 1}
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    image_url = response.json()["photos"][0]["src"]["large"]
    image_data = requests.get(image_url, timeout=30)
    image_data.raise_for_status()
    path = Path("output") / "background.jpg"
    path.write_bytes(image_data.content)
    return BackgroundAsset(path, "pexels")


def _fetch_pixabay() -> BackgroundAsset:
    if not KEYS.pixabay_api_key:
        raise RuntimeError("Missing PIXABAY_API_KEY")
    url = "https://pixabay.com/api/"
    params = {
        "key": KEYS.pixabay_api_key,
        "q": "abstract",
        "orientation": "vertical",
        "image_type": "photo",
        "per_page": 3,
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    hits = response.json()["hits"]
    if not hits:
        raise RuntimeError("Pixabay returned no images")
    image_url = hits[0]["largeImageURL"]
    image_data = requests.get(image_url, timeout=30)
    image_data.raise_for_status()
    path = Path("output") / "background.jpg"
    path.write_bytes(image_data.content)
    return BackgroundAsset(path, "pixabay")


def download_background() -> BackgroundAsset:
    handlers: list[Callable[[], BackgroundAsset]] = [_fetch_unsplash, _fetch_pexels, _fetch_pixabay]
    return try_chain("Background", handlers)


def blur_image(input_path: Path, output_path: Path) -> Path:
    image = Image.open(input_path)
    blurred = image.filter(ImageFilter.GaussianBlur(radius=8))
    blurred.save(output_path)
    return output_path


def compose_short(
    question: str,
    intro: str,
    answer: str,
    background_path: Path,
    audio_path: Path,
    output_path: Path,
    question_duration: int,
    answer_duration: int,
) -> Path:
    base_clip = ImageClip(str(background_path)).set_duration(question_duration + answer_duration)
    base_clip = resize(base_clip, height=1920)

    question_clip = (
        TextClip(question, fontsize=90, color="white", font="DejaVu-Sans")
        .set_position("center")
        .set_duration(question_duration)
    )
    intro_clip = (
        TextClip(intro, fontsize=55, color="#F8F8F8", font="DejaVu-Sans")
        .set_position(("center", 1450))
        .set_duration(question_duration)
    )
    answer_clip = (
        TextClip(answer, fontsize=90, color="#FDE047", font="DejaVu-Sans")
        .set_position("center")
        .set_start(question_duration)
        .set_duration(answer_duration)
    )
    timer_clips = []
    for second in range(question_duration):
        remaining = str(question_duration - second)
        timer_clips.append(
            TextClip(remaining, fontsize=80, color="#22D3EE", font="DejaVu-Sans")
            .set_position(("center", 1650))
            .set_start(second)
            .set_duration(1)
        )

    audio = AudioFileClip(str(audio_path)).set_duration(question_duration)
    final = CompositeVideoClip([base_clip, question_clip, intro_clip, answer_clip, *timer_clips]).set_audio(audio)
    final.write_videofile(str(output_path), fps=30, codec="libx264", audio_codec="aac")
    return output_path


def compose_long(short_paths: list[Path], output_path: Path) -> Path:
    clips = [VideoFileClip(str(path)) for path in short_paths]
    montage = concatenate_videoclips(clips, method="compose")
    montage.write_videofile(str(output_path), fps=30, codec="libx264", audio_codec="aac")
    return output_path
