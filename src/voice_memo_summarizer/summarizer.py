"""Summarize files using Gemini via Vertex AI."""

import mimetypes
import os
from pathlib import Path

from google import genai
from google.genai import types

MODEL = "gemini-3.1-pro-preview"
# The flash-lite-preview model is only available in the global region.
GCP_LOCATION = "global"

DEFAULT_PROMPT = """\
You are a meeting notes assistant. Your task is to: 1) transcribe, 2) summarise and then, if applicable 3) provide action items from the attached recording. 
Write your summary in the same language as the audio. Use markdown headers level two (##) for the transcription, summarization, etc. Always write the transcription first, then the rest.
"""

# Extra MIME types not always in Python's default database.
_MIME_OVERRIDES: dict[str, str] = {
    ".m4a": "audio/m4a",
    ".qta": "audio/mp4",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".webm": "audio/webm",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webp": "image/webp",
    ".heic": "image/heic",
}


def guess_mime_type(path: Path) -> str:
    """Guess the MIME type for a file, with sensible defaults."""
    suffix = path.suffix.lower()
    if suffix in _MIME_OVERRIDES:
        return _MIME_OVERRIDES[suffix]
    mime, _ = mimetypes.guess_type(path.name)
    return mime or "application/octet-stream"


def make_client() -> genai.Client:
    """Create a Vertex AI Gemini client."""
    project = os.environ.get("GCP_PROJECT")
    if not project:
        raise RuntimeError("GCP_PROJECT environment variable is not set")
    return genai.Client(
        vertexai=True,
        project=project,
        location=GCP_LOCATION,
    )


def summarize(
    files: list[Path],
    prompt: str = DEFAULT_PROMPT,
    client: genai.Client | None = None,
) -> str:
    """Send files to Gemini with a prompt and return the response.

    Args:
        files: Paths to files to embed in the request (audio, images, PDFs, etc.).
        prompt: The instruction prompt.
        client: Optional pre-configured client (for testing).
    """
    if client is None:
        client = make_client()

    parts: list[types.Part | str] = [prompt]
    for file_path in files:
        mime = guess_mime_type(file_path)
        data = file_path.read_bytes()
        parts.append(types.Part.from_bytes(data=data, mime_type=mime))

    response = client.models.generate_content(
        model=MODEL,
        contents=parts,
    )
    if response.text is None:
        raise RuntimeError("Gemini returned an empty response")
    return response.text