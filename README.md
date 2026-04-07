<h1 align="center">🧠 AutoPsychDx</h1>

<p align="center">
  <strong>One command. Three methods. Automatic clinical diagnosis from item-level response data.</strong>
</p>

<p align="center">
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Quick_Start-3_steps-blue?style=for-the-badge" alt="Quick Start"></a>
  <a href="#-example-depression-screening-forbes-2018"><img src="https://img.shields.io/badge/Example-PHQ--9_Depression-green?style=for-the-badge" alt="Example"></a>
  <a href="#-diagnostic-methods"><img src="https://img.shields.io/badge/Methods-3_(Cut--off_|_IRT_|_DCM)-purple?style=for-the-badge" alt="Methods"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-≥3.10-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/R-≥4.0-276DC3?logo=r&logoColor=white" alt="R">
  <img src="https://img.shields.io/badge/Claude_Code-agent-blueviolet" alt="Claude Code">
  <img src="https://img.shields.io/badge/tmux-session_management-orange" alt="tmux">
  <img src="https://img.shields.io/badge/install-pipx-informational" alt="pipx">
</p>

**You provide the scale. The agent runs cut-off, IRT, and DCM — and writes the report.**

Given item-level response data from any psychological scale, the agent applies three complementary diagnostic methods and generates a structured markdown report with prevalence estimates, method comparisons, and plain-language clinical interpretation.

