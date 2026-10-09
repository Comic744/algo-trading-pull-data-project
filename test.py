import yfinance as yf
import sqlite3

conn = sqlite3.connect('stocks.db')
data = yf.download('AAPL', period='1d', interval='1m')

data.to_sql('AAPL', conn, if_exists='replace', index=True)