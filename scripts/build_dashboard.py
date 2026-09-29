import pandas as pd
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.worksheet.page import PageMargins

# ---------- Load all analysis outputs ----------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'outputs')
revenue_country = pd.read_csv(os.path.join(OUT, 'out_revenue_by_country.csv'))
monthly_trend = pd.read_csv(os.path.join(OUT, 'out_monthly_revenue_trend.csv'))
top_products = pd.read_csv(os.path.join(OUT, 'out_top_products_revenue_clean.csv'))
day_of_week = pd.read_csv(os.path.join(OUT, 'out_day_of_week.csv'))
hourly = pd.read_csv(os.path.join(OUT, 'out_hourly_pattern.csv'))
rfm_summary = pd.read_csv(os.path.join(OUT, 'out_rfm_summary.csv'))
rfm_detail = pd.read_csv(os.path.join(OUT, 'out_rfm_segments.csv'))
quality = pd.read_csv(os.path.join(OUT, 'data_quality_report.csv'))
basket = pd.read_csv(os.path.join(OUT, 'out_market_basket.csv'))
retention = pd.read_csv(os.path.join(OUT, 'out_cohort_retention.csv'), index_col=0)
new_vs_repeat = pd.read_csv(os.path.join(OUT, 'out_new_vs_repeat.csv'))
country_opp = pd.read_csv(os.path.join(OUT, 'out_country_opportunity.csv'))

TOTAL_REVENUE = 10642110.80
TOTAL_ORDERS = 19962
TOTAL_CUSTOMERS = 4338
AOV = 533.12
AT_RISK_VALUE = 985682
CHAMPIONS_VALUE = 5791641
CHAMPIONS_PCT = 0.652

# ---------- Styling ----------
NAVY = "1F3864"
ACCENT = "2E5395"
GOLD = "C9A227"
GREEN = "2E7D32"
RED = "C62828"
GREY = "757575"
WHITE = "FFFFFF"

title_font = Font(name="Calibri", size=20, bold=True, color=NAVY)
subtitle_font = Font(name="Calibri", size=11, italic=True, color=GREY)
header_font = Font(name="Calibri", size=11, bold=True, color=WHITE)
header_fill = PatternFill(start_color=ACCENT, end_color=ACCENT, fill_type="solid")
kpi_label_font = Font(name="Calibri", size=11, bold=True, color=WHITE)
kpi_value_font = Font(name="Calibri", size=20, bold=True, color=WHITE)
section_font = Font(name="Calibri", size=13, bold=True, color=NAVY)
subsection_font = Font(name="Calibri", size=11, bold=True, color=ACCENT)
thin = Side(style="thin", color="BFBFBF")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

def style_header_row(ws, row, ncols, start_col=1):
    for c in range(start_col, start_col + ncols):
        cell = ws.cell(row=row, column=c)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border

def style_data_rows(ws, start_row, end_row, ncols, start_col=1):
    for r in range(start_row, end_row + 1):
        for c in range(start_col, start_col + ncols):
            cell = ws.cell(row=r, column=c)
            cell.border = border
            if r % 2 == 0:
                cell.fill = PatternFill(start_color="F2F5FB", end_color="F2F5FB", fill_type="solid")

