# src/database_setup.py
import pandas as pd
import numpy as np
from faker import Faker
from sqlalchemy import create_engine
import os
from datetime import datetime, timedelta
fake = Faker()

# ensure db dir exists
os.makedirs('../db', exist_ok=True)


def generate_sales(n_rows=1000, start_date="2024-01-01"):
    regions = ['North', 'South', 'East', 'West']
    products = ['A', 'B', 'C', 'D']
    start = datetime.fromisoformat(start_date)
    rows = []
    for i in range(n_rows):
        date = start + timedelta(days=int(np.random.exponential(10)))
        region = np.random.choice(regions, p=[0.25, 0.25, 0.25, 0.25])
        product = np.random.choice(products, p=[0.3, 0.3, 0.2, 0.2])
        quantity = int(np.random.poisson(20))
        price = float(np.round(np.random.uniform(20, 200), 2))
        revenue = round(price * quantity, 2)
        cost = round(revenue * np.random.uniform(0.5, 0.85), 2)
        rows.append({
            'date': date.date().isoformat(),
            'region': region,
            'product': product,
            'revenue': revenue,
            'cost': cost,
            'quantity': quantity
        })
    return pd.DataFrame(rows)


def generate_targets(months=12):
    # targets per month per region
    regions = ['North', 'South', 'East', 'West']
    rows = []
    today = datetime.today()
    for m in range(months):
        month = (today - pd.DateOffset(months=m)).strftime('%Y-%m')
        for r in regions:
            target = int(np.random.uniform(50000, 150000))
            rows.append({'month': month, 'region': r,
                        'revenue_target': target})
    return pd.DataFrame(rows)


def main():
    sales = generate_sales(800, start_date="2024-01-01")
    targets = generate_targets(12)
    engine = create_engine('sqlite:///../db/business_data.db')
    sales.to_sql('sales_data', engine, if_exists='replace', index=False)
    targets.to_sql('targets', engine, if_exists='replace', index=False)
    print("Database created at ../db/business_data.db with tables: sales_data, targets")
    print(sales.head())


if __name__ == "__main__":
    main()
