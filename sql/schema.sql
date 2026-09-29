-- Schema for the cleaned "sales" table loaded into SQLite (retail.db)
-- Created by scripts/01_clean_and_load.py

CREATE TABLE IF NOT EXISTS sales (
    InvoiceNo      TEXT,       -- Invoice number (6-digit); starts with 'C' if cancelled (already filtered out here)
    StockCode      TEXT,       -- Product code
    Description    TEXT,       -- Product name
    Quantity       INTEGER,    -- Units sold (only positive values kept)
    InvoiceDate    TEXT,       -- ISO-8601 timestamp
    UnitPrice      REAL,       -- Price per unit, GBP (only positive values kept)
    CustomerID     INTEGER,    -- Customer identifier (nullable — guest checkouts)
    Country        TEXT,       -- Customer's country
    is_cancelled   INTEGER,    -- 0/1 flag (all rows in `sales` are 0; cancellations live in all_transactions)
    Revenue        REAL,       -- Quantity * UnitPrice
    InvoiceMonth   TEXT,       -- YYYY-MM
    InvoiceYear    INTEGER,
    DayOfWeek      TEXT,
    Hour           INTEGER
);

CREATE INDEX IF NOT EXISTS idx_customer ON sales(CustomerID);
CREATE INDEX IF NOT EXISTS idx_date     ON sales(InvoiceDate);
CREATE INDEX IF NOT EXISTS idx_country  ON sales(Country);

-- `all_transactions` holds the full cleaned dataset including cancellations
-- (same columns, minus the derived Revenue/Month/DayOfWeek/Hour fields) for audit purposes.
