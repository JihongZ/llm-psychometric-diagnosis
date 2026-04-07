"""Load skill markdown files bundled with the package."""

from importlib.resources import files


def load(name: str) -> str:
    """Return the text content of a skill file by name (without .md extension)."""
    return files("diagnosis.skills").joinpath(f"{name}.md").read_text(encoding="utf-8")


def build_generate_items_prompt(project_folder: str, raw_data_file: str) -> str:
    generate_items_skill = load("generate-items")

    return f"""\
You are a psychometric items generator. A user has run:

    diagnosis run {project_folder}

items.csv was not found. The user has confirmed they want you to generate it automatically.

The absolute path to the project folder is: {project_folder}
The raw response data file to use is: {raw_data_file}

Follow the workflow below. Skip Step 1 (finding the raw data file) — use the file
specified above. Use smart defaults for all other values: infer the scale name and
cutoff from the data without pausing to ask the user questions.

---

{generate_items_skill}
"""


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
