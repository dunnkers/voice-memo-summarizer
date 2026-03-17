"""Summarize audio using Gemini via Vertex AI."""

import os
from pathlib import Path

from google import genai
from google.genai import types

MODEL = "gemini-3.1-flash-lite-preview"
# The flash-lite-preview model is only available in the global region.
GCP_LOCATION = "global"

PROMPT = """\
You are a meeting notes assistant. Summarize this voice memo concisely.

Structure your summary as:
- **Title**: A short descriptive title
- **Key Points**: Bullet list of main topics discussed
- **Action Items**: Any tasks or follow-ups mentioned (if any)
- **Summary**: 2-3 sentence overview

Keep it concise and actionable.\
"""


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


def summarize_audio(audio_path: Path, client: genai.Client | None = None) -> str:
    """Send an audio file to Gemini and return the summary.

    Args:
        audio_path: Path to an .m4a audio file.
        client: Optional pre-configured client (for testing).
    """
    if client is None:
        client = make_client()

    audio_bytes = audio_path.read_bytes()
    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/m4a")

    response = client.models.generate_content(
        model=MODEL,
        contents=[PROMPT, audio_part],
    )
    if response.text is None:
        raise RuntimeError("Gemini returned an empty response")
    return response.text
