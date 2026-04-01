import pandas as pd
import yfinance as yf
from fredapi import Fred
from dotenv import load_dotenv
import os

load_dotenv()
fred = Fred(api_key = os.getenv("FRED_API_KEY"))
print("All imports successful")
print(f"FRED API key loaded: {bool(os.getenv('FRED_API_KEY'))}")

'''
Pull FED funds rate from FRED
'''

fed_funds = fred.get_series('FEDFUNDS', observation_start='2000-01-01', observation_end='2024-12-31')


#convert to dataframe using pandas and clean

fed_funds = fed_funds.to_frame(name = 'fed_funds_rate')
fed_funds.index.name = 'date'
fed_funds.index = pd.to_datetime(fed_funds.index)

print(fed_funds.head(10))
print(f"\nShape: {fed_funds.shape}")
print(f"Date range: {fed_funds.index.min()} to {fed_funds.index.max()}")


# Save to raw data folder
fed_funds.to_csv('data/raw/fed_funds_raw.csv')
print("\nSaved to data/raw/fed_funds_raw.csv")

'''
Pull ETF prices from Yfinance
'''

tickers = ['XLF', 'XLK', 'XLE', 'XLV', 'XLI', 'XLP', 'XLY', 'XLU']
etf_data = yf.download(tickers, start='2000-01-01', end='2024-12-31', interval='1mo', auto_adjust=True)
# Keep only adjusted close prices
etf_prices = etf_data['Close']

print(etf_prices.head(10))
print(f"\nShape: {etf_prices.shape}")
print(f"Date range: {etf_prices.index.min()} to {etf_prices.index.max()}")

# Save to raw data folder
etf_prices.to_csv('data/raw/etf_prices_raw.csv')
print("\nSaved to data/raw/etf_prices_raw.csv")

#Calculate % change over month to month
etf_returns = etf_prices.pct_change() * 100

#drop first row NaN
etf_returns = etf_returns.dropna()

print(etf_returns.head(10))
print(f"\nShape: {etf_returns.shape}")

# Save to raw data folder
etf_returns.to_csv('data/raw/etf_returns_raw.csv')
print("\nSaved to data/raw/etf_returns_raw.csv")

'''
Label Rate Cycles 
'''

# Calculate month over month change in fed funds rate
fed_funds['rate_change'] = fed_funds['fed_funds_rate'].diff()

# Label direction: +1 = rising, -1 = falling, 0 = flat
fed_funds['direction'] = fed_funds['rate_change'].apply(
    lambda x: 1 if x > 0 else (-1 if x < 0 else 0)
)

# Rolling sum of last 2 months direction to enforce 2+ consecutive months rule
fed_funds['rolling_direction'] = fed_funds['direction'].rolling(2).sum()

# Assign cycle type
def assign_cycle(row):
    if row['rolling_direction'] >= 2:
        return 'hiking'
    elif row['rolling_direction'] <= -2:
        return 'cutting'
    else:
        return 'neutral'

fed_funds['cycle_type'] = fed_funds.apply(assign_cycle, axis=1)

print(fed_funds.head(20))
print("\nCycle distribution:")
print(fed_funds['cycle_type'].value_counts())

# Save
fed_funds.to_csv('data/clean/fed_rate_cycles.csv')
print("\nSaved to data/clean/fed_rate_cycles.csv")

'''
Now merge ETF returns with FED cycle labels for one clean dataset
'''

# Keep only date and cycle_type from fed_funds
cycle_labels = fed_funds[['cycle_type']]

# Merge on date index
etf_returns.index.name = 'date'
merged = etf_returns.merge(cycle_labels, left_index=True, right_index=True, how='left')

print(merged.head(10))
print(f"\nShape: {merged.shape}")
print(f"\nNull values:\n{merged.isnull().sum()}")

# Save to clean folder
merged.to_csv('data/clean/etf_returns_with_cycles.csv')
print("\nSaved to data/clean/etf_returns_with_cycles.csv")

'''
Part 2: Load data into postgreSQL
'''

import psycopg2
from psycopg2.extras import execute_values

# Connect to database
conn = psycopg2.connect(
    dbname="sector_etf_analysis",
    user="aayanverma",
    host="localhost"
)
cur = conn.cursor()

# Load fed_rate_cycles
fed_clean = pd.read_csv('data/clean/fed_rate_cycles.csv', index_col='date', parse_dates=True)
fed_clean = fed_clean.reset_index()

fed_rows = [
    (
        row['date'].date(),
        row['fed_funds_rate'],
        row['rate_change'] if pd.notna(row['rate_change']) else None,
        int(row['direction']) if pd.notna(row['direction']) else None,
        row['rolling_direction'] if pd.notna(row['rolling_direction']) else None,
        row['cycle_type']
    )
    for _, row in fed_clean.iterrows()
]

execute_values(cur, """
    INSERT INTO fed_rate_cycles (date, fed_funds_rate, rate_change, direction, rolling_direction, cycle_type)
    VALUES %s
""", fed_rows)

print(f"Inserted {len(fed_rows)} rows into fed_rate_cycles")

# Load etf_returns
etf_clean = pd.read_csv('data/clean/etf_returns_with_cycles.csv', index_col='date', parse_dates=True)
etf_clean = etf_clean.reset_index()

tickers = ['XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLU', 'XLV', 'XLY']
etf_rows = []
for _, row in etf_clean.iterrows():
    for ticker in tickers:
        etf_rows.append((
            row['date'].date(),
            ticker,
            row[ticker],
            row['cycle_type']
        ))

execute_values(cur, """
    INSERT INTO etf_returns (date, ticker, monthly_return, cycle_type)
    VALUES %s
""", etf_rows)

print(f"Inserted {len(etf_rows)} rows into etf_returns")

conn.commit()
cur.close()
conn.close()
print("\nDatabase load complete")