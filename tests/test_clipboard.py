"""Tests for the macOS file picker."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from voice_memo_summarizer.clipboard import pick_files


@patch("voice_memo_summarizer.clipboard.subprocess.run")
def test_pick_files_returns_paths(mock_run: MagicMock) -> None:
    mock_run.return_value.stdout = "/Users/test/memo.m4a\n/Users/test/other.mp3\n"
    result = pick_files()
    assert result == [Path("/Users/test/memo.m4a"), Path("/Users/test/other.mp3")]
    mock_run.assert_called_once()


@patch("voice_memo_summarizer.clipboard.subprocess.run")
def test_pick_files_returns_empty_on_cancel(mock_run: MagicMock) -> None:
    mock_run.return_value.stdout = "\n"
    result = pick_files()
    assert result == []


@patch("voice_memo_summarizer.clipboard.subprocess.run")
def test_pick_files_single_file(mock_run: MagicMock) -> None:
    mock_run.return_value.stdout = "/Users/test/memo.m4a\n"
    result = pick_files()
    assert result == [Path("/Users/test/memo.m4a")]


@patch("voice_memo_summarizer.clipboard.subprocess.run")
def test_pick_files_uses_custom_dir(mock_run: MagicMock) -> None:
    mock_run.return_value.stdout = "/some/path.m4a\n"
    custom_dir = Path("/custom/dir")
    pick_files(default_dir=custom_dir)
    script = mock_run.call_args.args[0][2]
    assert "/custom/dir" in script
