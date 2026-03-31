"""Get files via native macOS file picker."""

import subprocess
from pathlib import Path

VOICE_MEMOS_DIR = (
    Path.home()
    / "Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings"
)


def pick_files(default_dir: Path = VOICE_MEMOS_DIR) -> list[Path]:
    """Open a native macOS file picker dialog and return the selected paths.

    Allows selecting multiple files of any type.
    Defaults to the Voice Memos recordings directory.
    Returns an empty list if the user cancels.
    """
    script = (
        f'set defaultDir to POSIX file "{default_dir}" as alias\n'
        "try\n"
        "    set selectedFiles to choose file "
        'with prompt "Select files" '
        "default location defaultDir "
        "with multiple selections allowed\n"
        "    set posixPaths to {}\n"
        "    repeat with f in selectedFiles\n"
        "        set end of posixPaths to POSIX path of f\n"
        "    end repeat\n"
        '    set AppleScript\'s text item delimiters to "\\n"\n'
        "    return posixPaths as text\n"
        "on error\n"
        '    return ""\n'
        "end try"
    )
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip()
    if not output:
        return []
    return [Path(line) for line in output.splitlines() if line.strip()]
