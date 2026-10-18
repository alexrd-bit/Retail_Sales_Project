# Project Brief — Retail Sales Intelligence and Demand Forecasting

**Unit:** 17 — Data for Business Process Support  
**Student:** Alex Ramirez Duran  
**Project:** Individual end-to-end data science project  
**Prepared:** 18 October 2026  
**Status:** Proposal with verified source-data profile; hypotheses and models remain untested

## 1. Open dataset and eligibility

The proposed source is **Online Retail II**, published by the UCI Machine Learning Repository (Chen, 2012). It records invoice lines from a UK-based online giftware retailer over approximately two years. Local profiling confirms 1,067,371 records and eight original fields; results are recorded in [local profile](../reports/dataset-profile.json). Both worksheets contain `Invoice`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `Price` (GBP), `Customer ID` and `Country`, verified by the [profiling script](../src/check_dataset.py).

### Dataset card

| Field | Answer |
|---|---|
| Name | Online Retail II |
| Publisher and URL | Daqing Chen; UCI Machine Learning Repository — https://archive.ics.uci.edu/dataset/502/online+retail+ii |
| Licence (exact name and link) | Creative Commons Attribution 4.0 International (CC BY 4.0): https://creativecommons.org/licenses/by/4.0/ |
| Download date and version / last update | Downloaded 18 October 2026; UCI donation date: 20 September 2019. SHA-256 recorded in [local profile](../reports/dataset-profile.json); this identifies the local snapshot, not a publisher version. |
| Grain | One invoice line for one product (not one whole order). |
| Period | Verified: 2009-12-01 07:45:00 to 2011-12-09 12:50:00; 25 calendar months represented. |
| Size | Verified: 1,067,371 rows × 8 columns; 45.62 MB (45,622,278 bytes; decimal MB). Sheets: Year 2009-2010 (525,461 rows) and Year 2010-2011 (541,910 rows). |
| Key columns | Date: `InvoiceDate`. Categorical: `Country`, `StockCode`, `Customer ID` (nominal identifiers, not continuous measurements); `Description` is product text. Derived calendar categories: `weekday` and `month`. Numeric: `Quantity`, `Price`; derived `line_sales_gbp`. Candidate target: weekly units sold by SKU, aggregated from valid sales lines. |
| Known quality issues | Measured missing values: Customer ID 243,007; Description 4,382. Duplicate rows beyond the first: 34,335; negative quantities: 22,950; zero prices: 6,202; negative prices: 5; C-prefixed invoice lines: 19,494. Counts overlap. No rows have been removed. |
| Other sources | None initially. The UK government bank-holiday calendar may be evaluated as an optional join if a defensible date-matched source is needed. |

Three original categorical fields are available: product, country and customer identifier. Customer IDs support internal aggregate grouping only. Public dashboard filters will use product, country and calendar month derived from InvoiceDate; missing customer IDs will not exclude otherwise usable sales.

The major limitation is that observed purchases are **not** the same as unconstrained demand: stockouts are not recorded. Inventory, stock availability, marketing campaigns, costs and margins are not available. The historical data supports a demonstrator, not a current trading forecast.

## 2. Business problem

### 2.1 Organisation, department and stakeholder

**Northstar Gifts** is a fictional UK e-commerce retailer inspired by the dataset's giftware business. It sells multiple products online to domestic and international customers. Its proposed strategy is dependable product availability while limiting cash tied up in stock. Purchasing staff gain a shared review list; finance can assess purchasing priorities, while customers may benefit from availability improvements that this dataset cannot directly measure.

The **inventory planning and merchandising team** recommends weekly purchasing priorities. Every Monday, the **inventory planning manager** reviews the dashboard to select products for closer monitoring and purchasing review. Actual reorder quantities also require unavailable stock, lead-time and minimum-order data.

### 2.2 Decision and constraints

**With this system, the manager will decide which products to prioritise for the next weekly replenishment review, based on historical demand concentration, sales trends and forecast uncertainty.** The solution will not automatically place orders.

The alternative is spreadsheet reporting and recent-sales heuristics; these are cheaper initially but require repeated manual preparation. Constraints include limited historical coverage, absent inventory and cost information, possible wholesale bulk orders, returns, data quality and privacy. Monetary benefits would require cost assumptions.

### 2.3 Testable hypotheses (ordered by decision value)

H1 identifies review priorities first; H2 informs timing; H3 tests whether additional modelling earns its complexity.

**H1 — Demand is concentrated in a minority of products.**  
**Metric:** percentage of positive units sold contributed by the highest-volume 20% of SKUs, calculated for each complete quarter after excluding cancellations; round the SKU count up. **Expected direction:** over 50% of units come from this group (test threshold, not a known result). **Test:** Pareto chart and cumulative share table, including a UK-only sensitivity check. **If true:** prioritise those SKUs for frequent monitoring. **If false:** use wider product coverage rather than a narrow priority list.

**H2 — Weekly demand has a meaningful recurring pattern.**  
**Metric:** mean weekly units in November divided by mean weekly units during January–October, for a common cohort of products sold in both years. **Expected direction:** ratio above 1.10 in both 2010 and 2011 (proposed practical threshold). **Test:** use complete Monday–Sunday weeks, assign weeks by Thursday, compare each year separately and inspect SKU heatmaps. Two years provide limited evidence of recurrence. **If true:** adapt monitoring and forecast features to the calendar. **If false:** favour simple short-term averages and minimise calendar-specific assumptions.

