import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_data():
    os.makedirs("data", exist_ok=True)
    
    # 1. Dim Product
    categories = ['Electronics', 'Clothing', 'Home', 'Toys', 'Sports']
    products = []
    for i in range(50):
        cat = np.random.choice(categories)
        products.append({
            'product_id': f'P{i:03d}',
            'product_name': f'{cat} Product {i}',
            'category': cat,
            'price': np.random.uniform(10, 500)
        })
    dim_product = pd.DataFrame(products)
    dim_product.to_parquet("data/dim_product.parquet")
    print("Generated data/dim_product.parquet")

    # 2. Dim Store
    regions = ['North', 'South', 'East', 'West']
    stores = []
    for i in range(10):
        stores.append({
            'store_id': f'S{i:02d}',
            'store_name': f'Store {i}',
            'region': np.random.choice(regions),
            'city': f'City {i}'
        })
    dim_store = pd.DataFrame(stores)
    dim_store.to_parquet("data/dim_store.parquet")
    print("Generated data/dim_store.parquet")

    # 3. Fct Sales
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=x) for x in range(365)]
    
    sales_data = []
    for date in dates:
        # Generate 50 transactions per day
        for _ in range(50):
            prod = dim_product.sample(1).iloc[0]
            store = dim_store.sample(1).iloc[0]
            qty = np.random.randint(1, 5)
            gross_sales = qty * prod['price']
            
            sales_data.append({
                'order_id': f'O{len(sales_data):06d}',
                'order_date': date,
                'product_id': prod['product_id'],
                'store_id': store['store_id'],
                'quantity': qty,
                'gross_sales': gross_sales,
                'net_sales': gross_sales * 0.9, # 10% tax/discount
                'returns': 1 if np.random.random() < 0.05 else 0, # 5% return rate
                'tenant_id': 'tenant_123' # Default tenant
            })
            
    fct_sales = pd.DataFrame(sales_data)
    fct_sales.to_parquet("data/fct_sales.parquet")
    print("Generated data/fct_sales.parquet")

if __name__ == "__main__":
    generate_data()
