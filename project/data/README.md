# Model input data

`weekly-sales.parquet` contains anonymous aggregates derived from:

Chen, D. (2012). *Online Retail II* [Data set]. UCI Machine Learning Repository.
https://doi.org/10.24432/C5CG6D

Licence: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).
Changes: combine both sheets, remove exact duplicates, separate credits and nonpositive lines,
retain a documented merchandise-code proxy, remove incomplete boundary weeks, and aggregate.
`quality-audit.json` gives sequential counts and source/output SHA-256 checksums.

| Column | Meaning |
|---|---|
| StockCode | Product identifier, string |
| market | UK or International; derived from Country |
| week_start | Monday date, covering the complete Monday–Sunday week |
| units | Sum of eligible positive quantities, units |
| gross_sales_gbp | Sum of Quantity × Price in GBP; excludes credits; not net revenue or profit |
| lines | Number of retained source invoice lines in the group |

One row is one product × market × week with at least one eligible sale. The notebook creates
zero weeks for its initial, fixed product cohort. Zero means no recorded eligible sale;
it does not establish stock availability. No customer ID, invoice number or description is included.

Rebuild from the repository root with `python src/prepare_model_data.py` after placing the
original workbook under `data/raw/online_retail_II.xlsx`. This slow rebuild is optional: the
notebook reads the small committed Parquet file and needs no network connection.