**H3 — A short-history forecasting model improves on a naïve estimate.**  
**Metric:** weighted absolute error (WAPE = sum of absolute unit errors / sum of observed units) on future held-out weeks, with MAE as a secondary metric. **Expected direction:** a lag-and-calendar model reduces WAPE by at least 5% relative to the previous-week baseline (proposed threshold, not a result). **Test:** chronological holdout and rolling-origin backtests, restricted to information available before each forecast. **If true:** present model estimates alongside uncertainty and baseline. **If false:** retain the transparent baseline and avoid unnecessary complexity.

### 2.4 KPIs

| KPI | Definition and formula | Grain / comparison | Initial target or decision threshold |
|---|---|---|---|
| Units sold | Sum of positive `Quantity` in eligible sales lines; credits reported separately | Week × SKU; product and country | Monitor trend; no arbitrary volume target |
| Gross sales value | Sum of `Quantity × Price` for eligible positive-price sales lines, GBP; **not profit or net revenue** | Week; product and country | Compare with previous equivalent weeks |
| Average order value | Gross sales value / distinct eligible invoices | Week; country; whole orders | Compare equivalent periods |
| Weekly sales growth | (Current gross sales / previous week gross sales − 1) × 100 | Complete week; country | Investigate increases and decreases |
| Forecast error (WAPE) | Sum \|actual units − predicted units\| / sum actual units × 100 | Backtest period; SKU cohort | Proposed acceptance: WAPE at least 5% lower than baseline (H3) |

Eligible sales will require positive quantity and price, a non-C invoice and a documented merchandise code; credits and adjustments will be reported separately. Exact duplicate lines will be investigated before removal. Weeks run Monday–Sunday. Undefined ratios will show N/A, including zero prior-week sales or zero total actual units for WAPE. Product-week zeros represent no recorded sales within an observed selling window, not proven availability.

Higher sales or order values may reflect bulk orders rather than stable demand. Prioritising volume may neglect low-volume products; lower forecast error does not prove profit or availability gains. Targets require stakeholder agreement.

## 3. Solution design

### 3.1 Solution type: management dashboard with an analytical engine

The management dashboard is primary; forecasting is secondary and will be implemented later. Streamlit reuses Python transformations and avoids a separate BI stack. Spreadsheets suit a smaller manual prototype; Power BI offers stronger managed reporting but adds another tool. This brief proposes the design only. **Inputs:** the two-sheet Excel workbook, standardised invoice lines and derived product-week history. **Logic:** ingestion, quality rules, separation of sales from credits, time-series aggregation, historical KPIs and forecasts using only previous observations. Compare a naïve baseline with later candidate regression models. **Outputs:** product and country filters, weekly sales trends, a Pareto chart, a forecast-versus-actual plot, performance metrics and a ranked SKU review list. The rankings are advisory.

### 3.2 General architecture

```mermaid
flowchart LR
    A["UCI Online Retail II Excel"] --> B["Python / pandas ingestion"]
    B --> C["Quality checks and cleaning"]
    C --> D["Sales fact and product/date dimensions in Parquet"]
    D --> E["KPIs and weekly demand forecast"]
    E --> F["Streamlit dashboard"]
    F --> G["Inventory planning manager"]
```

| Layer | What it does | Tool | Refresh |
|---|---|---|---|
| Source | Historical invoice-line extracts | UCI Excel | Static historical snapshot |
| Ingestion | Read both worksheets; standardise names, dates and numeric types | Python, pandas, openpyxl | Once, reproducible rerun |
| Cleaning & quality | Profile nulls, duplicates, cancellations, prices and outliers; record excluded counts | pandas, validation assertions | Each pipeline execution |
| Data model | Store transaction fact, SKU/date dimensions and continuous product-week panel | Parquet / pandas | Each pipeline execution |
| Analytics / engine | KPI tables, previous-week baseline, future forecast evaluation | pandas, scikit-learn | On processed data refresh |
| Dashboard | Filters, trends, alerts and forecast comparison | Streamlit / Plotly | On application reload or file refresh |

**Update and ownership:** the student owns the reproducible workflow during the course. UCI is not a live transaction feed. A future business implementation would require access to current transaction and inventory systems and scheduled weekly ingestion. Schema changes will stop the pipeline with an explicit validation error. Code and pinned dependencies live in GitHub; raw data will be downloaded from UCI and stored locally under `data/raw/`, not committed unnecessarily. Processed outputs will be regenerated.

**Main risks and safeguards:** (1) historical behaviour may not represent today's customers, so avoid claims of current predictive accuracy; (2) missing IDs, credit notes and unusually large wholesale orders may bias aggregates, so publish quality counts and sensitivity comparisons; (3) customer identifiers, even pseudonymous ones, create privacy concerns, so exclude them from shared dashboard outputs, minimise retention, avoid unnecessary individual profiling and use aggregate reporting. Respect the CC BY 4.0 attribution requirement (Creative Commons, n.d.). Any future personal-data use requires a separate privacy assessment. Additional controls include input validation, read-only dashboard access and not committing credentials.

## 4. Delivery and next steps

**No cleaning, hypothesis tests or models are claimed complete.** Source download, checksum and profiling are complete; see [quality report](../reports/dataset-quality.md). Next: confirm eligibility with the lecturer and agree cleaning rules. Later blocks will add the dashboard, chronological forecasting evaluation and deployment, then assess business value with explicit assumptions.

## References (Harvard style)

Chen, D. (2012) *Online Retail II* [dataset]. UCI Machine Learning Repository. Available at: https://doi.org/10.24432/C5CG6D (Accessed: 18 October 2026).

Creative Commons (n.d.) *Attribution 4.0 International (CC BY 4.0)*. Available at: https://creativecommons.org/licenses/by/4.0/ (Accessed: 18 October 2026).

