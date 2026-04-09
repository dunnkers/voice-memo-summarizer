# voice-memo-summarizer

A CLI tool that summarizes voice memos and other files using Gemini on Vertex AI. Select one or more files via a native macOS file picker, and get a transcription, summary, and action items — all copied to your clipboard.

![File picker](docs/Screenshot%202026-04-09%20at%2021.40.53.png)

## Usage

Requires a GCP project with Vertex AI enabled. Set the `GCP_PROJECT` environment variable (e.g. via `.env`, `export`, or inline):

```sh
GCP_PROJECT=your-gcp-project uv run voice-memo-summarizer
```

A native macOS file picker opens, allowing you to select one or more files (audio, markdown, PDFs, etc.):

```
Selected 2 file(s) (9450 KB total):
  - The QEII Centre 11.m4a
  - Sunil Pai - Keynote.md

Default prompt:
  You are a meeting notes assistant. Your task is to: 1) transcribe, 2) summarise
  and then, if applicable 3) provide action items from the attached recording.
  Write your summary in the same language as the audio.

Enter custom prompt (or press Enter to use default): 

Sending to Gemini...
```

After summarization, you can copy the result to your clipboard.

You can also pass files directly as arguments:

```sh
GCP_PROJECT=your-gcp-project uv run voice-memo-summarizer recording.m4a notes.md
```

## Installation

```sh
uv sync
```

Authenticate with GCP:

```sh
gcloud auth application-default login
```