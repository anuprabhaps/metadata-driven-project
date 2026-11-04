"""Create a small customers.parquet file for local ingestion testing.

Run after installing pandas and pyarrow:
    pip install pandas pyarrow
    python create_sample_customers_parquet.py
"""
from pathlib import Path
import pandas as pd

customers = pd.DataFrame({
    "customer_id": ["CUST001", "CUST002", "CUST003", "CUST004", "CUST005"],
    "customer_name": ["Arun Kumar", "Priya Sharma", "Karthik Raj", "Meena Devi", "Sanjay Kumar"],
    "email": ["arun@example.com", "priya@example.com", "karthik@example.com", "meena@example.com", "sanjay@example.com"],
    "city": ["Coimbatore", "Chennai", "Bengaluru", "Kochi", "Hyderabad"],
    "signup_date": pd.to_datetime(["2025-01-12", "2025-02-03", "2025-03-18", "2025-04-09", "2025-05-21"]),
    "is_active": [True, True, False, True, True],
})

output_path = Path(__file__).parent / "sample_data" / "customers.parquet"
output_path.parent.mkdir(parents=True, exist_ok=True)
customers.to_parquet(output_path, index=False)
print(f"Created: {output_path}")
print(f"Rows: {len(customers)}")
print(customers.head())