def autofit(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

def write_df(ws, df, start_row, start_col=1):
    ncols = len(df.columns)
    for j, col in enumerate(df.columns):
        ws.cell(row=start_row, column=start_col + j, value=col)
    style_header_row(ws, start_row, ncols, start_col)
    for i, row in enumerate(df.itertuples(index=False), start=1):
        for j, val in enumerate(row):
            ws.cell(row=start_row + i, column=start_col + j, value=val)
    style_data_rows(ws, start_row + 1, start_row + len(df), ncols, start_col)
    return start_row + len(df)

def set_print(ws):
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins = PageMargins(left=0.3, right=0.3, top=0.4, bottom=0.4)
    ws.sheet_view.showGridLines = False

wb = Workbook()

# =========================================================
# SHEET 1: EXECUTIVE SUMMARY — the "business brain" page
# =========================================================
ws = wb.active
ws.title = "Executive Summary"
set_print(ws)

ws.merge_cells("A1:J1")
ws["A1"] = "Retail Growth & Customer Strategy Dashboard"
ws["A1"].font = title_font

ws.merge_cells("A2:J2")
ws["A2"] = "UK Online Gift Retailer | Dec 2010 - Dec 2011 | Prepared for: Commercial & Marketing Leadership"
ws["A2"].font = subtitle_font

kpis = [
    ("Total Revenue", f"£{TOTAL_REVENUE:,.0f}"),
    ("Avg Order Value", f"£{AOV:,.2f}"),
    ("Revenue at Churn Risk", f"£{AT_RISK_VALUE:,.0f}"),
    ("Revenue from Top 22% Customers", f"{CHAMPIONS_PCT:.0%}"),
]
col = 1
for label, value in kpis:
    ws.merge_cells(start_row=4, start_column=col, end_row=4, end_column=col + 1)
    ws.merge_cells(start_row=5, start_column=col, end_row=6, end_column=col + 1)
    lbl = ws.cell(row=4, column=col, value=label)
    lbl.font = kpi_label_font
    lbl.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
    lbl.alignment = Alignment(horizontal="center")
    val = ws.cell(row=5, column=col, value=value)
    val.font = kpi_value_font
    val.fill = PatternFill(start_color=ACCENT, end_color=ACCENT, fill_type="solid")
    val.alignment = Alignment(horizontal="center", vertical="center")
    col += 2
ws.row_dimensions[5].height = 40

# ---- Strategic Q&A block: the dashboard "thinks" like a business consultant ----
ws["A8"] = "The 5 Business Questions This Data Answers"
ws["A8"].font = section_font

qa = [
    ("Q1. Where is our revenue actually coming from, and is that healthy?",
     "65% of revenue comes from just 957 'Champion' customers (22% of the base). This is a concentration risk, not just a success story — losing a handful of these accounts would materially hurt revenue. See: Customer Segments (RFM)."),
    ("Q2. Are we growing by acquiring customers, or just re-selling to the same ones?",
     "New-customer revenue share fell from ~16% (Sep-Oct) to ~12% (Nov). Growth is increasingly dependent on repeat buyers — acquisition marketing may be under-invested. See: Growth Mix."),
    ("Q3. Which customers should Marketing spend money trying to save right now?",
     "£985,682 in historical revenue sits with 'At Risk' and 'Lost' customers (1,464 people). A 15% win-back campaign would recover an estimated £147,852. See: Customer Segments (RFM)."),
    ("Q4. Are there quick wins to increase order value without new customers?",
     "Several product pairs are bought together far more often than chance (Lift > 190x), e.g. matching color variants (Blue/Pink Scottie Dog, Landmark Frames). These are ready-made bundle/cross-sell opportunities. See: Cross-Sell Opportunities."),
    ("Q5. Where should the business expand next?",
     "EIRE, Netherlands and Australia show high revenue-per-customer with a still-small customer base — a stronger buy signal for expansion spend than large-but-low-value markets. See: Country Expansion Opportunity."),
]
r = 9
for q, a in qa:
    ws.cell(row=r, column=1, value=q).font = Font(bold=True, size=11, color=NAVY)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=10)
    ws.row_dimensions[r].height = 18
    r += 1
    ws.cell(row=r, column=1, value=a).alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=10)
    ws.row_dimensions[r].height = 30
    r += 2

autofit(ws, [13]*10)

# =========================================================
# SHEET 2: Strategic Recommendations (action plan)
# =========================================================
ws2 = wb.create_sheet("Strategic Recommendations")
set_print(ws2)
ws2["A1"] = "Recommended Actions — Prioritized by Estimated Revenue Impact"
ws2["A1"].font = section_font

