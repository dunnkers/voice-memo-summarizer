"""Tests for the CLI entry point."""

from pathlib import Path

import pytest

from voice_memo_summarizer.__main__ import extract_title, resolve_audio_path


class TestResolveAudioPath:
    def test_from_cli_arg(self) -> None:
        path = resolve_audio_path(["prog", "/path/to/memo.m4a"])
        assert path == Path("/path/to/memo.m4a")

    def test_strips_quotes(self) -> None:
        path = resolve_audio_path(["prog", "'/path/to/memo.m4a'"])
        assert path == Path("/path/to/memo.m4a")

    def test_strips_whitespace(self) -> None:
        path = resolve_audio_path(["prog", "  /path/to/memo.m4a  "])
        assert path == Path("/path/to/memo.m4a")

    def test_opens_file_picker_when_no_arg(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "voice_memo_summarizer.__main__.pick_audio_file",
            lambda: Path("/picked/file.m4a"),
        )
        path = resolve_audio_path(["prog"])
        assert path == Path("/picked/file.m4a")

    def test_exits_when_picker_cancelled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "voice_memo_summarizer.__main__.pick_audio_file", lambda: None
        )
        with pytest.raises(SystemExit, match="1"):
            resolve_audio_path(["prog"])


class TestExtractTitle:
    def test_extracts_title_from_summary(self) -> None:
        summary = "- **Title**: Weekly Standup\n- **Key Points**: ..."
        assert extract_title(summary) == "Weekly Standup"

    def test_fallback_when_no_title(self) -> None:
        assert extract_title("Just some text without structure") == "Voice Memo Summary"

    def test_strips_markdown_formatting(self) -> None:
        summary = "- **Title**: **Project Review**\n"
        assert extract_title(summary) == "Project Review"


class TestMainValidation:
    def test_exits_on_missing_file(self, tmp_path: Path) -> None:
        """main() should exit with code 1 for non-existent files."""
        import sys
        from unittest.mock import patch

        from voice_memo_summarizer.__main__ import main

        fake_path = str(tmp_path / "nonexistent.m4a")
        with (
            patch.object(sys, "argv", ["prog", fake_path]),
            pytest.raises(SystemExit, match="1"),
        ):
            main()

    def test_exits_on_wrong_extension(self, tmp_path: Path) -> None:
        """main() should exit with code 1 for non-.m4a files."""
        import sys
        from unittest.mock import patch

        from voice_memo_summarizer.__main__ import main

        txt_file = tmp_path / "notes.txt"
        txt_file.write_text("not audio")
        with (
            patch.object(sys, "argv", ["prog", str(txt_file)]),
            pytest.raises(SystemExit, match="1"),
        ):
            main()
