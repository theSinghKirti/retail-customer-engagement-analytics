import sqlite3
import pandas as pd
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(ROOT, 'retail.db'))

queries = {}

queries['revenue_by_country'] = """
SELECT Country,
       ROUND(SUM(Revenue),2) AS Revenue,
       COUNT(DISTINCT InvoiceNo) AS NumInvoices,
       COUNT(DISTINCT CustomerID) AS NumCustomers,
       ROUND(SUM(Revenue)/COUNT(DISTINCT InvoiceNo),2) AS AvgOrderValue
FROM sales
GROUP BY Country
ORDER BY Revenue DESC;
"""

queries['monthly_revenue_trend'] = """
SELECT InvoiceMonth,
       ROUND(SUM(Revenue),2) AS Revenue,
       COUNT(DISTINCT InvoiceNo) AS NumInvoices,
       COUNT(DISTINCT CustomerID) AS NumCustomers
FROM sales
GROUP BY InvoiceMonth
ORDER BY InvoiceMonth;
"""

queries['top_products_revenue'] = """
SELECT StockCode, Description,
       ROUND(SUM(Revenue),2) AS ProductRevenue,
       SUM(Quantity) AS TotalQtySold,
       COUNT(DISTINCT InvoiceNo) AS TimesPurchased
FROM sales
GROUP BY StockCode, Description
ORDER BY ProductRevenue DESC
LIMIT 15;
"""

queries['day_of_week'] = """
SELECT DayOfWeek,
       ROUND(SUM(Revenue),2) AS Revenue,
       COUNT(DISTINCT InvoiceNo) AS NumInvoices
FROM sales
GROUP BY DayOfWeek
ORDER BY Revenue DESC;
"""

queries['hourly_pattern'] = """
SELECT Hour,
       ROUND(SUM(Revenue),2) AS Revenue,
       COUNT(DISTINCT InvoiceNo) AS NumInvoices
FROM sales
GROUP BY Hour
ORDER BY Hour;
"""

queries['customer_metrics'] = """
SELECT CustomerID,
       MAX(InvoiceDate) AS LastPurchase,
       COUNT(DISTINCT InvoiceNo) AS Frequency,
       ROUND(SUM(Revenue),2) AS Monetary,
       Country
FROM sales
WHERE CustomerID IS NOT NULL
GROUP BY CustomerID;
"""

results = {}
for name, q in queries.items():
    results[name] = pd.read_sql_query(q, conn)
    results[name].to_csv(os.path.join(ROOT, 'outputs', f'out_{name}.csv'), index=False)
    print(name, results[name].shape)

conn.close()