rec_data = [
    ["Priority", "Recommendation", "Why (Evidence)", "Estimated Impact", "Owner"],
    ["1 - High", "Launch a win-back campaign (targeted discount/email) for 'At Risk' and 'Lost' segments",
     "1,464 customers, £985,682 in historical spend, no purchase in 90-365+ days", "+£147K-£246K recovered (15-25% win-back)", "CRM / Marketing"],
    ["2 - High", "Build a VIP retention program for 'Champions' (957 customers)",
     "This group drives 65% of revenue — losing even 5% of them is a bigger risk than any single growth initiative", "Protects £5.79M revenue base", "Customer Success"],
    ["3 - Medium", "Create bundles from high-lift product pairs (color/style variants)",
     "Pairs like Blue/Pink Scottie Dog and Landmark Frame sets are bought together 190x+ more than chance", "Est. +3-6% AOV on affected SKUs", "Merchandising"],
    ["4 - Medium", "Increase new-customer acquisition spend",
     "New-customer revenue share is trending down (~16% to ~12%) while repeat share rises — growth is not being replenished", "Protects future revenue pipeline", "Marketing"],
    ["5 - Medium", "Prioritize EIRE, Netherlands, Australia for international marketing spend",
     "Highest revenue-per-customer among non-UK markets, still small customer base = room to grow before diminishing returns", "Est. 2-3x ROI vs. low-value-per-customer markets", "International / Growth"],
    ["6 - Lower", "Ramp inventory & support staffing from August for Sep-Nov peak",
     "September revenue jumps ~40% vs August every year in this data; Nov is the single highest month", "Avoids stockouts during highest-revenue period", "Operations"],
]
for i, row in enumerate(rec_data):
    for j, val in enumerate(row):
        ws2.cell(row=3+i, column=1+j, value=val)
style_header_row(ws2, 3, 5)
for r in range(4, 3+len(rec_data)):
    for c in range(1, 6):
        ws2.cell(row=r, column=c).alignment = Alignment(wrap_text=True, vertical="top")
        ws2.cell(row=r, column=c).border = border
        if r % 2 == 0:
            ws2.cell(row=r, column=c).fill = PatternFill(start_color="F2F5FB", end_color="F2F5FB", fill_type="solid")
    ws2.row_dimensions[r].height = 48
autofit(ws2, [11, 30, 42, 24, 16])

ws2["A" + str(4+len(rec_data))] = "Note: revenue-impact figures are directional estimates based on this dataset's own history, not guarantees — intended to prioritize where to test first."
ws2["A" + str(4+len(rec_data))].font = subtitle_font
ws2.merge_cells(start_row=4+len(rec_data), start_column=1, end_row=4+len(rec_data), end_column=5)

# =========================================================
# SHEET 3: Customer Segments (RFM)
# =========================================================
ws3 = wb.create_sheet("Customer Segments (RFM)")
set_print(ws3)
ws3["A1"] = "Customer Segmentation Summary (RFM Analysis)"
ws3["A1"].font = section_font
write_df(ws3, rfm_summary, start_row=3)
autofit(ws3, [18, 14, 14, 14, 14, 16])

pchart = PieChart()
pchart.title = "Revenue Contribution by Segment"
data = Reference(ws3, min_col=6, min_row=3, max_row=3+len(rfm_summary))
cats = Reference(ws3, min_col=1, min_row=4, max_row=3+len(rfm_summary))
pchart.add_data(data, titles_from_data=True)
pchart.set_categories(cats)
pchart.height = 10
pchart.width = 16
ws3.add_chart(pchart, "H3")

bchart2 = BarChart()
bchart2.title = "Customer Count by Segment"
data = Reference(ws3, min_col=2, min_row=3, max_row=3+len(rfm_summary))
cats = Reference(ws3, min_col=1, min_row=4, max_row=3+len(rfm_summary))
bchart2.add_data(data, titles_from_data=True)
bchart2.set_categories(cats)
bchart2.height = 10
bchart2.width = 16
ws3.add_chart(bchart2, "H21")

ws3["A11"] = "Action Guide by Segment"
ws3["A11"].font = subsection_font
guide = [
    ("Champions", "Reward & retain: early access, loyalty perks. Do not discount — protect margin."),
    ("Loyal Customers", "Upsell path to Champions: bundle offers, volume incentives."),
    ("At Risk", "Win-back campaign now: personalized discount, 'we miss you' email."),
    ("Need Attention", "Re-engagement content, remind of new products since last visit."),
    ("Lost", "Low-cost automated win-back only; do not over-invest."),
    ("New/Promising", "Onboarding nurture sequence to convert into Loyal Customers."),
]
r = 12
for seg, action in guide:
    ws3.cell(row=r, column=1, value=seg).font = Font(bold=True)
    ws3.cell(row=r, column=2, value=action)
    ws3.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
    r += 1

