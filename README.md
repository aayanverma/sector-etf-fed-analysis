# Sector ETF & Federal Reserve Rate Analysis (2000–2024)

## Project Overview

An end-to-end data analysis project examining how Federal Reserve interest rate cycles (hiking, cutting, neutral) affect returns across 8 major U.S. market sectors over 25 years.

**Tools Used:** Python, PostgreSQL, Excel, Tableau Public, GitHub

---

## Key Findings

- **During cutting cycles:** XLE (Energy) was the top performer at +1.35% avg monthly return. XLF (Financials) was the worst at -0.75% — challenging the common assumption that financials lead in any rate environment
- **During hiking cycles:** XLU (Utilities) surprisingly led all sectors at +1.10% avg monthly return, followed by XLF at +0.83%
- **During neutral cycles:** XLK (Technology) led at +1.22% avg monthly return
- **Win rate leader:** XLU had the highest percentage of positive return months at 62.5% across all cycles
- **Hypothesis result:** The original hypothesis (Financials and Energy outperform during hiking; Technology and Utilities outperform during cutting) was only partially confirmed — Energy dominated cutting cycles but Utilities led hiking cycles, not Financials

---

## Tableau Dashboard

[View Interactive Dashboard](https://public.tableau.com/app/profile/aayan.verma/viz/SectorETFvsFED/SectorETFPerformancevsFederalReserveRateCycles2000-2024?publish=yes)

---

## Workflow

### Phase 1 — Python (Data Ingestion & Cleaning)

- Pulled 300 months of Federal funds rate data from FRED API
- Pulled adjusted close price data for 8 sector ETFs via yfinance
- Calculated monthly returns using pct_change()
- Labeled each month as hiking, cutting, or neutral (2+ consecutive months rule)
- Output: clean CSVs in `data/clean/`

### Phase 2 — PostgreSQL (Data Modeling & Analysis)

- Created `sector_etf_analysis` database with two tables: `fed_rate_cycles` and `etf_returns`
- Loaded 300 rows into `fed_rate_cycles` and 2,392 rows into `etf_returns`
- Wrote SQL queries for average returns by cycle, sector rankings, best/worst performers, win rates
- Exported results to CSVs for Excel and Tableau

### Phase 3 — Excel (Interim Analysis)

- Built pivot table: tickers as rows, cycle types as columns, average return as values
- Added green-white-red conditional formatting heatmap
- Built XLOOKUP formula to dynamically return top performing sector by cycle type
- Built SUMIF to count positive return months per sector
- Created clustered bar chart of average returns by sector and cycle type

### Phase 4 — Tableau (Interactive Dashboard)

- Connected to long-format CSV (2,392 rows)
- Built sector performance heatmap with diverging red-green color scale
- Built ranked bar chart grouped by cycle type
- Built ETF return timeline (2000–2024)
- Published interactive dashboard to Tableau Public

---

## How to Reproduce

1. Clone the repo
2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Get a free FRED API key at [fred.stlouisfed.org](https://fred.stlouisfed.org)
4. Create a `.env` file with `FRED_API_KEY=your_key_here`
5. Run `python analysis.py`
6. Set up PostgreSQL and run `psql -d sector_etf_analysis -f sql/setup.sql`

---

## Repository Structure

```
sector-etf-fed-analysis/
├── data/
│   ├── raw/          # Original API pulls
│   └── clean/        # Processed CSVs
├── sql/
│   ├── setup.sql     # Database schema
│   └── queries.sql   # Analysis queries
├── excel/
│   └── sector_analysis.xlsx
├── analysis.py       # Main Python script
├── requirements.txt
└── README.md
```

---

## Data Sources

- **Federal Reserve (FRED API):** Federal funds rate, monthly 2000–2024
- **Yahoo Finance (yfinance):** Adjusted close prices for XLF, XLK, XLE, XLV, XLI, XLP, XLY, XLU
