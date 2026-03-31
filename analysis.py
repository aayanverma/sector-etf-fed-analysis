import pandas as pd
import yfinance as yf
from fredapi import Fred
from dotenv import load_dotenv
import os

load_dotenv()
fred = Fred(api_key = os.getenv("FRED_API_KEY"))
print("All imports successful")
print(f"FRED API key loaded: {bool(os.getenv('FRED_API_KEY'))}")