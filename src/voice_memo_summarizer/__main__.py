"""CLI entry point for voice-memo-summarizer."""

import argparse
import subprocess
import sys
from pathlib import Path

from voice_memo_summarizer.clipboard import pick_files
from voice_memo_summarizer.summarizer import DEFAULT_PROMPT, summarize


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="voice-memo-summarizer",
        description="Summarize voice memos and other files using Gemini on Vertex AI. "
        "Outputs raw markdown to stdout; status messages go to stderr. "
        "The summary is copied to the clipboard by default.",
        epilog=(
            "examples:\n"
            "  %(prog)s recording.m4a\n"
            "  %(prog)s recording.m4a > summary.md\n"
            "  %(prog)s --prompt-file prompt.md recording.m4a\n"
            "  %(prog)s --gcp-project my-proj --no-clipboard *.m4a\n"
            "  %(prog)s                  # opens macOS file picker"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="files to summarize (audio, video, images, PDFs, etc.). "
        "Opens a native macOS file picker when omitted.",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        default=None,
        metavar="PATH",
        help="path to a markdown file containing a custom prompt. "
        "Uses a built-in meeting-notes prompt when omitted.",
    )
    parser.add_argument(
        "--gcp-project",
        default=None,
        metavar="PROJECT",
        help="GCP project ID for Vertex AI (default: GCP_PROJECT env var).",
    )
    parser.add_argument(
        "--no-clipboard",
        action="store_true",
        default=False,
        help="skip copying the summary to the clipboard.",
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
        summary = summarize(files, prompt=prompt, gcp_project=args.gcp_project)
    except Exception as e:
        print(f"Error during summarization: {e}", file=sys.stderr)
        sys.exit(1)

    print(summary)

    if not args.no_clipboard:
        copy_to_clipboard(summary)
        print("Copied to clipboard.", file=sys.stderr)


if __name__ == "__main__":
    main()
