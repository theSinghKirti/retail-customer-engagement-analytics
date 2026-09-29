# Retail Sales & Customer Strategy Dashboard

A SQL + Python + Power BI project that goes beyond reporting: it turns 500K+ raw e-commerce
transactions into a **prioritized, revenue-quantified action plan** for a retail business —
not just charts, but answers to the questions a commercial/marketing leader actually asks.

**[📊 Open the dashboard (Power BI)](Retail.pbix)** · **[📄 View as PDF](Retail%20dashboard.pdf)** (no Power BI Desktop needed)

---

## The business questions this project answers

| # | Question | Answer (see dashboard) |
|---|----------|--------------------------|
| 1 | Where does our revenue actually come from, and is that healthy? | 65% of revenue comes from just 957 "Champion" customers (22% of the base) — a concentration risk, not just a success story. |
| 2 | Are we growing by acquiring customers, or reselling to the same ones? | New-customer revenue share fell from ~16% (Sep-Oct) to ~12% (Nov) — growth is increasingly dependent on repeat buyers. |
| 3 | Which customers should Marketing spend money trying to save right now? | £985,682 in historical revenue sits with "At Risk"/"Lost" customers — a win-back campaign could recover an estimated £147K-£246K. |
| 4 | Are there quick wins to raise order value without new customers? | Market basket analysis surfaces high-confidence cross-sell pairs (Lift > 190x) ready to bundle. |
| 5 | Where should the business expand next? | An opportunity-scoring model ranks Netherlands, EIRE and Australia above larger-but-lower-value markets. |

## What's in this repo

```
├── data/                       Raw dataset (gzip-compressed CSV)
├── sql/                        Database schema + documented analysis queries
├── scripts/                    Python pipeline (clean → analyze → segment → build star-schema tables)
├── outputs/                    All intermediate analysis results (CSV)
├── PowerBI_Package/
│   ├── data/                   Star-schema CSVs ready for Power BI import
│   │                           (fact_sales, dim_customer, dim_product, dim_date)
├── Retail.pbix                 Final deliverable — native Power BI dashboard
├── Retail dashboard.pdf        Static PDF export (for viewing without Power BI Desktop)
└── requirements.txt
```

## Dashboard contents (5 report pages)

1. **Executive Summary** — KPI cards (Total Revenue, Avg Order Value, Revenue at Churn Risk, Champion Revenue %), the monthly revenue trend, and the top strategic Q&A callouts answered in plain English
2. **Customer Segments (RFM)** — revenue share by segment (donut), customer count by segment, and a Recency/Frequency/Monetary averages table per segment
3. **Growth & Retention** — new vs. repeat customer revenue by year, customers by first-purchase month, and a monthly cohort retention matrix (% of each cohort still buying N months later)
4. **Country Expansion, Top Products & Recommendations** — opportunity-scored international markets, top products by revenue, and the 6 prioritized actions with estimated £ impact
5. **Cross-Sell Opportunities** — market basket analysis (Support/Confidence/Lift) surfacing product pairs worth bundling

## Methodology

- **Data**: [UCI Online Retail Dataset](https://archive.ics.uci.edu/dataset/352/online+retail) (Chen, D., 2015) — 541,909 real transaction lines from a UK-based online gift retailer, Dec 2010–Dec 2011. Licensed CC BY 4.0.
- **Cleaning**: removed cancelled invoices, returns/negative quantities, invalid prices, and duplicate rows (see `outputs/data_quality_report.csv` for exact counts).
- **SQL**: aggregation and reporting queries run in SQLite (`sql/analysis_queries.sql`).
- **RFM segmentation**: quantile-based Recency/Frequency/Monetary scoring in Python, 6 customer segments — pre-computed into `PowerBI_Package/data/dim_customer.csv`.
- **Market basket analysis**: co-occurrence, Support/Confidence/Lift computed per product pair from invoice line items in Python, imported into Power BI as a static reference table.
- **Cohort retention**: customers grouped by first-purchase month, tracked forward via a Power BI matrix visual to measure repeat-purchase rate by month.
- **Country opportunity score**: ranks markets by revenue-per-customer × AOV, normalized by customer count — surfaces high-value/low-penetration markets rather than just largest-by-revenue.
- **Power BI model**: a star schema (`fact_sales` + `dim_customer` / `dim_product` / `dim_date`) with 12+ DAX measures (Total Revenue, AOV, Revenue at Churn Risk, New vs. Repeat Revenue, Champion Revenue %, etc.). The complete model — every DAX formula, relationship and page layout — lives inside `Retail.pbix`; open it in Power BI Desktop and use **View → DAX query view** to read the measures.

## How to reproduce

```bash
pip install -r requirements.txt

python scripts/01_clean_and_load.py       # clean raw data, load into SQLite (retail.db)
python scripts/02_analysis_queries.py     # run core SQL reporting queries
python scripts/03_rfm_segmentation.py     # RFM customer segmentation
python scripts/05_strategic_analysis.py   # market basket, cohort retention, expansion scoring
```

Run them in that order — each script depends on the artefacts the previous one writes. (The
numbering skips `04`; there is no script with that prefix, and the gap is not referenced anywhere.)

This regenerates everything under `outputs/` and the star-schema tables in `PowerBI_Package/data/`.
To rebuild the dashboard itself: open Power BI Desktop, import the 4 CSVs in `PowerBI_Package/data/`,
and rebuild the relationships, DAX measures and report layout from `Retail.pbix` —
or simply open `Retail.pbix` directly.

## Tools

Python (Pandas) for data cleaning and analysis, SQL (SQLite) for reporting queries, Power BI (Power Query + DAX) for the data model and dashboard.

## License

Code in this repo: MIT. Dataset: CC BY 4.0, per [UCI's terms](https://archive.ics.uci.edu/dataset/352/online+retail) — cite Chen, D. (2015) if reused.
