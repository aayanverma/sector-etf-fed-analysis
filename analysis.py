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

