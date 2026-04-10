"""Integration tests that run the CLI against a real audio file and Gemini API.

Requires GCP credentials and a project with Vertex AI enabled.
Skipped automatically when GCP_PROJECT is not set.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent / "data"
AUDIO_FILE = DATA_DIR / "google-adk-is-nice.m4a"

needs_gcp = pytest.mark.skipif(
    not os.environ.get("GCP_PROJECT"),
    reason="GCP_PROJECT not set — skipping integration tests",
)


class TestCLIIntegration:
    def test_missing_file_exits_nonzero(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "voice_memo_summarizer",
                "--no-clipboard",
                "/nonexistent/file.m4a",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode != 0
        assert "file not found" in result.stderr

    def test_stderr_shows_file_info(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "voice_memo_summarizer",
                "--no-clipboard",
                str(AUDIO_FILE),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert "Selected 1 file(s)" in result.stderr
        assert "google-adk-is-nice.m4a" in result.stderr

    @needs_gcp
    def test_summarize_audio_file(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "voice_memo_summarizer",
                "--no-clipboard",
                str(AUDIO_FILE),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0
        assert "Sending to Gemini..." in result.stderr

    @needs_gcp
    def test_output_contains_markdown(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "voice_memo_summarizer",
                "--no-clipboard",
                str(AUDIO_FILE),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0
        assert "##" in result.stdout

    @needs_gcp
    def test_custom_prompt(self, tmp_path: Path) -> None:
        prompt_file = tmp_path / "prompt.md"
        prompt_file.write_text("Transcribe the audio. Respond in English.")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "voice_memo_summarizer",
                "--no-clipboard",
                "--prompt-file",
                str(prompt_file),
                str(AUDIO_FILE),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0