# =========================================================
# SHEET 4: Cross-Sell Opportunities (Market Basket)
# =========================================================
ws4 = wb.create_sheet("Cross-Sell Opportunities")
set_print(ws4)
ws4["A1"] = "Market Basket Analysis — Products Frequently Bought Together"
ws4["A1"].font = section_font
ws4["A2"] = "Lift > 1 means the pair is bought together more than random chance would predict. Higher Lift = stronger bundle candidate."
ws4["A2"].font = subtitle_font
last = write_df(ws4, basket.head(15), start_row=4)
autofit(ws4, [30, 30, 16, 12, 14, 14, 10])

ws4["A" + str(last+3)] = "How to use this: create 'Buy the Set' bundles or cross-sell prompts at checkout for the top pairs above."
ws4["A" + str(last+3)].font = subsection_font

# =========================================================
# SHEET 5: Growth Mix (New vs Repeat)
# =========================================================
ws5 = wb.create_sheet("Growth Mix")
set_print(ws5)
ws5["A1"] = "New vs. Repeat Customer Revenue (Monthly)"
ws5["A1"].font = section_font
ws5["A2"] = "Note: Dec 2011 is a partial month (data ends Dec 9) — treat as directional only."
ws5["A2"].font = subtitle_font
nvr_display = new_vs_repeat[['OrderMonth','New_Revenue','Repeat_Revenue','New_Pct','Repeat_Pct']]
write_df(ws5, nvr_display, start_row=4)
autofit(ws5, [14, 16, 16, 12, 12])

achart = BarChart()
achart.type = "col"
achart.grouping = "stacked"
achart.overlap = 100
achart.title = "New vs Repeat Revenue by Month"
data = Reference(ws5, min_col=2, max_col=3, min_row=4, max_row=4+len(nvr_display))
cats = Reference(ws5, min_col=1, min_row=5, max_row=4+len(nvr_display))
achart.add_data(data, titles_from_data=True)
achart.set_categories(cats)
achart.height = 10
achart.width = 22
ws5.add_chart(achart, "G4")

# =========================================================
# SHEET 6: Cohort Retention
# =========================================================
ws6 = wb.create_sheet("Cohort Retention")
set_print(ws6)
ws6["A1"] = "Customer Retention by Monthly Cohort (% still active N months after first purchase)"
ws6["A1"].font = section_font
ws6["A2"] = "Read across a row: of customers who first bought in that month, what % came back in month 1, 2, 3...?"
ws6["A2"].font = subtitle_font

retention_reset = retention.reset_index()
retention_reset.columns = ['CohortMonth'] + [f"M+{c}" for c in retention.columns]
last = write_df(ws6, retention_reset, start_row=4)
autofit(ws6, [12] + [8]*(len(retention.columns)))

# Heatmap color scale on the retention percentages
data_range = f"B5:{get_column_letter(1+len(retention.columns))}{last}"
rule = ColorScaleRule(start_type='min', start_color='F8696B',
                       mid_type='percentile', mid_value=50, mid_color='FFEB84',
                       end_type='max', end_color='63BE7B')
ws6.conditional_formatting.add(data_range, rule)

note_row = last + 3
ws6.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=13)
ws6.cell(row=note_row, column=1, value="Headline KPI: Average Month-1 retention across all cohorts = 20.6%. Industry benchmark for repeat e-commerce is typically 20-30%, so this is roughly in line but has room to improve via the win-back and loyalty actions on the Recommendations tab.").alignment = Alignment(wrap_text=True, vertical="top")
ws6.row_dimensions[note_row].height = 45

# =========================================================
# SHEET 7: Country Expansion Opportunity
# =========================================================
ws7 = wb.create_sheet("Country Expansion Opportunity")
set_print(ws7)
ws7["A1"] = "International Expansion Opportunity Score"
ws7["A1"].font = section_font
ws7["A2"] = "OpportunityScore (index, higher = better) ranks markets with high value-per-customer against a still-small customer base — signals where incremental marketing spend goes furthest, as opposed to just ranking by total revenue. Note: EIRE's high order count from very few customers suggests wholesale/B2B accounts rather than typical retail customers."
ws7["A2"].font = subtitle_font
write_df(ws7, country_opp, start_row=4)
autofit(ws7, [16, 14, 12, 12, 18, 16, 16])

