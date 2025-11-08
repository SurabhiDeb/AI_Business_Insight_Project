# src/etl_pipeline.py
import pandas as pd
from sqlalchemy import create_engine


def extract():
    engine = create_engine('sqlite:///../db/business_data.db')
    sales = pd.read_sql('SELECT * FROM sales_data',
                        engine, parse_dates=['date'])
    targets = pd.read_sql('SELECT * FROM targets', engine)
    return sales, targets


def transform(sales, targets):
    # Add profit column
    sales['profit'] = sales['revenue'] - sales['cost']

    # Monthly aggregation
    sales['month'] = sales['date'].dt.strftime('%Y-%m')
    monthly = sales.groupby(['month', 'region']).agg({
        'revenue': 'sum',
        'profit': 'sum',
        'quantity': 'sum'
    }).reset_index()

    # region summary (latest month)
    latest_month = monthly['month'].max()
    region_summary = monthly[monthly['month'] == latest_month].copy()
    region_summary['profit_margin'] = (
        region_summary['profit'] / region_summary['revenue']).fillna(0) * 100

    # Merge with targets
    latest_targets = targets[targets['month'] == latest_month]
    merged = region_summary.merge(
        latest_targets, how='left', on=['month', 'region'])
    merged['target_achievement_pct'] = (
        merged['revenue'] / merged['revenue_target']).fillna(0) * 100

    # Overall KPIs
    overall = {
        'latest_month': latest_month,
        'total_revenue': float(monthly[monthly['month'] == latest_month]['revenue'].sum()),
        'total_profit': float(monthly[monthly['month'] == latest_month]['profit'].sum())
    }

    return merged, overall


def load_to_csv(merged, overall):
    import os
    os.makedirs('../data', exist_ok=True)
    merged.to_csv('../data/summary.csv', index=False)
    pd.DataFrame([overall]).to_csv('../data/overall_kpis.csv', index=False)
    print("Wrote ../data/summary.csv and overall_kpis.csv")


if __name__ == "__main__":
    sales, targets = extract()
    merged, overall = transform(sales, targets)
    load_to_csv(merged, overall)
