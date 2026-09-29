import pandas as pd
import sqlite3
import os
from itertools import combinations
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(ROOT, 'retail.db'))
sales = pd.read_csv(os.path.join(ROOT, 'outputs', 'clean_sales.csv'), parse_dates=['InvoiceDate'])

# ============================================================
# 0) Clean "Top Products" list — drop non-product admin codes
#    (postage, manual adjustments, bank charges, etc.) so the
#    dashboard's product ranking reflects real merchandise only.
# ============================================================
non_product_codes = ['POST', 'DOT', 'M', 'C2', 'BANK CHARGES', 'PADS', 'AMAZONFEE', 'CRUK']
top_products = pd.read_csv(os.path.join(ROOT, 'outputs', 'out_top_products_revenue.csv'))
top_products_clean = top_products[~top_products['StockCode'].isin(non_product_codes)]
top_products_clean.head(15).to_csv(os.path.join(ROOT, 'outputs', 'out_top_products_revenue_clean.csv'), index=False)


# ============================================================
# 1) MARKET BASKET ANALYSIS — cross-sell / bundle opportunities
# ============================================================
# Build basket: InvoiceNo -> set of product descriptions (exclude non-product codes)
non_product = {'POST','DOT','M','C2','BANK CHARGES','PADS','AMAZONFEE','CRUK'}
basket_df = sales[~sales['StockCode'].isin(non_product)]

baskets = basket_df.groupby('InvoiceNo')['Description'].apply(lambda x: set(x.dropna())).reset_index()
baskets = baskets[baskets['Description'].apply(len) >= 2]

pair_counter = Counter()
item_counter = Counter()
for items in baskets['Description']:
    for item in items:
        item_counter[item] += 1
    for a, b in combinations(sorted(items), 2):
        pair_counter[(a, b)] += 1

total_baskets = len(baskets)
rows = []
for (a, b), co_count in pair_counter.items():
    if co_count < 30:
        continue
    support = co_count / total_baskets
    conf_a_b = co_count / item_counter[a]
    conf_b_a = co_count / item_counter[b]
    lift = support / ((item_counter[a] / total_baskets) * (item_counter[b] / total_baskets))
    rows.append({
        'Product A': a, 'Product B': b, 'TimesBoughtTogether': co_count,
        'Support': round(support, 4), 'Confidence A->B': round(conf_a_b, 3),
        'Confidence B->A': round(conf_b_a, 3), 'Lift': round(lift, 2)
    })

basket_result = pd.DataFrame(rows).sort_values('Lift', ascending=False)
basket_result = basket_result[basket_result['Lift'] > 1]  # only genuine cross-sell signal
basket_result.head(20).to_csv(os.path.join(ROOT, 'outputs', 'out_market_basket.csv'), index=False)
print("Top cross-sell pairs:")
print(basket_result.head(10))

# ============================================================
# 2) COHORT RETENTION ANALYSIS — how sticky is the customer base?
# ============================================================
cust_sales = sales.dropna(subset=['CustomerID']).copy()
cust_sales['CustomerID'] = cust_sales['CustomerID'].astype(int)
cust_sales['OrderMonth'] = cust_sales['InvoiceDate'].dt.to_period('M')
first_purchase = cust_sales.groupby('CustomerID')['OrderMonth'].min().rename('CohortMonth')
cust_sales = cust_sales.join(first_purchase, on='CustomerID')
cust_sales['CohortIndex'] = (cust_sales['OrderMonth'] - cust_sales['CohortMonth']).apply(lambda x: x.n)

cohort_data = cust_sales.groupby(['CohortMonth', 'CohortIndex'])['CustomerID'].nunique().reset_index()
cohort_pivot = cohort_data.pivot(index='CohortMonth', columns='CohortIndex', values='CustomerID')
cohort_size = cohort_pivot.iloc[:, 0]
retention = cohort_pivot.divide(cohort_size, axis=0).round(3)

retention.to_csv(os.path.join(ROOT, 'outputs', 'out_cohort_retention.csv'))
cohort_pivot.to_csv(os.path.join(ROOT, 'outputs', 'out_cohort_counts.csv'))

# Overall month-1 retention rate (industry-comparable KPI)
month1_retention = retention[1].mean() if 1 in retention.columns else None
print(f"\nAvg Month-1 retention rate: {month1_retention:.1%}" if month1_retention else "N/A")

# ============================================================
# 3) NEW vs REPEAT CUSTOMER REVENUE SPLIT (per month)
# ============================================================
cust_sales['IsFirstMonth'] = cust_sales['CohortIndex'] == 0
monthly_split = cust_sales.groupby(['OrderMonth', 'IsFirstMonth'])['Revenue'].sum().unstack(fill_value=0)
monthly_split.columns = ['Repeat_Revenue', 'New_Revenue']
monthly_split['Total'] = monthly_split.sum(axis=1)
monthly_split['New_Pct'] = (monthly_split['New_Revenue'] / monthly_split['Total']).round(3)
monthly_split['Repeat_Pct'] = (monthly_split['Repeat_Revenue'] / monthly_split['Total']).round(3)
monthly_split.index = monthly_split.index.astype(str)
monthly_split.to_csv(os.path.join(ROOT, 'outputs', 'out_new_vs_repeat.csv'))
print("\nNew vs Repeat revenue split (last 3 months):")
print(monthly_split.tail(3))

# ============================================================
# 4) COUNTRY EXPANSION OPPORTUNITY SCORE
# ============================================================
country_stats = sales.groupby('Country').agg(
    Revenue=('Revenue', 'sum'),
    Customers=('CustomerID', 'nunique'),
    Orders=('InvoiceNo', 'nunique')
).reset_index()
country_stats = country_stats[country_stats['Country'] != 'United Kingdom']
country_stats = country_stats[country_stats['Customers'] > 0]
country_stats['RevenuePerCustomer'] = (country_stats['Revenue'] / country_stats['Customers']).round(2)
country_stats['AvgOrderValue'] = (country_stats['Revenue'] / country_stats['Orders']).round(2)
# Opportunity = high value-per-customer but still low customer count (untapped high-value market)
country_stats['OpportunityScore'] = (country_stats['RevenuePerCustomer'] * country_stats['AvgOrderValue']) / (country_stats['Customers'] + 1)
country_stats['OpportunityScore'] = country_stats['OpportunityScore'].round(0).astype(int)
country_stats = country_stats.sort_values('OpportunityScore', ascending=False)
country_stats.head(10).to_csv(os.path.join(ROOT, 'outputs', 'out_country_opportunity.csv'), index=False)
print("\nTop expansion opportunity markets:")
print(country_stats.head(5)[['Country','Revenue','Customers','RevenuePerCustomer','AvgOrderValue']])

# ============================================================
# 5) CHURN REVENUE AT RISK (quantified)
# ============================================================
rfm = pd.read_csv(os.path.join(ROOT, 'outputs', 'out_rfm_segments.csv'))
at_risk_value = rfm[rfm['Segment'].isin(['At Risk','Lost'])]['Monetary'].sum()
champions_value = rfm[rfm['Segment']=='Champions']['Monetary'].sum()
total_value = rfm['Monetary'].sum()
print(f"\nRevenue at risk (At Risk + Lost): £{at_risk_value:,.0f} ({at_risk_value/total_value:.1%} of historical revenue)")
print(f"Champions revenue concentration: £{champions_value:,.0f} ({champions_value/total_value:.1%})")

conn.close()
