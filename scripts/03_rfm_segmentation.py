import pandas as pd
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(ROOT, 'outputs', 'out_customer_metrics.csv'), parse_dates=['LastPurchase'])
snapshot_date = df['LastPurchase'].max() + pd.Timedelta(days=1)
df['Recency'] = (snapshot_date - df['LastPurchase']).dt.days

# Score 1-5 using quantiles (5 = best)
df['R_Score'] = pd.qcut(df['Recency'], 5, labels=[5,4,3,2,1]).astype(int)
df['F_Score'] = pd.qcut(df['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
df['M_Score'] = pd.qcut(df['Monetary'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
df['RFM_Score'] = df['R_Score'] + df['F_Score'] + df['M_Score']

def segment(row):
    r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
    if r >= 4 and f >= 4 and m >= 4:
        return 'Champions'
    elif r >= 3 and f >= 3 and m >= 3:
        return 'Loyal Customers'
    elif r >= 4 and f <= 2:
        return 'New/Promising'
    elif r <= 2 and f >= 3:
        return 'At Risk'
    elif r <= 2 and f <= 2 and m <= 2:
        return 'Lost'
    else:
        return 'Need Attention'

df['Segment'] = df.apply(segment, axis=1)
df.to_csv(os.path.join(ROOT, 'outputs', 'out_rfm_segments.csv'), index=False)

summary = df.groupby('Segment').agg(
    NumCustomers=('CustomerID','count'),
    AvgRecency=('Recency','mean'),
    AvgFrequency=('Frequency','mean'),
    AvgMonetary=('Monetary','mean'),
    TotalRevenue=('Monetary','sum')
).round(1).sort_values('TotalRevenue', ascending=False)
summary.to_csv(os.path.join(ROOT, 'outputs', 'out_rfm_summary.csv'))
print(summary)
print()
print(df['Segment'].value_counts())
