"""CLI entry point for voice-memo-summarizer."""

import sys
from pathlib import Path

from dotenv import load_dotenv

from voice_memo_summarizer.clipboard import pick_audio_file
from voice_memo_summarizer.craft import upload_to_craft
from voice_memo_summarizer.summarizer import summarize_audio


def resolve_audio_path(args: list[str]) -> Path:
    """Get the audio file path from CLI args or native file picker.

    If a CLI argument is provided, use it directly. Otherwise, open a
    native macOS file picker defaulting to the Voice Memos directory.
    """
    if len(args) > 1:
        # Drag-and-drop into terminal can add quotes or trailing whitespace.
        cleaned = args[1].strip().strip("'\"")
        return Path(cleaned)

    path = pick_audio_file()
    if path is None:
        print("No file selected.", file=sys.stderr)
        sys.exit(1)
    return path


def extract_title(summary: str) -> str:
    """Extract a title from the summary, falling back to a default."""
    for line in summary.strip().splitlines():
        if "title" in line.lower() and ":" in line:
            return line.split(":", 1)[1].strip().strip("*").strip()
    return "Voice Memo Summary"


def main() -> None:
    """Find a voice memo, summarize it, and optionally upload to Craft."""
    load_dotenv()
    audio_path = resolve_audio_path(sys.argv)

    if not audio_path.exists():
        print(f"Error: file not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    if audio_path.suffix.lower() != ".m4a":
        print(f"Error: expected .m4a file, got {audio_path.suffix}", file=sys.stderr)
        sys.exit(1)

    size_kb = audio_path.stat().st_size / 1024
    print(f"Voice memo: {audio_path.name} ({size_kb:.0f} KB)")
    print()

    print("Summarizing with Gemini...")
    try:
        summary = summarize_audio(audio_path)
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
