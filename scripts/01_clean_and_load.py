import pandas as pd
import sqlite3
import os

# All paths are relative to the project root (run this script with `python scripts/01_clean_and_load.py`
# from the repo root, or `cd scripts && python 01_clean_and_load.py`).
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(ROOT, 'outputs'), exist_ok=True)

# Load raw data preserving InvoiceNo as string (to catch cancellations starting with 'C')
df = pd.read_csv(os.path.join(ROOT, 'data', 'online_retail_raw.csv.gz'),
                  dtype={'InvoiceNo': str, 'StockCode': str})

print("Raw shape:", df.shape)

# --- Data Quality Report (before cleaning) ---
quality_report = {
    'total_rows': len(df),
    'missing_description': int(df['Description'].isnull().sum()),
    'missing_customerid': int(df['CustomerID'].isnull().sum()),
    'cancelled_invoices': int(df['InvoiceNo'].str.startswith('C').sum()),
    'negative_quantity_rows': int((df['Quantity'] < 0).sum()),
    'zero_or_negative_price_rows': int((df['UnitPrice'] <= 0).sum()),
    'duplicate_rows': int(df.duplicated().sum()),
}
print(quality_report)

# --- Cleaning steps ---
df_clean = df.copy()
df_clean['is_cancelled'] = df_clean['InvoiceNo'].str.startswith('C')

# Drop duplicates
df_clean = df_clean.drop_duplicates()

# Keep only valid sales lines for revenue analysis (positive qty, positive price, not cancelled)
df_valid = df_clean[(~df_clean['is_cancelled']) & (df_clean['Quantity'] > 0) & (df_clean['UnitPrice'] > 0)].copy()

# Drop rows with missing CustomerID for customer-level analysis, keep separately for product/country analysis
df_valid['Revenue'] = df_valid['Quantity'] * df_valid['UnitPrice']
df_valid['InvoiceDate'] = pd.to_datetime(df_valid['InvoiceDate'])
df_valid['InvoiceMonth'] = df_valid['InvoiceDate'].dt.to_period('M').astype(str)
df_valid['InvoiceYear'] = df_valid['InvoiceDate'].dt.year
df_valid['DayOfWeek'] = df_valid['InvoiceDate'].dt.day_name()
df_valid['Hour'] = df_valid['InvoiceDate'].dt.hour

print("Clean valid-sales shape:", df_valid.shape)
print("Revenue total (valid sales):", df_valid['Revenue'].sum())

# Save cleaned datasets
df_valid.to_csv(os.path.join(ROOT, 'outputs', 'clean_sales.csv'), index=False)
quality_df = pd.DataFrame([quality_report])
quality_df.to_csv(os.path.join(ROOT, 'outputs', 'data_quality_report.csv'), index=False)

# --- Load into SQLite ---
conn = sqlite3.connect(os.path.join(ROOT, 'retail.db'))
df_valid.to_sql('sales', conn, if_exists='replace', index=False)
df_clean.to_sql('all_transactions', conn, if_exists='replace', index=False)
conn.execute("CREATE INDEX idx_customer ON sales(CustomerID);")
conn.execute("CREATE INDEX idx_date ON sales(InvoiceDate);")
conn.execute("CREATE INDEX idx_country ON sales(Country);")
conn.commit()
conn.close()
print("Loaded into retail.db")
