import pandas as pd
from sqlalchemy import create_engine
import os

# --- PATH DEFINITION ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'db', 'business_data.db')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
SUMMARY_PATH = os.path.join(DATA_DIR, 'summary.csv')
OVERALL_KPI_PATH = os.path.join(DATA_DIR, 'overall_kpis.csv')


def extract():
    """Extracts raw sales and target data from the SQLite database."""

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database file not found at {DB_PATH}. Please run database_setup.py first.")

    engine = create_engine(f'sqlite:///{DB_PATH}')

    # Load sales data (ensure 'date' is parsed correctly)
    sales = pd.read_sql('SELECT * FROM sales_data',
                        engine, parse_dates=['date'])

    # Load targets data (ensure 'month' is treated as a string)
    targets = pd.read_sql('SELECT * FROM targets', engine)

    # Convert the month in targets to YYYY-MM format to match sales data aggregation
    if 'month' in targets.columns:
        # Assuming targets month is already in YYYY-MM string format from database_setup
        targets['month'] = targets['month'].astype(str)

    return sales, targets


def transform(sales, targets):
    """Transforms raw data into regional summaries and overall KPIs."""

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

    # Perform the merge. Use fillna(0) on revenue_target to avoid 'None'
    merged = region_summary.merge(
        latest_targets, how='left', on=['month', 'region'])

    # Fill missing targets with 0 for accurate calculation/display
    merged['revenue_target'] = merged['revenue_target'].fillna(0)

    # *** CRITICAL COLUMN CALCULATION ***
    merged['target_achievement_pct'] = (
        merged['revenue'] / merged['revenue_target'].replace(0, 1)).fillna(0) * 100

    # Replace the '1' used for division by zero back to 0 for display
    merged.loc[merged['revenue_target'] == 0, 'target_achievement_pct'] = 0

    # Overall KPIs
    overall = {
        'latest_month': latest_month,
        'total_revenue': float(monthly[monthly['month'] == latest_month]['revenue'].sum()),
        'total_profit': float(monthly[monthly['month'] == latest_month]['profit'].sum())
    }

    return merged, overall


def load_to_csv(merged, overall):
    """Saves the transformed data to CSV files using robust paths."""

    os.makedirs(DATA_DIR, exist_ok=True)
    merged.to_csv(SUMMARY_PATH, index=False)
    pd.DataFrame([overall]).to_csv(OVERALL_KPI_PATH, index=False)

    print(f"\nSUCCESS: Wrote new regional summary to {SUMMARY_PATH}")
    print(f"SUCCESS: Wrote new overall KPIs to {OVERALL_KPI_PATH}")


if __name__ == "__main__":
    try:
        sales, targets = extract()
        merged, overall = transform(sales, targets)
        load_to_csv(merged, overall)
    except FileNotFoundError as e:
        print(
            f"FATAL ERROR: Could not find required file. Ensure database_setup.py was run. Details: {e}")
    except Exception as e:
        print(f"FATAL ERROR: An unexpected error occurred during ETL: {e}")
