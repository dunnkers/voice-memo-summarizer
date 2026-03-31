"""CLI entry point for voice-memo-summarizer."""

import sys
from pathlib import Path

from dotenv import load_dotenv

from voice_memo_summarizer.clipboard import pick_files
from voice_memo_summarizer.craft import upload_to_craft
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


def extract_title(summary: str) -> str:
    """Extract a title from the summary, falling back to a default."""
    for line in summary.strip().splitlines():
        if "title" in line.lower() and ":" in line:
            return line.split(":", 1)[1].strip().strip("*").strip()
    return "Voice Memo Summary"


def main() -> None:
    """Select files, get a prompt, summarize, and optionally upload to Craft."""
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

    answer = input("Upload to Craft? [y/N] ").strip().lower()
    if answer != "y":
        return

    title = extract_title(summary)
    try:
        dated_title = upload_to_craft(title, summary)
        print(f"Uploaded to Craft: {dated_title}")
    except Exception as e:
        print(f"Error uploading to Craft: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()