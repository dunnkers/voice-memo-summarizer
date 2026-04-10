"""Tests for the Gemini summarizer."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from voice_memo_summarizer.summarizer import (
    DEFAULT_PROMPT,
    MODEL,
    guess_mime_type,
    make_client,
    summarize,
)


class TestGuessMimeType:
    def test_m4a(self, tmp_path: Path) -> None:
        assert guess_mime_type(tmp_path / "file.m4a") == "audio/m4a"

    def test_mp3(self, tmp_path: Path) -> None:
        assert guess_mime_type(tmp_path / "file.mp3") == "audio/mpeg"

    def test_mp4(self, tmp_path: Path) -> None:
        assert guess_mime_type(tmp_path / "file.mp4") == "video/mp4"

    def test_unknown_extension(self, tmp_path: Path) -> None:
        result = guess_mime_type(tmp_path / "file.xyz123")
        assert result == "application/octet-stream"


class TestMakeClient:
    def test_raises_without_gcp_project(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GCP_PROJECT", raising=False)
        with pytest.raises(RuntimeError, match="GCP_PROJECT"):
            make_client()


class TestSummarize:
    def test_calls_generate_content(self, tmp_path: Path) -> None:
        audio = tmp_path / "test.m4a"
        audio.write_bytes(b"fake audio data")

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value.text = (
            "## Summary\nMeeting about X."
        )

        result = summarize([audio], client=mock_client)

        assert result == "## Summary\nMeeting about X."
        mock_client.models.generate_content.assert_called_once()

        call_kwargs = mock_client.models.generate_content.call_args
        assert call_kwargs.kwargs["model"] == MODEL
        contents = call_kwargs.kwargs["contents"]
        assert len(contents) == 2  # prompt + audio part

    def test_uses_default_prompt(self, tmp_path: Path) -> None:
        audio = tmp_path / "test.m4a"
        audio.write_bytes(b"fake")

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value.text = "ok"

        summarize([audio], client=mock_client)

        contents = mock_client.models.generate_content.call_args.kwargs["contents"]
        assert contents[0] == DEFAULT_PROMPT

    def test_uses_custom_prompt(self, tmp_path: Path) -> None:
        audio = tmp_path / "test.m4a"
        audio.write_bytes(b"fake")

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value.text = "ok"

        summarize([audio], prompt="Custom prompt", client=mock_client)

        contents = mock_client.models.generate_content.call_args.kwargs["contents"]
        assert contents[0] == "Custom prompt"

    def test_multiple_files(self, tmp_path: Path) -> None:
        files = []
        for name in ["a.m4a", "b.mp3"]:
            f = tmp_path / name
            f.write_bytes(b"data")
            files.append(f)

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value.text = "combined"

        result = summarize(files, client=mock_client)

        assert result == "combined"
        contents = mock_client.models.generate_content.call_args.kwargs["contents"]
        assert len(contents) == 3  # prompt + 2 files

    def test_reads_file_bytes(self, tmp_path: Path) -> None:
        audio = tmp_path / "memo.m4a"
        audio.write_bytes(b"\x00\x01\x02\x03")

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value.text = "summary"

        summarize([audio], client=mock_client)

        contents = mock_client.models.generate_content.call_args.kwargs["contents"]
        audio_part = contents[1]
        assert audio_part.inline_data.data == b"\x00\x01\x02\x03"
        assert audio_part.inline_data.mime_type == "audio/m4a"

    def test_raises_on_empty_response(self, tmp_path: Path) -> None:
        audio = tmp_path / "test.m4a"
        audio.write_bytes(b"fake")

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value.text = None

        with pytest.raises(RuntimeError, match="empty response"):
            summarize([audio], client=mock_client)
