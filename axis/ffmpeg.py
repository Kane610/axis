"""Routines to convert audio into Axis-compatible format with ffmpeg."""

import asyncio
import shutil


async def to_axis_mulaw(audio_path: str, ffmpeg_path: str | None = None) -> bytes:
    """Convert media to Axis-compatible format."""
    if not ffmpeg_path:
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            err = "ffmpeg not found in PATH"
            raise Exception(err)

    args = [
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        audio_path,
        "-vn",
        "-probesize",
        "32",
        "-analyzeduration",
        "32",
        "-c:a",
        "pcm_mulaw",
        "-ab",
        "128k",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-f",
        "wav",
        "-",
    ]

    process = await asyncio.create_subprocess_exec(
        ffmpeg_path,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return stdout
