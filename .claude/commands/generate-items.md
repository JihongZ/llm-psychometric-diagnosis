# Generate Items Command

Generate `items.csv` for a project folder by inspecting raw response data interactively.

---

## Expected Input

A raw response CSV file where:
- Each **row** is one person
- Each **column** is one item
- **Column names** serve as both `item_id` and `item_text`

---

## Workflow

### Step 0 — Identify the project folder

Use the current working directory as the project folder unless the user has specified otherwise.

### Step 1 — Find raw response data

Scan the project folder for CSV files, excluding `responses.csv` and anything inside `Output/`.

- If exactly one CSV is found, use it and inform the user.
- If multiple CSVs are found, list them and ask the user which one to use.
- If none are found, ask the user to provide the path to the raw data file.

### Step 2 — Inspect the data

Read the CSV file and compute:

- `item_ids`: all column names
- `n_items`: number of columns
- `response_min`: minimum value observed across all cells
- `response_max`: maximum value observed across all cells
- `default_cutoff`: `round(n_items × response_max / 2)`
- `default_scale`: `{filename}_scale` where `{filename}` is the CSV file name without extension

Report a brief summary to the user:
> Found {n_items} items, response range {response_min}–{response_max}, default cutoff {default_cutoff}.

### Step 3 — Ask for scale name

Ask the user:

> What is the scale/instrument name for these items?
> [Press Enter for default: {default_scale}]

If the user provides no input, use `{default_scale}`.

### Step 4 — Ask for cutoff

Ask the user:

> What is the validated sum-score cutoff?
> [Press Enter for default: {default_cutoff}  ← half of maximum sum score ({n_items} × {response_max} / 2)]

If the user provides no input, use `{default_cutoff}`.

### Step 5 — Generate items.csv

Write `{PROJECT_FOLDER}/items.csv` with the following columns:

| column | value |
|---|---|
| `item_id` | column name from raw data |
| `item_text` | column name from raw data (same as item_id) |
| `scale` | scale name from Step 3 |
| `cutoff` | cutoff from Step 4 (same value repeated for every row) |
| `response_min` | minimum response value inferred in Step 2 |
| `response_max` | maximum response value inferred in Step 2 |

One row per item. After writing, display the full contents of the generated file so the user can review it.

---

## Notes

- If `items.csv` already exists, warn the user and ask for confirmation before overwriting.
- `item_text` can be edited manually later if the column names are not human-readable (e.g., `PHQ1` → full item wording).
- After generating `items.csv`, the user can run `diagnosis run <folder>` to start the full diagnostic pipeline.
