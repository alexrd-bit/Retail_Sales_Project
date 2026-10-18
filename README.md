# Retail Sales Intelligence and Demand Forecasting

Current scope: first project brief, source-data eligibility and quality profiling only.

- Proposal: [project/project-brief.md](project/project-brief.md)
- Verified profile: [reports/dataset-quality.md](reports/dataset-quality.md)
- Source: Daqing Chen (2012), Online Retail II, UCI, https://doi.org/10.24432/C5CG6D
- Dataset licence: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/

## Reproduce on macOS

Download the original workbook from UCI into `data/raw/online_retail_II.xlsx` (both sheets).
Use Python 3.13.7 and run from this project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/check_dataset.py
```

Raw data and the virtual environment are excluded from Git. The script writes aggregate reports only and leaves the workbook unchanged. No cleaning, hypothesis testing or forecasting has been performed.

The lecturer’s original PROJECT_BRIEF.md has been reviewed. It specifies submission in the repository used for autograded exercises, under `project/`. This is a new repository: confirm that it is the correct course repository before sending the link. The deadline is announced in class (before session 7). Submit through the same channel as the exercises.
