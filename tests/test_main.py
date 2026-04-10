"""Tests for the CLI entry point."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voice_memo_summarizer.__main__ import (
    build_parser,
    copy_to_clipboard,
    load_prompt,
    main,
    resolve_files,
)
from voice_memo_summarizer.summarizer import DEFAULT_PROMPT


class TestBuildParser:
    def test_parses_files(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["a.m4a", "b.m4a"])
        assert args.files == [Path("a.m4a"), Path("b.m4a")]

    def test_no_files(self) -> None:
        parser = build_parser()
        args = parser.parse_args([])
        assert args.files == []

    def test_prompt_file(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--prompt-file", "p.md", "a.m4a"])
        assert args.prompt_file == Path("p.md")

    def test_no_clipboard_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--no-clipboard", "a.m4a"])
        assert args.no_clipboard is True

    def test_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["a.m4a"])
        assert args.prompt_file is None
        assert args.no_clipboard is False


class TestResolveFiles:
    def test_returns_paths_when_provided(self) -> None:
        paths = resolve_files([Path("/path/to/memo.m4a")])
        assert paths == [Path("/path/to/memo.m4a")]

    def test_strips_quotes(self) -> None:
        paths = resolve_files([Path("'/path/to/memo.m4a'")])
        assert paths == [Path("/path/to/memo.m4a")]

    def test_opens_picker_when_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "voice_memo_summarizer.__main__.pick_files",
            lambda: [Path("/picked/file.m4a")],
        )
        paths = resolve_files([])
        assert paths == [Path("/picked/file.m4a")]

    def test_exits_when_picker_cancelled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("voice_memo_summarizer.__main__.pick_files", lambda: [])
        with pytest.raises(SystemExit):
            resolve_files([])


class TestLoadPrompt:
    def test_returns_default_when_none(self) -> None:
        assert load_prompt(None) == DEFAULT_PROMPT

    def test_reads_from_file(self, tmp_path: Path) -> None:
        prompt_file = tmp_path / "prompt.md"
        prompt_file.write_text("Custom prompt here\n")
        assert load_prompt(prompt_file) == "Custom prompt here"

    def test_exits_on_missing_file(self) -> None:
        with pytest.raises(SystemExit):
            load_prompt(Path("/nonexistent/prompt.md"))


class TestCopyToClipboard:
    @patch("voice_memo_summarizer.__main__.subprocess.run")
    def test_calls_pbcopy(self, mock_run: MagicMock) -> None:
        copy_to_clipboard("hello")
        mock_run.assert_called_once_with(["pbcopy"], input=b"hello", check=True)


class TestMain:
    def test_exits_on_missing_file(self, tmp_path: Path) -> None:
        fake_path = str(tmp_path / "nonexistent.m4a")
        with (
            patch.object(sys, "argv", ["prog", fake_path]),
            pytest.raises(SystemExit),
        ):
            main()

    def test_outputs_summary_to_stdout(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        audio = tmp_path / "test.m4a"
        audio.write_bytes(b"fake audio")

        mock_summary = "## Summary\nTest summary."
        with (
            patch.object(sys, "argv", ["prog", "--no-clipboard", str(audio)]),
            patch(
                "voice_memo_summarizer.__main__.summarize",
                return_value=mock_summary,
            ),
            patch("voice_memo_summarizer.__main__.load_dotenv"),
        ):
            main()

        captured = capsys.readouterr()
        assert captured.out.strip() == mock_summary
        assert "Sending to Gemini..." in captured.err

    def test_copies_to_clipboard_by_default(self, tmp_path: Path) -> None:
        audio = tmp_path / "test.m4a"
        audio.write_bytes(b"fake audio")

        with (
            patch.object(sys, "argv", ["prog", str(audio)]),
            patch(
                "voice_memo_summarizer.__main__.summarize",
                return_value="summary",
            ),
            patch("voice_memo_summarizer.__main__.load_dotenv"),
            patch("voice_memo_summarizer.__main__.copy_to_clipboard") as mock_clip,
        ):
            main()

        mock_clip.assert_called_once_with("summary")

    def test_no_clipboard_skips_copy(self, tmp_path: Path) -> None:
        audio = tmp_path / "test.m4a"
        audio.write_bytes(b"fake audio")

        with (
            patch.object(sys, "argv", ["prog", "--no-clipboard", str(audio)]),
            patch(
                "voice_memo_summarizer.__main__.summarize",
                return_value="summary",
            ),
            patch("voice_memo_summarizer.__main__.load_dotenv"),
            patch("voice_memo_summarizer.__main__.copy_to_clipboard") as mock_clip,
        ):
            main()

        mock_clip.assert_not_called()

    def test_uses_custom_prompt_file(self, tmp_path: Path) -> None:
        audio = tmp_path / "test.m4a"
        audio.write_bytes(b"fake audio")
        prompt = tmp_path / "prompt.md"
        prompt.write_text("Custom prompt")

        with (
            patch.object(
                sys,
                "argv",
                [
                    "prog",
                    "--no-clipboard",
                    "--prompt-file",
                    str(prompt),
                    str(audio),
                ],
            ),
            patch(
                "voice_memo_summarizer.__main__.summarize",
                return_value="result",
            ) as mock_summarize,
            patch("voice_memo_summarizer.__main__.load_dotenv"),
        ):
            main()

        mock_summarize.assert_called_once()
        assert mock_summarize.call_args.kwargs["prompt"] == "Custom prompt"