ochart = BarChart()
ochart.title = "Top Expansion Opportunity Markets"
data = Reference(ws7, min_col=7, min_row=4, max_row=4+min(8,len(country_opp)))
cats = Reference(ws7, min_col=1, min_row=5, max_row=4+min(8,len(country_opp)))
ochart.add_data(data, titles_from_data=True)
ochart.set_categories(cats)
ochart.height = 10
ochart.width = 20
ws7.add_chart(ochart, "I4")

# =========================================================
# SHEET 8: Revenue by Country
# =========================================================
ws8 = wb.create_sheet("Revenue by Country")
set_print(ws8)
ws8["A1"] = "Revenue by Country (Full Breakdown)"
ws8["A1"].font = section_font
write_df(ws8, revenue_country, start_row=3)
autofit(ws8, [18, 15, 14, 14, 16])

chart = BarChart()
chart.type = "bar"
chart.title = "Top 10 Countries by Revenue"
chart.y_axis.title = "Country"
chart.x_axis.title = "Revenue (£)"
data = Reference(ws8, min_col=2, min_row=3, max_row=13)
cats = Reference(ws8, min_col=1, min_row=4, max_row=13)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.height = 10
chart.width = 20
ws8.add_chart(chart, "G3")

# =========================================================
# SHEET 9: Monthly Trend
# =========================================================
ws9 = wb.create_sheet("Monthly Trend")
set_print(ws9)
ws9["A1"] = "Monthly Revenue Trend"
ws9["A1"].font = section_font
write_df(ws9, monthly_trend, start_row=3)
autofit(ws9, [16, 14, 14, 14])

lchart = LineChart()
lchart.title = "Monthly Revenue Trend (Dec 2010 - Dec 2011)"
lchart.y_axis.title = "Revenue (£)"
lchart.x_axis.title = "Month"
data = Reference(ws9, min_col=2, min_row=3, max_row=3+len(monthly_trend))
cats = Reference(ws9, min_col=1, min_row=4, max_row=3+len(monthly_trend))
lchart.add_data(data, titles_from_data=True)
lchart.set_categories(cats)
lchart.height = 10
lchart.width = 22
ws9.add_chart(lchart, "F3")

# =========================================================
# SHEET 10: Top Products
# =========================================================
ws10 = wb.create_sheet("Top Products")
set_print(ws10)
ws10["A1"] = "Top 12 Products by Revenue"
ws10["A1"].font = section_font
ws10["A2"] = "Note: excludes non-product codes (POSTAGE, MANUAL, BANK CHARGES, etc.)"
ws10["A2"].font = subtitle_font
write_df(ws10, top_products, start_row=4)
autofit(ws10, [12, 36, 16, 14, 16])

bchart = BarChart()
bchart.title = "Top 10 Products by Revenue"
bchart.y_axis.title = "Revenue (£)"
data = Reference(ws10, min_col=3, min_row=4, max_row=14)
cats = Reference(ws10, min_col=2, min_row=5, max_row=14)
bchart.add_data(data, titles_from_data=True)
bchart.set_categories(cats)
bchart.height = 10
bchart.width = 22
ws10.add_chart(bchart, "G4")

# =========================================================
# SHEET 11: Time Patterns
# =========================================================
ws11 = wb.create_sheet("Time Patterns")
set_print(ws11)
ws11["A1"] = "Day of Week Performance"
ws11["A1"].font = section_font
r1 = write_df(ws11, day_of_week, start_row=3)

ws11["A" + str(r1 + 3)] = "Hourly Sales Pattern"
ws11["A" + str(r1 + 3)].font = section_font
r2 = write_df(ws11, hourly, start_row=r1 + 5)
autofit(ws11, [14, 14, 14])

dchart = PieChart()
dchart.title = "Revenue Share by Day of Week"
data = Reference(ws11, min_col=2, min_row=3, max_row=3+len(day_of_week))
cats = Reference(ws11, min_col=1, min_row=4, max_row=3+len(day_of_week))
dchart.add_data(data, titles_from_data=True)
dchart.set_categories(cats)
dchart.height = 9
dchart.width = 14
ws11.add_chart(dchart, "E3")

hchart = LineChart()
hchart.title = "Revenue by Hour of Day"
hchart.y_axis.title = "Revenue (£)"
hchart.x_axis.title = "Hour"
data = Reference(ws11, min_col=2, min_row=r1+5, max_row=r2)
cats = Reference(ws11, min_col=1, min_row=r1+6, max_row=r2)
hchart.add_data(data, titles_from_data=True)
hchart.set_categories(cats)
hchart.height = 9
hchart.width = 18
ws11.add_chart(hchart, "E22")

