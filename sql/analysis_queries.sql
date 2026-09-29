-- ============================================================
-- Retail Sales & Customer Segmentation — Analysis Queries
-- Run against retail.db (SQLite) created by scripts/01_clean_and_load.py
-- ============================================================

-- 1. Revenue by country, with order count, customer count and AOV
SELECT
    Country,
    ROUND(SUM(Revenue), 2)                                   AS Revenue,
    COUNT(DISTINCT InvoiceNo)                                AS NumInvoices,
    COUNT(DISTINCT CustomerID)                                AS NumCustomers,
    ROUND(SUM(Revenue) / COUNT(DISTINCT InvoiceNo), 2)        AS AvgOrderValue
FROM sales
GROUP BY Country
ORDER BY Revenue DESC;

-- 2. Monthly revenue trend
SELECT
    InvoiceMonth,
    ROUND(SUM(Revenue), 2)      AS Revenue,
    COUNT(DISTINCT InvoiceNo)   AS NumInvoices,
    COUNT(DISTINCT CustomerID)  AS NumCustomers
FROM sales
GROUP BY InvoiceMonth
ORDER BY InvoiceMonth;

-- 3. Top products by revenue
SELECT
    StockCode,
    Description,
    ROUND(SUM(Revenue), 2)      AS ProductRevenue,
    SUM(Quantity)                AS TotalQtySold,
    COUNT(DISTINCT InvoiceNo)    AS TimesPurchased
FROM sales
GROUP BY StockCode, Description
ORDER BY ProductRevenue DESC
LIMIT 15;

-- 4. Day-of-week performance
SELECT
    DayOfWeek,
    ROUND(SUM(Revenue), 2)     AS Revenue,
    COUNT(DISTINCT InvoiceNo)  AS NumInvoices
FROM sales
GROUP BY DayOfWeek
ORDER BY Revenue DESC;

-- 5. Hourly sales pattern
SELECT
    Hour,
    ROUND(SUM(Revenue), 2)     AS Revenue,
    COUNT(DISTINCT InvoiceNo)  AS NumInvoices
FROM sales
GROUP BY Hour
ORDER BY Hour;

-- 6. Customer-level metrics (feeds the RFM segmentation in Python)
SELECT
    CustomerID,
    MAX(InvoiceDate)             AS LastPurchase,
    COUNT(DISTINCT InvoiceNo)    AS Frequency,
    ROUND(SUM(Revenue), 2)       AS Monetary,
    Country
FROM sales
WHERE CustomerID IS NOT NULL
GROUP BY CustomerID;

-- 7. RFM segmentation, done natively in SQL (equivalent to scripts/03_rfm_segmentation.py,
--    provided here to show the pure-SQL approach — quantile scoring is easier to keep flexible in Python/pandas,
--    so the shipped pipeline uses the Python version).
WITH customer_metrics AS (
    SELECT
        CustomerID,
        MAX(InvoiceDate) AS last_purchase_date,
        COUNT(DISTINCT InvoiceNo) AS frequency,
        ROUND(SUM(Revenue), 2) AS monetary_value
    FROM sales
    WHERE CustomerID IS NOT NULL
    GROUP BY CustomerID
),
rfm_scores AS (
    SELECT
        CustomerID, last_purchase_date, frequency, monetary_value,
        CASE
            WHEN last_purchase_date >= date('2011-12-09', '-30 days') THEN 5
            WHEN last_purchase_date >= date('2011-12-09', '-60 days') THEN 4
            WHEN last_purchase_date >= date('2011-12-09', '-90 days') THEN 3
            WHEN last_purchase_date >= date('2011-12-09', '-180 days') THEN 2
            ELSE 1
        END AS recency_score,
        CASE
            WHEN frequency >= 20 THEN 5
            WHEN frequency >= 10 THEN 4
            WHEN frequency >= 5  THEN 3
            WHEN frequency >= 2  THEN 2
            ELSE 1
        END AS frequency_score,
        CASE
            WHEN monetary_value >= 5000 THEN 5
            WHEN monetary_value >= 2000 THEN 4
            WHEN monetary_value >= 1000 THEN 3
            WHEN monetary_value >= 500  THEN 2
            ELSE 1
        END AS monetary_score
    FROM customer_metrics
)
SELECT
    CustomerID, recency_score, frequency_score, monetary_score,
    (recency_score + frequency_score + monetary_score) AS rfm_score,
    CASE
        WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
        WHEN recency_score >= 3 AND frequency_score >= 3 THEN 'Loyal Customers'
        WHEN recency_score >= 4 AND frequency_score <= 2 THEN 'New/Promising'
        WHEN recency_score <= 2 AND frequency_score >= 3 THEN 'At Risk'
        WHEN recency_score <= 2 AND frequency_score <= 2 THEN 'Lost'
        ELSE 'Need Attention'
    END AS customer_segment
FROM rfm_scores
ORDER BY rfm_score DESC;

-- 8. Data quality checks
SELECT
    COUNT(*)                                                       AS total_rows,
    SUM(CASE WHEN CustomerID IS NULL THEN 1 ELSE 0 END)            AS missing_customer_id,
    ROUND(100.0 * SUM(CASE WHEN CustomerID IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_missing
FROM all_transactions;
