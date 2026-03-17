"""Tests for the macOS file picker."""

from pathlib import Path
from unittest.mock import patch

from voice_memo_summarizer.clipboard import pick_audio_file


@patch("voice_memo_summarizer.clipboard.subprocess.run")
def test_pick_audio_file_returns_path(mock_run):
    mock_run.return_value.stdout = "/Users/test/memo.m4a\n"
    result = pick_audio_file()
    assert result == Path("/Users/test/memo.m4a")
    mock_run.assert_called_once()


@patch("voice_memo_summarizer.clipboard.subprocess.run")
def test_pick_audio_file_returns_none_on_cancel(mock_run):
    mock_run.return_value.stdout = "\n"
    result = pick_audio_file()
    assert result is None


@patch("voice_memo_summarizer.clipboard.subprocess.run")
def test_pick_audio_file_uses_default_dir(mock_run):
    mock_run.return_value.stdout = "/some/path.m4a\n"
    custom_dir = Path("/custom/dir")
    pick_audio_file(default_dir=custom_dir)
    script = mock_run.call_args.args[0][2]
    assert "/custom/dir" in script
