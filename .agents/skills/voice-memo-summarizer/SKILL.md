---
name: voice-memo-summarizer
description: Summarize voice memos and other files (audio, video, images, PDFs) using Gemini on Vertex AI. Outputs a transcription, summary, and action items as markdown.
---

# voice-memo-summarizer

Summarize one or more files using the `voice-memo-summarizer` CLI, which sends them to Gemini on Vertex AI and returns a markdown summary with transcription, key points, and action items.

## When to use

- The user asks to summarize a voice memo, audio recording, video, image, or PDF.
- The user wants a transcription or meeting notes from a recording.
- The user wants to extract action items from a voice memo or meeting.

## Instructions

1. Identify the file(s) to summarize. Supported formats: audio (`.m4a`, `.mp3`, `.wav`, `.ogg`, `.flac`, `.webm`), video (`.mp4`, `.mov`), images (`.webp`, `.heic`), markdown, and PDFs.
2. Run the CLI directly (no clone needed):
   ```sh
   uvx --from git+https://github.com/dunnkers/voice-memo-summarizer voice-memo-summarizer <file> [<file> ...]
   ```
3. If the user wants a custom prompt, pass `--prompt-file <path>` with a markdown file containing the prompt.
4. If the user wants to save the output to a file, redirect stdout: `uvx --from git+https://github.com/dunnkers/voice-memo-summarizer voice-memo-summarizer <file> > summary.md`.
5. The summary is automatically copied to the clipboard. Pass `--no-clipboard` to skip this.
6. A GCP project with Vertex AI enabled is required. Set via `GCP_PROJECT` env var or `--gcp-project <project>`.
7. If no files are provided, the CLI opens a native macOS file picker.
