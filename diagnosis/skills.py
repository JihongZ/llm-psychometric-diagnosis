"""Load skill markdown files bundled with the package."""

from importlib.resources import files


def load(name: str) -> str:
    """Return the text content of a skill file by name (without .md extension)."""
    return files("diagnosis.skills").joinpath(f"{name}.md").read_text(encoding="utf-8")


def build_prompt(project_folder: str) -> str:
    diagnosis_skill = load("diagnosis")
    psychometric_functions = load("psychometric-diagnosis")

    return f"""\
You are a psychometric diagnosis agent. A user has run:

    diagnosis {project_folder}

The absolute path to the project folder is: {project_folder}

Follow the workflow below exactly.

---

{diagnosis_skill}

---

The R functions you must inline into each generated script are defined here:

{psychometric_functions}
"""
