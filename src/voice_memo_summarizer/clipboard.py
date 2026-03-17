"""Get a voice memo file via native macOS file picker."""

import subprocess
from pathlib import Path

VOICE_MEMOS_DIR = (
    Path.home()
    / "Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings"
)


def pick_audio_file(default_dir: Path = VOICE_MEMOS_DIR) -> Path | None:
    """Open a native macOS file picker dialog and return the selected path.

    Defaults to the Voice Memos recordings directory.
    Returns None if the user cancels.
    """
    script = (
        f'set defaultDir to POSIX file "{default_dir}" as alias\n'
        "try\n"
        '    POSIX path of (choose file of type {"public.audio"} '
        'with prompt "Select a voice memo" '
        "default location defaultDir)\n"
        "on error\n"
        '    return ""\n'
        "end try"
    )
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    path_str = result.stdout.strip()
    if not path_str:
        return None
    return Path(path_str)
