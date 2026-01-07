import asyncio
from pathlib import Path

import edge_tts
from gtts import gTTS

from pipeline.fallback import try_chain


async def _edge_tts(text: str, voice: str, output_path: Path) -> Path:
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(str(output_path))
    return output_path


def _edge_tts_sync(text: str, voice: str, output_path: Path) -> Path:
    return asyncio.run(_edge_tts(text, voice, output_path))


def _gtts_sync(text: str, output_path: Path) -> Path:
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(str(output_path))
    return output_path


def synthesize(text: str, voice: str, output_path: Path) -> Path:
    handlers = [
        lambda: _edge_tts_sync(text, voice, output_path),
        lambda: _gtts_sync(text, output_path),
    ]
    return try_chain("TTS", handlers)
