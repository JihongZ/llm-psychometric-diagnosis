"""tmux backend: create a session and run the Claude agent inside it."""

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def _require_tmux() -> None:
    if not shutil.which("tmux"):
        print("Error: tmux is not installed. Install it with: brew install tmux", file=sys.stderr)
        sys.exit(1)


def _require_claude() -> None:
    if not shutil.which("claude"):
        print(
            "Error: 'claude' command not found.\n"
            "\n"
            "Possible causes:\n"
            "  1. Claude Code is not installed.\n"
            "     Install it: https://github.com/anthropics/claude-code\n"
            "  2. Claude Code is installed but not in your PATH.\n"
            "     Try: which claude   (or: npm list -g @anthropic-ai/claude-code)\n"
            "     If installed via npm, ensure the npm global bin directory is in your PATH:\n"
            "       export PATH=\"$(npm prefix -g)/bin:$PATH\"",
            file=sys.stderr,
        )
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


def _inside_tmux() -> bool:
    return bool(os.environ.get("TMUX"))


def _switch_or_attach(session: str) -> None:
    """Switch to session if already inside tmux, otherwise attach."""
    if _inside_tmux():
        subprocess.run(["tmux", "switch-client", "-t", session])
    else:
        subprocess.run(["tmux", "attach-session", "-t", session])


def kill(session: str) -> bool:
    if is_running(session):
        subprocess.run(["tmux", "kill-session", "-t", session], check=True)
        return True
    return False


def _wait_for_finish(session: str, poll_interval: float = 3.0) -> None:
    """Block until the tmux session ends, printing a spinner."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    print()
    while is_running(session):
        print(f"\r  {frames[i % len(frames)]}  Agent running… "
              f"(tmux attach -t {session} to watch)", end="", flush=True)
        time.sleep(poll_interval)
        i += 1
    print("\r  ✓  Agent finished.                                        ")


def spawn(project_folder: str, prompt: str, attach: bool = True) -> str:
    """
    Create a tmux session, write the prompt to a temp file, and run:
        claude --dangerously-skip-permissions -p "$(cat prompt_file)"

    If attach=True and inside an existing tmux session, switch to it.
    If attach=True and outside tmux, attach to it.
    If attach=False, poll and print a spinner until the session ends.

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
        f'echo "--- Diagnosis agent started ---" && '
        f'claude --dangerously-skip-permissions -p "$(cat {shlex.quote(str(prompt_file))})"; '
        f'echo ""; echo "--- Agent finished. Press any key to close ---"; '
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

    print(f"  Session: {session}")
    print(f"  Attach:  tmux attach -t {session}")
    print(f"  Kill:    diagnosis kill {Path(project_folder).name}")

    if attach:
        print("  Switching to tmux session…")
        _switch_or_attach(session)
    else:
        _wait_for_finish(session)

    return session