See details of data analysis in the preprint on OSF - *AutoPsychDx: An LLM Agent Framework for Automated Psychometric Diagnosis Using Multi-Method Classification* [(Zhang, 2026)](https://osf.io/jtpa3/files/sp3jt).

---

## 🤔 Why This Tool?

Psychometric diagnosis requires expertise across multiple frameworks. Researchers must manually choose between sum-score cut-offs, IRT, and DCM — each with different software, assumptions, and outputs. Reconciling disagreements between methods takes additional effort, and generating readable reports requires even more.

**What if an LLM agent could do all of this automatically?**

- 🚀 **Runs all three methods** — cut-off, IRT, and DCM in a single command
- 📋 **Validates inputs automatically** — checks item IDs, response ranges, and missing data
- 💬 **Flags method disagreements** — highlights ambiguous cases where methods diverge
- 📊 **Generates a full report** — prevalence tables, item content, and clinical interpretation
- 🔄 **Works with any scale** — instrument-agnostic, configured via a simple `items.csv`

#### ✨ The Result?
You set up the project folder. The agent diagnoses, interprets, and reports.

---

## 📐 Diagnostic Methods

<table align="center" width="100%">
<tr>
<td width="33%" align="center" style="vertical-align: top; padding: 15px;">

### 📏 Sum Score Cut-off

<img src="https://img.shields.io/badge/Method_A-Cut--off-FF6B6B?style=for-the-badge" alt="Cut-off">

Sums item responses per person and compares to a validated clinical threshold.

**Key parameter:** `cutoff` (from `items.csv`)

**Best for:** Quick screening when a published cut-off exists (e.g. PHQ-9 ≥ 10, PCL-5 ≥ 33)

</td>
<td width="33%" align="center" style="vertical-align: top; padding: 15px;">

### 📈 Item Response Theory

<img src="https://img.shields.io/badge/Method_B-IRT_(GRM)-4ECDC4?style=for-the-badge" alt="IRT">

Fits a Graded Response Model using `mirt`. Estimates latent trait θ with standard errors per person.

**Key parameter:** `theta_cutoff` (default: 0)

**Best for:** Scales with items of varying quality; when measurement uncertainty matters

</td>
<td width="33%" align="center" style="vertical-align: top; padding: 15px;">

### 🔬 Diagnostic Classification

<img src="https://img.shields.io/badge/Method_C-DCM_(GDM)-C77DFF?style=for-the-badge" alt="DCM">

Fits a log-linear cognitive diagnosis model using `CDM::gdm`. Returns posterior class membership probability per person.

**Key parameter:** `prob_cutoff` (default: 0.5)

**Best for:** When the construct is naturally categorical (present/absent)

</td>
</tr>
</table>

A person is flagged as diagnosed if **at least 2 of 3 methods** agree (**consensus diagnosis**). Persons where only 1 method flags them are marked ambiguous in the report.

---

## ⚡ Quick Start

**Requirements:** [Claude Code](https://github.com/anthropics/claude-code), [tmux](https://github.com/tmux/tmux/wiki), R ≥ 4.0, Python ≥ 3.10.

**Step 1 — Install pipx**

| Platform | Command |
|---|---|
| macOS | `brew install pipx && pipx ensurepath` |
| Linux | `python3 -m pip install --user pipx && python3 -m pipx ensurepath` |
| Windows | `python -m pip install --user pipx && python -m pipx ensurepath` |

**Step 2 — Install R**

Download from **https://cran.r-project.org** or:

| Platform | Command |
|---|---|
| macOS | `brew install r` |
| Linux (Debian/Ubuntu) | `sudo apt install r-base` |
| Windows | Installer from CRAN |

Then install R packages:
```r
install.packages(c("mirt", "CDM"))
```

**Step 3 — Install the `diagnosis` command**

```bash
git clone https://github.com/JihongZ/AutoPsychDx
cd AutoPsychDx
pipx install -e .   # use pipx, not pip
```

Verify:
```bash
diagnosis --help
```

---

## 🖥️ CLI Reference

| Command | Description |
|---|---|
| `diagnosis compile <folder>` | Generate `items.csv` from `responses.csv` |
| `diagnosis run <folder>` | Run the full diagnosis pipeline (spinner, blocks until done) |
| `diagnosis run <folder> --clear` | Delete `Output/` then re-run |
| `diagnosis clean <folder>` | Remove generated `Output/` directory |
| `diagnosis clean <folder> --all` | Also remove `items.csv` (responses.csv is never deleted) |
| `diagnosis attach <name>` | Attach to a running tmux session to watch live output |
| `diagnosis ls` | List all active diagnosis sessions |
| `diagnosis kill <name>` | Stop a running session |
| `diagnosis version` | Show installed version |

`<folder>` is the path to your project folder (e.g. `Projects/PTSD_Forbes2018`).
`<name>` is the folder name only (e.g. `PTSD_Forbes2018`).

> Both `compile` and `run` run the agent inside a **tmux session** in the background and show a spinner until finished. Use `diagnosis attach <name>` at any time to watch the agent output live.

---

## 📁 Preparing a New Project

The minimum setup is a folder with two files: `responses.csv` and `items.csv`.

### Step 1 — Prepare `responses.csv`

A CSV where each **row is a person** and each **column is an item** (column names = item IDs):

```csv
GAD1,GAD2,GAD3,GAD4,GAD5,GAD6,GAD7
0,1,0,2,1,0,1
1,2,1,3,2,1,2
...
```

Place this file directly in your project folder. If you need to extract items from a larger dataset, write a `prepare_responses.R` script (see below).

### Step 2 — Generate `items.csv` with `diagnosis compile`

Run:

```bash
diagnosis compile Projects/your_study
```

The agent reads `responses.csv`, infers item metadata (response range, scale name, cut-off), and writes `items.csv` automatically. Review and edit `item_text` afterwards if column names are codes rather than full wording.

### `items.csv` format

One row per item:

| Column | Description |
|---|---|
| `item_id` | Unique ID matching column names in `responses.csv` (e.g. `PCL1`) |
| `item_text` | Full item wording as shown to respondents |
| `scale` | Scale name used to group items and label outputs (e.g. `PCL-5`) |
| `cutoff` | Validated sum-score cut-off for this scale (repeat for all rows in the scale) |
| `response_min` | Minimum response value (e.g. `0`) |
| `response_max` | Maximum response value (e.g. `4`) |

```csv
item_id,item_text,scale,cutoff,response_min,response_max
PCL1,Repeated disturbing and unwanted memories of the stressful experience,PCL-5,33,0,4
PCL2,Repeated disturbing dreams of the stressful experience,PCL-5,33,0,4
```

### `prepare_responses.R` (optional)

Only needed if you are extracting item columns from a larger raw dataset or downloading data at runtime. The agent generates a template if this file is missing.

**Example A — local file:**
```r
raw       <- read.csv("raw_data.csv")
items     <- read.csv("items.csv")
responses <- raw[, items$item_id]
write.csv(responses, "responses.csv", row.names = FALSE)
```

**Example B — download from URL:**
```r
tmp <- tempfile(fileext = ".csv")
download.file("https://osf.io/abc123/download", tmp)
raw       <- read.csv(tmp)
items     <- read.csv("items.csv")
responses <- raw[, items$item_id]
write.csv(responses, "responses.csv", row.names = FALSE)
```

### Step 3 — Run diagnosis

```bash
diagnosis run Projects/your_study
```

---

## 🏗️ How It Works

```
  responses.csv
       │
       ▼
  diagnosis compile <folder>          ← infers metadata, writes items.csv
       │
       ▼
  items.csv  +  responses.csv
       │
       ▼
  diagnosis run <folder>
       │
       ├─── Method A: Sum Score Cut-off ──► dx_cutoff (0/1)
       │
       ├─── Method B: IRT (Graded Response Model) ──► dx_irt (0/1) + θ ± SE
       │
       └─── Method C: DCM (CDM::gdm) ──► dx_dcm (0/1) + P(diagnosed)
                      │
                      ▼
          Consensus: diagnosed if ≥ 2/3 methods agree
                      │
                      ▼
       Output/
         [scale]_diagnosis.R           ← generated R script
         [scale]_diagnosis_results.csv ← person-level results
         [scale]_diagnosis_output.txt  ← raw report text
         diagnosis_report.md           ← full report with interpretation
```

Both commands run inside a **tmux session** in the background and block with a spinner until done. Use `diagnosis attach <name>` to watch live output at any time. Skill files in `diagnosis/skills/` define the agent workflow — edit them to change behaviour for all projects.

---

## 📊 Example: Depression Screening (Forbes 2018)

`Projects/PTSD_Forbes2018/` demonstrates the workflow using publicly available PHQ-9 data from [Forbes et al. (2018)](https://osf.io/6fk3v/).

```bash
diagnosis run Projects/PTSD_Forbes2018
```

`prepare_responses.R` downloads the data from OSF automatically on first run. All output is written to `Projects/PTSD_Forbes2018/Output/`.

<table align="center" width="100%">
<tr>
<td width="50%" align="center">

**Agent running in tmux**

![Diagnosis demo — tmux session showing agent output and PHQ-9 report](Screenshots/Diagnosis_PTSD.png)

</td>
<td width="50%" align="center">

**Generated diagnosis_report.md**

![Generated diagnosis_report.md showing PHQ-9 results for the Forbes 2018 sample](Screenshots/Diagnosis_Report.png)

</td>
</tr>
</table>

> [!NOTE]
> **Current Limitations**
> - **Unidimensional only:** All three methods currently assume a single latent construct. Multidimensional scales (e.g., instruments with subscales measuring distinct attributes) are not yet supported.
> - **DCM:** Only the general diagnostic model (`CDM::gdm`) is supported. LCDM, GDINA, DINA, and DINO are not yet implemented.
> - **IRT:** Limited to the Graded Response Model. Requires **complete responses** — handle missing data in `prepare_responses.R` before running.

---

## 🗺️ Roadmap

<table align="center" width="100%">
<tr>
<th>Phase</th>
<th>Feature</th>
<th>Details</th>
</tr>
<tr>
<td>v0.2</td>
<td>Multidimensional DCMs</td>
<td>

- User-specified Q-matrix in `items.csv` (item × attribute mapping)
- LCDM via `CDM::gdm` with multi-attribute Q-matrix
- GDINA via `GDINA::GDINA` for flexible item–attribute interactions
- DINA / DINO as constrained special cases
- Attribute-level diagnostic profiles per person

</td>
</tr>
<tr>
<td>v0.3</td>
<td>Multidimensional IRT</td>
<td>

- MIRT (multidimensional GRM) via `mirt` with exploratory or confirmatory specification
- Subscale-level θ estimates with SEs
- Per-subscale cut-off and consensus diagnosis

</td>
</tr>
<tr>
<td>v0.4</td>
<td>Additional IRT models</td>
<td>

- 2PL for binary items
- GPCM / PCM for alternative polytomous models
- Automatic model selection based on item format

</td>
</tr>
<tr>
<td>v0.5</td>
<td>Missing data & robustness</td>
<td>

- Full-information maximum likelihood (FIML) for IRT
- Multiple imputation support
- Longitudinal multi-timepoint comparison

</td>
</tr>
<tr>
<td>Future</td>
<td>Multi-backend & validation</td>
<td>

- Support for additional LLM backends (OpenAI, Gemini)
- External validation against structured clinical interviews
- Automated sensitivity analysis across cut-off thresholds

</td>
</tr>
</table>

---

## 📖 Acknowledgements

- [Forbes et al. (2018)](https://osf.io/6fk3v/) — PHQ-9 and GAD-7 community sample dataset used in the example project
- [`mirt`](https://cran.r-project.org/package=mirt) — R package for Item Response Theory (IRT) models
- [`CDM`](https://cran.r-project.org/package=CDM) — R package for Cognitive Diagnosis Models (DCM)
- [ClawTeam](https://github.com/HKUDS/ClawTeam) — architectural inspiration for the tmux-based agent CLI
- [Claude Code](https://github.com/anthropics/claude-code) — LLM agent runtime

---

## 📄 License

MIT License — free to use, modify, and distribute. See [LICENSE](LICENSE).

---

## 🗂️ Project Structure

```
.
├── diagnosis/                           # Python package (pipx install -e .)
│   ├── cli.py                           # Typer CLI: compile / run / clean / attach / kill / ls / version
│   ├── tmux.py                          # tmux session management
│   ├── skill_loader.py                  # loads bundled skill files
│   ├── __init__.py
│   ├── __main__.py
│   └── skills/
│       ├── diagnosis.md                 # agent workflow definition
│       ├── generate-items.md            # items.csv generation workflow
│       └── psychometric-diagnosis.md   # R function definitions
├── pyproject.toml                       # package metadata and entry point
├── .claude/
│   └── commands/                        # same skills as Claude Code slash commands
├── Projects/
│   └── PTSD_Forbes2018/                 # example project
│       ├── items.csv                    # item metadata
│       ├── prepare_responses.R          # downloads OSF data → responses.csv
│       └── Output/                      # auto-generated (git-ignored)
├── Screenshots/
│   ├── Diagnosis_PTSD.png
│   └── Diagnosis_Report.png
└── README.md
```

---

<div align="center">

**AutoPsychDx**

*Cut-off · IRT · DCM · One Command*

If you find this project useful, please consider giving it a ⭐

</div>
