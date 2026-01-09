from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from yt_auto.config import Config
from yt_auto.llm import QuizItem
from yt_auto.utils import ensure_dir, wrap_lines


def _run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"command_failed: {' '.join(cmd[:6])} ... | err={p.stderr[:700]}")


def ffprobe_duration_seconds(media_path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(media_path),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe_failed: {p.stderr[:500]}")
    try:
        return float(p.stdout.strip())
    except Exception as e:
        raise RuntimeError(f"ffprobe_bad_duration: {p.stdout!r}") from e


def build_short(cfg: Config, quiz: QuizItem, bg_image: Path, tts_wav: Path, out_mp4: Path, seed: int) -> dict:
    ensure_dir(out_mp4.parent)

    audio_dur = ffprobe_duration_seconds(tts_wav)
    countdown = float(cfg.countdown_seconds)
    reveal = float(cfg.answer_reveal_seconds)

    total = max(3.0, audio_dur + countdown + reveal)
    answer_start = audio_dur + countdown
    answer_end = answer_start + reveal

    q_txt = out_mp4.with_suffix(".question.txt")
    a_txt = out_mp4.with_suffix(".answer.txt")

    q_wrapped = wrap_lines(quiz.question, width=28, max_lines=4)
    a_wrapped = wrap_lines(quiz.answer, width=24, max_lines=3)

    q_txt.write_text(q_wrapped, encoding="utf-8")
    a_txt.write_text(a_wrapped, encoding="utf-8")

    vfilter = (
        f"[0:v]"
        f"scale={cfg.short_w}:{cfg.short_h}:force_original_aspect_ratio=increase,"
        f"crop={cfg.short_w}:{cfg.short_h},"
        f"boxblur=20:1,"
        f"eq=brightness=-0.05:contrast=1.15:saturation=1.08"
        f"[v0];"
        f"[v0]drawtext=fontfile={cfg.fontfile}:textfile={q_txt}:reload=1:"
        f"fontsize=64:fontcolor=white:x=(w-text_w)/2:y=(h*0.33-text_h/2):"
        f"line_spacing=12:box=1:boxcolor=black@0.55:boxborderw=28:"
        f"enable=lt(t\\,{answer_start:.3f})"
        f"[v1];"
        f"[v1]drawtext=fontfile={cfg.fontfile}:"
        f"text=%{{eif\\:max(0\\,ceil({cfg.countdown_seconds}-(t-{audio_dur:.3f})))\\:d}}:"
        f"fontsize=100:fontcolor=white:x=(w-text_w)/2:y=(h*0.79-text_h/2):"
        f"box=1:boxcolor=black@0.45:boxborderw=18:"
        f"enable=between(t\\,{audio_dur:.3f}\\,{audio_dur + countdown:.3f})"
        f"[v2];"
        f"[v2]drawtext=fontfile={cfg.fontfile}:textfile={a_txt}:reload=1:"
        f"fontsize=84:fontcolor=white:x=(w-text_w)/2:y=(h*0.46-text_h/2):"
        f"line_spacing=12:box=1:boxcolor=black@0.65:boxborderw=30:"
        f"enable=between(t\\,{answer_start:.3f}\\,{answer_end:.3f})"
        f"[v]"
    )

    afilter = f"[1:a]apad,atrim=0:{total:.3f}[a]"

    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(bg_image),
        "-i",
        str(tts_wav),
        "-filter_complex",
        f"{vfilter};{afilter}",
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-t",
        f"{total:.3f}",
        "-r",
        str(cfg.fps),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        str(out_mp4),
    ]
    _run(cmd)

    q_txt.unlink(missing_ok=True)
    a_txt.unlink(missing_ok=True)

    return {
        "audio_dur": audio_dur,
        "total_dur": total,
        "answer_start": answer_start,
        "answer_end": answer_end,
        "seed": seed,
    }


def _make_intro(cfg: Config, out_path: Path, title: str) -> None:
    ensure_dir(out_path.parent)
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=black:s={cfg.long_w}x{cfg.long_h}:d=2.2",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=44100:cl=stereo",
        "-filter_complex",
        f"[0:v]drawtext=fontfile={cfg.fontfile}:"
        f"text='{title}':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:"
        f"box=1:boxcolor=black@0.35:boxborderw=24[v]",
        "-map",
        "[v]",
        "-map",
        "1:a",
        "-shortest",
        "-r",
        str(cfg.fps),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        str(out_path),
    ]
    _run(cmd)


def _convert_vertical_to_16x9(cfg: Config, in_path: Path, out_path: Path) -> None:
    ensure_dir(out_path.parent)
    filt = (
        "[0:v]split=2[v1][v2];"
        f"[v1]scale={cfg.long_w}:{cfg.long_h}:force_original_aspect_ratio=increase,"
        f"crop={cfg.long_w}:{cfg.long_h},boxblur=20:1[bg];"
        f"[v2]scale=-2:{cfg.long_h}:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(in_path),
        "-filter_complex",
        filt,
        "-map",
        "[v]",
        "-map",
        "0:a?",
        "-r",
        str(cfg.fps),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        str(out_path),
    ]
    _run(cmd)


def build_long_compilation(cfg: Config, clips: list[Path], out_mp4: Path, date_yyyymmdd: str) -> None:
    ensure_dir(out_mp4.parent)

    intro = cfg.out_dir / f"intro_{date_yyyymmdd}.mp4"
    _make_intro(cfg, intro, f"Daily Quiz Compilation • {date_yyyymmdd}")

    processed: list[Path] = [intro]
    for i, c in enumerate(clips, start=1):
        outp = cfg.out_dir / f"clip16x9_{date_yyyymmdd}_{i}.mp4"
        _convert_vertical_to_16x9(cfg, c, outp)
        processed.append(outp)

    concat_list = cfg.out_dir / f"concat_{date_yyyymmdd}.txt"
    lines = []
    for p in processed:
        lines.append(f"file '{p.resolve()}'")
    concat_list.write_text("\n".join(lines) + "\n", encoding="utf-8")

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list),
        "-c",
        "copy",
        str(out_mp4),
    ]
    _run(cmd)

    concat_list.unlink(missing_ok=True)
