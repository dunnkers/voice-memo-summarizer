"""CLI entry point for voice-memo-summarizer."""

import argparse
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

from voice_memo_summarizer.clipboard import pick_files
from voice_memo_summarizer.summarizer import DEFAULT_PROMPT, summarize


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="voice-memo-summarizer",
        description="Summarize voice memos and other files using Gemini.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Files to summarize. Opens macOS file picker if none provided.",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        default=None,
        help="Path to a markdown file containing the prompt. Uses built-in default if omitted.",
    )
    parser.add_argument(
        "--no-clipboard",
        action="store_true",
        default=False,
        help="Do not copy the summary to the clipboard.",
    )
    return parser


def resolve_files(paths: list[Path]) -> list[Path]:
    """Get file paths from parsed args or native file picker.

    If paths are provided, use them directly. Otherwise, open a
    native macOS file picker allowing multiple file selection.
    """
    if paths:
        return [Path(str(p).strip().strip("'\"")) for p in paths]

    picked = pick_files()
    if not picked:
        print("No files selected.", file=sys.stderr)
        sys.exit(1)
    return picked


def load_prompt(prompt_file: Path | None) -> str:
    """Load prompt from a file, or return the default prompt."""
    if prompt_file is None:
        return DEFAULT_PROMPT
    if not prompt_file.exists():
        print(f"Error: prompt file not found: {prompt_file}", file=sys.stderr)
        sys.exit(1)
    return prompt_file.read_text().strip()


def copy_to_clipboard(text: str) -> None:
    """Copy text to the macOS clipboard using pbcopy."""
    subprocess.run(["pbcopy"], input=text.encode(), check=True)


def main() -> None:
    """Select files, summarize with Gemini, and output the result."""
    load_dotenv()

    args = build_parser().parse_args()
    files = resolve_files(args.files)

    for f in files:
        if not f.exists():
            print(f"Error: file not found: {f}", file=sys.stderr)
            sys.exit(1)

    total_kb = sum(f.stat().st_size for f in files) / 1024
    print(f"Selected {len(files)} file(s) ({total_kb:.0f} KB total):", file=sys.stderr)
    for f in files:
        print(f"  - {f.name}", file=sys.stderr)

    prompt = load_prompt(args.prompt_file)

    print("Sending to Gemini...", file=sys.stderr)
    try:
        summary = summarize(files, prompt=prompt)
    except Exception as e:
        print(f"Error during summarization: {e}", file=sys.stderr)
        sys.exit(1)

    print(summary)

    if not args.no_clipboard:
        copy_to_clipboard(summary)
        print("Copied to clipboard.", file=sys.stderr)


if __name__ == "__main__":
    main()
