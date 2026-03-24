"""tmux backend: create a session and run the Claude agent inside it."""

import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _require_tmux() -> None:
    if not shutil.which("tmux"):
        print("Error: tmux is not installed. Install it with: brew install tmux", file=sys.stderr)
        sys.exit(1)


def _require_claude() -> None:
    if not shutil.which("claude"):
        print("Error: claude CLI not found. Install Claude Code first.", file=sys.stderr)
        sys.exit(1)


def session_name(project_folder: str) -> str:
    slug = Path(project_folder).name.replace(" ", "-").replace("_", "-").lower()
    return f"diagnosis-{slug}"


def is_running(session: str) -> bool:
    result = subprocess.run(
        ["tmux", "has-session", "-t", session],
        capture_output=True,
    )
    return result.returncode == 0


def kill(session: str) -> bool:
    if is_running(session):
        subprocess.run(["tmux", "kill-session", "-t", session], check=True)
        return True
    return False


def spawn(project_folder: str, prompt: str, attach: bool = True) -> str:
    """
    Create a tmux session, write the prompt to a temp file, and run:
        claude --dangerously-skip-permissions -p "$(cat prompt_file)"

    Returns the session name.
    """
    _require_tmux()
    _require_claude()

    session = session_name(project_folder)

    if is_running(session):
        print(f"Session '{session}' is already running.")
        print(f"  Attach:  tmux attach -t {session}")
        print(f"  Kill:    diagnosis kill {Path(project_folder).name}")
        sys.exit(1)

    # Write prompt to a temp file to avoid shell quoting issues
    prompt_file = Path(tempfile.mkstemp(suffix=".txt", prefix="diagnosis_")[1])
    prompt_file.write_text(prompt, encoding="utf-8")

    cmd = (
        f'claude --dangerously-skip-permissions -p "$(cat {shlex.quote(str(prompt_file))})"; '
        f'echo "--- Agent finished. Press any key to exit ---"; '
        f'read -n 1; '
        f'rm -f {shlex.quote(str(prompt_file))}'
    )

    # Create detached tmux session and send the command
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", session, "-x", "220", "-y", "50"],
        check=True,
    )
    subprocess.run(
        ["tmux", "send-keys", "-t", session, cmd, "Enter"],
        check=True,
    )

    print(f"Diagnosis agent started in tmux session: {session}")
    print(f"  Attach:  tmux attach -t {session}")
    print(f"  Kill:    diagnosis kill {Path(project_folder).name}")
    print()

    if attach:
        subprocess.run(["tmux", "attach-session", "-t", session])

    return session
