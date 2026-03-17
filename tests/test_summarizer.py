"""Tests for the Gemini summarizer."""

from pathlib import Path
from unittest.mock import MagicMock

from voice_memo_summarizer.summarizer import MODEL, summarize_audio


def test_summarize_audio_calls_generate_content(tmp_path: Path) -> None:
    audio_file = tmp_path / "test.m4a"
    audio_file.write_bytes(b"fake audio data")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "## Summary\nThis was a meeting about X."
    mock_client.models.generate_content.return_value = mock_response

    result = summarize_audio(audio_file, client=mock_client)

    assert result == "## Summary\nThis was a meeting about X."
    mock_client.models.generate_content.assert_called_once()

    call_kwargs = mock_client.models.generate_content.call_args
    assert call_kwargs.kwargs["model"] == MODEL
    contents = call_kwargs.kwargs["contents"]
    assert len(contents) == 2  # prompt + audio part


def test_summarize_audio_reads_file_bytes(tmp_path: Path) -> None:
    audio_file = tmp_path / "memo.m4a"
    audio_file.write_bytes(b"\x00\x01\x02\x03")

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value.text = "summary"

    summarize_audio(audio_file, client=mock_client)

    # Verify the audio part was created from the file bytes.
    contents = mock_client.models.generate_content.call_args.kwargs["contents"]
    audio_part = contents[1]
    assert audio_part.inline_data.data == b"\x00\x01\x02\x03"
    assert audio_part.inline_data.mime_type == "audio/m4a"
