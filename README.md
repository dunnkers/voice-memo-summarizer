# voice-memo-summarizer

A CLI tool that summarizes voice memos and other files using Gemini on Vertex AI. Get a transcription, summary, and action items — output as raw markdown to stdout, and copied to your clipboard by default.

Supports audio (`.m4a`, `.mp3`, `.wav`, `.ogg`, `.flac`, `.webm`), video (`.mp4`, `.mov`), images (`.webp`, `.heic`), markdown, and PDFs.

![File picker](docs/Screenshot%202026-04-09%20at%2021.40.53.png)

## Installation

### As a Claude Code skill

```sh
npx skills add https://github.com/dunnkers/voice-memo-summarizer --skill voice-memo-summarizer
```

### Manually

Clone the repo and install dependencies:

```sh
git clone https://github.com/dunnkers/voice-memo-summarizer.git
cd voice-memo-summarizer
uv sync
```

### Prerequisites

Authenticate with GCP:

```sh
gcloud auth application-default login
```

## Usage

Requires a GCP project with Vertex AI enabled. Set the `GCP_PROJECT` environment variable or pass `--gcp-project`.

```sh
# Summarize a file (copies to clipboard, prints markdown to stdout)
uvx git+https://github.com/dunnkers/voice-memo-summarizer voice-memo-summarizer recording.m4a

# Save to a file
uvx git+https://github.com/dunnkers/voice-memo-summarizer voice-memo-summarizer recording.m4a > summary.md

# Multiple files
uvx git+https://github.com/dunnkers/voice-memo-summarizer voice-memo-summarizer recording.m4a notes.md photo.heic

# Custom prompt from a markdown file
uvx git+https://github.com/dunnkers/voice-memo-summarizer voice-memo-summarizer --prompt-file prompt.md recording.m4a

# Explicit GCP project
uvx git+https://github.com/dunnkers/voice-memo-summarizer voice-memo-summarizer --gcp-project my-proj recording.m4a

# Skip clipboard copy
uvx git+https://github.com/dunnkers/voice-memo-summarizer voice-memo-summarizer --no-clipboard recording.m4a

# No arguments — opens a native macOS file picker
uvx git+https://github.com/dunnkers/voice-memo-summarizer voice-memo-summarizer
```

If installed manually, use `uv run voice-memo-summarizer` instead of the `uvx git+...` command.

Status messages (file selection, progress) go to stderr, so stdout contains only the raw markdown summary. This makes the tool pipe-friendly and usable programmatically (e.g. from an agent or script).

### Full help

```
$ voice-memo-summarizer --help
usage: voice-memo-summarizer [-h] [--prompt-file PATH] [--gcp-project PROJECT]
                             [--no-clipboard]
                             [files ...]

Summarize voice memos and other files using Gemini on Vertex AI. Outputs raw
markdown to stdout; status messages go to stderr. The summary is copied to the
clipboard by default.

positional arguments:
  files                 files to summarize (audio, video, images, PDFs, etc.).
                        Opens a native macOS file picker when omitted.

options:
  -h, --help            show this help message and exit
  --prompt-file PATH    path to a markdown file containing a custom prompt.
                        Uses a built-in meeting-notes prompt when omitted.
  --gcp-project PROJECT
                        GCP project ID for Vertex AI (default: GCP_PROJECT env
                        var).
  --no-clipboard        skip copying the summary to the clipboard.

examples:
  voice-memo-summarizer recording.m4a
  voice-memo-summarizer recording.m4a > summary.md
  voice-memo-summarizer --prompt-file prompt.md recording.m4a
  voice-memo-summarizer --gcp-project my-proj --no-clipboard *.m4a
  voice-memo-summarizer                  # opens macOS file picker
```