# =========================================================
# SHEET 12: Customer Detail (raw RFM table)
# =========================================================
ws12 = wb.create_sheet("Customer Detail")
set_print(ws12)
ws12["A1"] = "Full Customer-Level RFM Table (for pivoting / filtering)"
ws12["A1"].font = section_font
cols_keep = ['CustomerID', 'Country', 'Recency', 'Frequency', 'Monetary', 'R_Score', 'F_Score', 'M_Score', 'RFM_Score', 'Segment']
detail = rfm_detail[cols_keep]
start_r = 3
ncols = len(detail.columns)
for j, colname in enumerate(detail.columns):
    ws12.cell(row=start_r, column=1+j, value=colname)
style_header_row(ws12, start_r, ncols)
for i, row in enumerate(detail.itertuples(index=False), start=1):
    for j, val in enumerate(row):
        ws12.cell(row=start_r+i, column=1+j, value=val)
autofit(ws12, [14, 18, 12, 12, 14, 10, 10, 10, 11, 18])
end_row = start_r + len(detail)
tab = Table(displayName="CustomerRFMTable", ref=f"A{start_r}:J{end_row}")
tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium9", showRowStripes=True)
ws12.add_table(tab)

# =========================================================
# SHEET 13: Data Quality & Methodology
# =========================================================
ws13 = wb.create_sheet("Data Quality Notes")
set_print(ws13)
ws13["A1"] = "Data Cleaning & Methodology"
ws13["A1"].font = section_font
notes = [
    ("Source", "UCI Machine Learning Repository — Online Retail Dataset (Chen, D., 2015), 541,909 raw transaction lines, Dec 2010 - Dec 2011, UK-based online gift retailer."),
    ("Raw rows", str(int(quality['total_rows'][0]))),
    ("Removed - cancelled invoices", f"{int(quality['cancelled_invoices'][0])} rows (InvoiceNo starting with 'C')"),
    ("Removed - negative/zero quantity or price", f"{int(quality['negative_quantity_rows'][0]) + int(quality['zero_or_negative_price_rows'][0])} rows (returns, data errors)"),
    ("Removed - duplicate rows", f"{int(quality['duplicate_rows'][0])} rows"),
    ("Missing CustomerID", f"{int(quality['missing_customerid'][0])} rows kept for product/country analysis, excluded from customer-level RFM"),
    ("Clean rows used for revenue analysis", "524,878"),
    ("RFM method", "Recency/Frequency/Monetary scored 1-5 via quantiles (5 = best). Segments: Champions, Loyal Customers, At Risk, Lost, Need Attention, New/Promising."),
    ("Market basket method", "Co-occurrence analysis on invoice line items; Support/Confidence/Lift computed per product pair; filtered to Lift > 1 and >=30 co-occurrences."),
    ("Cohort retention method", "Customers grouped by first-purchase month (cohort); tracked % of each cohort making a repeat purchase in each subsequent month."),
    ("Caveat", "Dec 2011 is a partial month (data ends Dec 9, 2011) — monthly figures for that month understate true performance."),
    ("Tools used", "SQL (SQLite) for aggregation queries, Python/Pandas for cleaning, RFM, market basket and cohort analysis, Excel (openpyxl) for this dashboard. Same logic is directly portable to Power BI (Power Query for cleaning, DAX for RFM/retention measures)."),
]
r = 3
for label, val in notes:
    ws13.cell(row=r, column=1, value=label).font = Font(bold=True)
    ws13.merge_cells(start_row=r, start_column=2, end_row=r, end_column=8)
    c = ws13.cell(row=r, column=2, value=val)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws13.row_dimensions[r].height = 32
    r += 1
autofit(ws13, [30, 14, 14, 14, 14, 14, 14, 14])

os.makedirs(os.path.join(ROOT, "dashboard"), exist_ok=True)
OUT_PATH = os.path.join(ROOT, "dashboard", "Retail_Sales_Dashboard.xlsx")
wb.save(OUT_PATH)
print("Saved", OUT_PATH, "with", len(wb.sheetnames), "sheets:", wb.sheetnames)
