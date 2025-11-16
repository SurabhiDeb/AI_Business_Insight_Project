import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Define paths relative to the project root for robustness
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(PROJECT_ROOT, 'db')
DB_PATH = os.path.join(DB_DIR, 'business_data.db')

# Ensure db directory exists
os.makedirs(DB_DIR, exist_ok=True)


def generate_sales(n_rows=50000, start_date_offset_months=6):
    """Generates synthetic sales transaction data for the last N months."""
    regions = ['North', 'South', 'East', 'West']
    products = ['A', 'B', 'C', 'D']

    # Start date is 6 months ago to ensure we have a full "latest month"
    start = datetime.today() - relativedelta(months=start_date_offset_months)
    rows = []

    # Generate random sales data
    for i in range(n_rows):
        # Generate date spanning the last 6 months
        date_offset = np.random.randint(0, 30 * start_date_offset_months)
        date = start + timedelta(days=date_offset)

        region = np.random.choice(regions)
        product = np.random.choice(products, p=[0.3, 0.3, 0.2, 0.2])

        # Quantity and Price setup to yield higher revenues
        quantity = int(np.random.normal(loc=50, scale=10))
        price = float(np.round(np.random.uniform(50, 500), 2))

        revenue = round(price * quantity, 2)
        cost = round(revenue * np.random.uniform(0.5, 0.75), 2)

        rows.append({
            'date': date.date().isoformat(),
            'region': region,
            'product': product,
            'revenue': revenue,
            'cost': cost,
            'quantity': quantity
        })

    return pd.DataFrame(rows)


def generate_targets(months=6):
    """Generates synthetic monthly revenue targets per region for the last N months."""
    regions = ['North', 'South', 'East', 'West']
    rows = []

    for m in range(months):
        # Calculate the month string (e.g., '2025-11')
        month = (datetime.today() - relativedelta(months=m)).strftime('%Y-%m')
        for r in regions:
            # Generate higher target revenue between 200k and 500k
            target = int(np.random.uniform(200000, 500000))
            rows.append({'month': month, 'region': r,
                        'revenue_target': target})
    return pd.DataFrame(rows)


def main():
    # Generate high volume data for 6 months
    sales = generate_sales(n_rows=50000, start_date_offset_months=6)
    targets = generate_targets(months=6)

    # Create SQLAlchemy engine
    engine = create_engine(f'sqlite:///{DB_PATH}')

    # Load data into the database
    sales.to_sql('sales_data', engine, if_exists='replace', index=False)
    targets.to_sql('targets', engine, if_exists='replace', index=False)

    print(f"Database created at {DB_PATH} with tables: sales_data, targets")
    print(sales.head())


if __name__ == "__main__":
    main()
