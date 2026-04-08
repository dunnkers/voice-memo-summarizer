"""CLI entry point for voice-memo-summarizer."""

import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

from voice_memo_summarizer.clipboard import pick_files
from voice_memo_summarizer.summarizer import DEFAULT_PROMPT, summarize


def resolve_files(args: list[str]) -> list[Path]:
    """Get file paths from CLI args or native file picker.

    If CLI arguments are provided, use them directly. Otherwise, open a
    native macOS file picker allowing multiple file selection.
    """
    if len(args) > 1:
        paths = []
        for arg in args[1:]:
            cleaned = arg.strip().strip("'\"")
            paths.append(Path(cleaned))
        return paths

    paths = pick_files()
    if not paths:
        print("No files selected.", file=sys.stderr)
        sys.exit(1)
    return paths


def ask_prompt() -> str:
    """Ask the user for a custom prompt, defaulting to the built-in one."""
    print(f"Default prompt:\n  {DEFAULT_PROMPT.strip()}\n")
    custom = input("Enter custom prompt (or press Enter to use default): ").strip()
    return custom if custom else DEFAULT_PROMPT


def copy_to_clipboard(text: str) -> None:
    """Copy text to the macOS clipboard using pbcopy."""
    subprocess.run(["pbcopy"], input=text.encode(), check=True)


def main() -> None:
    """Select files, get a prompt, summarize, and optionally copy to clipboard."""
    load_dotenv()
    files = resolve_files(sys.argv)

    for f in files:
        if not f.exists():
            print(f"Error: file not found: {f}", file=sys.stderr)
            sys.exit(1)

    total_kb = sum(f.stat().st_size for f in files) / 1024
    print(f"Selected {len(files)} file(s) ({total_kb:.0f} KB total):")
    for f in files:
        print(f"  - {f.name}")
    print()

    prompt = ask_prompt()
    print()

    print("Sending to Gemini...")
    try:
        summary = summarize(files, prompt=prompt)
    except Exception as e:
        print(f"Error during summarization: {e}", file=sys.stderr)
        sys.exit(1)

    print()
    print(summary)
    print()

    answer = input("Copy note to clipboard? [y/N] ").strip().lower()
    if answer == "y":
        copy_to_clipboard(summary)
        print("Copied to clipboard.")


if __name__ == "__main__":
    main()