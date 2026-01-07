from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

from config import CONFIG, DATA_DIR, OUTPUT_DIR
from pipeline.generator import QuestionItem, generate_question, shuffle_intro
from pipeline.media import blur_image, compose_long, compose_short, download_background
from pipeline.seo import build_seo
from pipeline.tts import synthesize
from pipeline.youtube import UploadRequest, upload_video
from utils.log import info, warn
from utils.rate_limit import RateLimiter
from utils.storage import read_json, write_json

USED_QUESTIONS_PATH = DATA_DIR / "used_questions.json"
RATE_LIMIT_PATH = DATA_DIR / "rate_limit.json"


def _question_hash(item: QuestionItem) -> str:
    raw = f"{item.question}|{item.answer}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _is_duplicate(item: QuestionItem) -> bool:
    used = read_json(USED_QUESTIONS_PATH, [])
    return _question_hash(item) in set(used)


def _store_question(item: QuestionItem) -> None:
    used = read_json(USED_QUESTIONS_PATH, [])
    used.append(_question_hash(item))
    write_json(USED_QUESTIONS_PATH, used)


def _generate_unique_question() -> QuestionItem:
    for _ in range(CONFIG.max_generation_attempts):
        item = generate_question()
        if not _is_duplicate(item):
            return item
    raise RuntimeError("Failed to generate a unique question")


def run_short(index: int) -> Path:
    item = _generate_unique_question()
    intro = shuffle_intro()
    background = download_background()
    blurred = blur_image(background.image_path, OUTPUT_DIR / f"background_{index}.jpg")
    audio_path = OUTPUT_DIR / f"voice_{index}.mp3"
    synthesize(f"{item.question}. {intro}", CONFIG.voice, audio_path)

    video_path = OUTPUT_DIR / f"short_{index}.mp4"
    compose_short(
        question=item.question,
        intro=intro,
        answer=item.answer,
        background_path=blurred,
        audio_path=audio_path,
        output_path=video_path,
        question_duration=CONFIG.question_duration_seconds,
        answer_duration=CONFIG.answer_duration_seconds,
    )
    _store_question(item)
    seo = build_seo(item.question, item.answer, item.category)
    upload_id = upload_video(
        UploadRequest(
            title=seo.title,
            description=seo.description,
            tags=seo.tags,
            file_path=video_path,
            privacy_status="public",
            is_short=True,
        )
    )
    info(f"Uploaded short {index}: {upload_id}")
    return video_path


def run_day() -> None:
    now = datetime.utcnow()
    limiter = RateLimiter(RATE_LIMIT_PATH, CONFIG.max_daily_uploads)
    if not limiter.can_upload(now):
        warn("Daily upload limit reached. Skipping run.")
        return

    short_paths: list[Path] = []
    for idx in range(CONFIG.shorts_per_day):
        if not limiter.can_upload(now):
            warn("Rate limit reached mid-run.")
            break
        short_paths.append(run_short(idx + 1))
        limiter.record_upload(now)

    if short_paths:
        long_path = OUTPUT_DIR / "daily_compilation.mp4"
        compose_long(short_paths, long_path)
        long_title = "Daily Quiz Shorts Compilation"
        long_description = "All today\'s quiz shorts in one video. #quiz #shorts"
        upload_id = upload_video(
            UploadRequest(
                title=long_title,
                description=long_description,
                tags=["quiz", "shorts", "compilation", "trivia"],
                file_path=long_path,
                privacy_status="public",
                is_short=False,
            )
        )
        limiter.record_upload(now)
        info(f"Uploaded long video: {upload_id}")


if __name__ == "__main__":
    run_day()
