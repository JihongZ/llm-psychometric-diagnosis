"""CLI entry point for the diagnosis command."""

import shutil
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from diagnosis import __version__
from diagnosis import skills, tmux

app = typer.Typer(
    name="diagnosis",
    help="LLM-assisted psychometric diagnosis using cut-off, IRT, and DCM methods.",
    no_args_is_help=True,
)
console = Console()


def _validate_folder(project_folder: Path) -> Path:
    project_folder = project_folder.resolve()
    if not project_folder.is_dir():
        console.print(f"[red]Error:[/red] folder not found: {project_folder}")
        raise typer.Exit(1)
    if not (project_folder / "items.csv").exists():
        console.print(f"[red]Error:[/red] items.csv not found in {project_folder}")
        console.print("Expected columns: item_id, item_text, scale, cutoff, response_min, response_max")
        raise typer.Exit(1)
    return project_folder


@app.command()
def run(
    project_folder: Path = typer.Argument(..., help="Path to project folder containing items.csv"),
    clear: bool = typer.Option(False, "--clear", help="Delete Output/ before running"),
    no_attach: bool = typer.Option(False, "--no-attach", help="Start session but do not attach to it"),
):
    """
    Run psychometric diagnosis on a project folder.

    The folder must contain items.csv. The agent will generate prepare_responses.R
    (if missing), run the diagnosis pipeline, and write Output/diagnosis_report.md.
    """
    project_folder = _validate_folder(project_folder)

    if clear:
        output_dir = project_folder / "Output"
        if output_dir.exists():
            shutil.rmtree(output_dir)
            console.print(f"[yellow]Cleared:[/yellow] {output_dir}")
        else:
            console.print("[dim]Output/ does not exist — nothing to clear.[/dim]")

    console.print(Panel(
        f"[bold]Project:[/bold] {project_folder}\n"
        f"[bold]Version:[/bold] {__version__}",
        title="Psychometric Diagnosis Agent",
        border_style="blue",
    ))

    prompt = skills.build_prompt(str(project_folder))
    tmux.spawn(str(project_folder), prompt, attach=not no_attach)


@app.command()
def kill(
    project_name: str = typer.Argument(..., help="Project folder name (not full path)"),
):
    """Kill a running diagnosis tmux session."""
    session = tmux.session_name(project_name)
    if tmux.kill(session):
        console.print(f"[green]Killed session:[/green] {session}")
    else:
        console.print(f"[yellow]No session found:[/yellow] {session}")


@app.command()
def attach(
    project_name: str = typer.Argument(..., help="Project folder name (not full path)"),
):
    """Attach to a running diagnosis tmux session."""
    session = tmux.session_name(project_name)
    if not tmux.is_running(session):
        console.print(f"[red]No running session:[/red] {session}")
        raise typer.Exit(1)
    import subprocess
    subprocess.run(["tmux", "attach-session", "-t", session])


@app.command()
def ls():
    """List all active diagnosis sessions."""
    import subprocess
    result = subprocess.run(
        ["tmux", "list-sessions", "-F", "#{session_name}"],
        capture_output=True, text=True,
    )
    sessions = [s for s in result.stdout.splitlines() if s.startswith("diagnosis-")]
    if not sessions:
        console.print("[dim]No active diagnosis sessions.[/dim]")
        return
    table = Table(title="Active Diagnosis Sessions")
    table.add_column("Session", style="cyan")
    table.add_column("Attach command", style="dim")
    for s in sessions:
        table.add_row(s, f"tmux attach -t {s}")
    console.print(table)


@app.command()
def version():
    """Show the diagnosis version."""
    console.print(f"diagnosis {__version__}")


def main():
    app()
