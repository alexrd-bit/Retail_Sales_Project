# Retail Sales Intelligence and Demand Forecasting

Alex Ramirez Duran · Unit 17 · Individual project

## Deliverables

1. [Project brief](project/project-brief.md): the original business proposal.
2. [Executed modelling notebook](project/project-model.ipynb): second deliverable, with saved tables and Plotly charts.
3. [Saved pipeline](project/model.joblib) and [input schema](project/model-input-schema.json).
4. [Measured evaluation](project/results/model-evaluation.json), [validation comparisons](project/results/validation-comparison.csv), and [final holdout predictions](project/results/test-predictions.csv).

The modelling notebook retains the headings from the original lecturer template. The first brief is preserved.
The final model is an evaluated candidate; the notebook's recommendation determines whether it should be used.

## Run on macOS or another computer

Use **Python 3.12** (the course version). From the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyter lab project/project-model.ipynb
```

Choose **Restart Kernel and Run All Cells**, then save. Alternatively:

```bash
python src/run_model_notebook.py
```

The notebook works from the repository root or `project/`, uses relative paths, and needs no source download.
The fresh-kernel Python 3.12 execution was checked under the ten-minute limit. The committed tables and PNG
fallbacks allow GitHub reading without execution; reruns display Plotly charts interactively in Jupyter.
Interactive standalone HTML previews are generated locally under `project/results/` and excluded from Git.

All seeds are fixed. Read `project/data/README.md` for source attribution, aggregation rules and data limitations.
The notebook's Markdown narrative is within 1,200–2,500 words. Outputs contain actual computed results.

## Saved-model contract

`model.joblib` is a scikit-learn pipeline containing stateless feature derivation, learned preprocessing and a
fitted regressor. Keep `project/retail_features.py` on the Python import path and use the pinned versions.
One input row contains `StockCode`, Monday `week_start`, and `lag_1` to `lag_13` from closed weekly sales.
It does not accept arbitrary invoice lines. Check that SKU is in the schema cohort before serving: unseen
SKUs require a fallback and must not receive an unqualified prediction. Only load trusted joblib files.
The model is trained through the development period; test targets were not used to fit it.

## Source and optional rebuild

Chen, D. (2012). *Online Retail II* [Data set]. UCI Machine Learning Repository.
https://doi.org/10.24432/C5CG6D · CC BY 4.0, https://creativecommons.org/licenses/by/4.0/

The raw workbook and virtual environment are excluded from Git. To reproduce transaction-level preparation,
download the original workbook into `data/raw/online_retail_II.xlsx`, then run:

```bash
python src/check_dataset.py
python src/prepare_model_data.py
```

Do not run these optional slow source checks inside the modelling notebook. They are already documented
in the original profiling report and the model-data audit. Customer and invoice identifiers are not published.

## Submission

Send the lecturer the GitHub link to `project/project-model.ipynb` before the date announced in class.
The exact deadline and delivery channel are not stated in the supplied second brief. This is the student's
only repository; confirm any course-specific repository requirement with the lecturer.
