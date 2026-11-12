"""Rebuild anonymous weekly modelling inputs from the original UCI workbook."""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def main():
    source = ROOT / 'data/raw/online_retail_II.xlsx'
    raw = pd.concat(pd.read_excel(source, sheet_name=None).values(), ignore_index=True)
    audit = []
    def keep(frame, mask, step):
        result = frame.loc[mask].copy()
        audit.append({'step': step, 'before': len(frame), 'removed': len(frame)-len(result), 'after': len(result)})
        return result
    data = keep(raw, ~raw.duplicated(), 'Exact duplicate invoice lines: retain first')
    data['StockCode'] = data.StockCode.astype(str).str.strip().str.upper()
    data['InvoiceDate'] = pd.to_datetime(data.InvoiceDate, errors='coerce')
    data = keep(data, data.InvoiceDate.notna() & data.Country.notna(), 'Valid date and country')
    data = keep(data, ~data.Invoice.astype(str).str.upper().str.startswith('C'), 'Separate credit/cancellation invoices')
    data = keep(data, (data.Quantity > 0) & (data.Price > 0), 'Positive units and prices only')
    data = keep(data, data.StockCode.str.fullmatch(r'\d{5}[A-Z]?'), 'Merchandise-code proxy: five digits and optional letter')
    data['week_start'] = data.InvoiceDate.dt.normalize() - pd.to_timedelta(data.InvoiceDate.dt.weekday, unit='D')
    first = raw.InvoiceDate.min().normalize()
    last = raw.InvoiceDate.max().normalize()
    first_week = first + pd.Timedelta(days=(7-first.weekday()) % 7)
    last_week = last - pd.Timedelta(days=last.weekday())
    if last.weekday() != 6:
        last_week -= pd.Timedelta(days=7)
    data = keep(data, data.week_start.between(first_week, last_week), 'Complete Monday-Sunday weeks only')
    data['market'] = data.Country.eq('United Kingdom').map({True: 'UK', False: 'International'})
    data['gross_sales_gbp'] = data.Quantity * data.Price
    weekly = data.groupby(['StockCode', 'market', 'week_start'], observed=True).agg(units=('Quantity', 'sum'), gross_sales_gbp=('gross_sales_gbp', 'sum'), lines=('Quantity','size')).reset_index()
    duplicate_candidates = raw[raw.duplicated()].copy()
    duplicate_candidates['InvoiceDate'] = pd.to_datetime(duplicate_candidates.InvoiceDate)
    duplicate_candidates['StockCode'] = duplicate_candidates.StockCode.astype(str).str.strip().str.upper()
    # Quantify the extra positive units removed by the exact-row rule, independently of later filters.
    dup_positive = duplicate_candidates.loc[(duplicate_candidates.Quantity>0)&(duplicate_candidates.Price>0)]
    out = ROOT/'project/data'
    out.mkdir(exist_ok=True)
    weekly.to_parquet(out/'weekly-sales.parquet', index=False)
    meta = {
        'source': 'https://doi.org/10.24432/C5CG6D', 'licence': 'CC BY 4.0',
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'source_rows': len(raw), 'source_missing': {k:int(v) for k,v in raw.isna().sum().items()},
        'audit': audit, 'complete_week_start': str(first_week.date()), 'complete_week_end': str(last_week.date()),
        'retained_transaction_lines':len(data), 'aggregate_rows':len(weekly),
        'positive_duplicate_units_removed':float(dup_positive.Quantity.sum()),
        'positive_duplicate_value_removed_gbp':float((dup_positive.Quantity*dup_positive.Price).sum()),
        'eligible_units':float(data.Quantity.sum()), 'eligible_value_gbp':float(data.gross_sales_gbp.sum()),
        'large_positive_lines_above_1000_units_retained':int((data.Quantity>1000).sum()),
        'missing_customer_ids_retained':int(data['Customer ID'].isna().sum()),
        'missing_descriptions_retained':int(data.Description.isna().sum()),
        'sku_count':int(data.StockCode.nunique()),
        'published_columns':list(weekly.columns),
        'weekly_file_sha256':hashlib.sha256((out/'weekly-sales.parquet').read_bytes()).hexdigest(),
        'notes':['Audit removals are sequential, not overlapping.', 'Source workbook unchanged.', 'No customer identifiers, invoice identifiers or descriptions published.', 'Weekly aggregates disclose historical business activity; no person-level predictions.', 'Code pattern is a merchandise proxy, not a verified product taxonomy.']
    }
    (out/'quality-audit.json').write_text(json.dumps(meta, indent=2)+'\n')
    print(json.dumps(meta,indent=2))

if __name__=='__main__': main()
