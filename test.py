import yfinance as yf
import sqlite3
import pandas as pd

conn = sqlite3.connect('stocks.db')
data = yf.download('AAPL', period='1mo', interval='1d', rounding=True)
data.columns = data.columns.get_level_values(0) # Flatten the multi-level columns
# data.to_sql('AAPL', conn, if_exists='replace', index=True)
data.index = data.index.strftime('%Y-%m-%d')
data_list = []
for row in data.itertuples(name=None):
    data_list.append(("AAPL",) + row)

# print(data_list)

conn.execute('''CREATE TABLE IF NOT EXISTS AAPL (
    Symbol TEXT,
    Date TEXT,
    Close REAL,
    High REAL,
    Low REAL,
    Open REAL,   
    Volume INTEGER,
    PRIMARY KEY (Symbol, Date)
)''')
print(conn.execute('SELECT COUNT(*) FROM AAPL').fetchone()[0])
conn.executemany('INSERT OR REPLACE INTO AAPL VALUES (?, ?, ?, ?, ?, ?, ?)', data_list)
print(conn.execute('SELECT COUNT(*) FROM AAPL').fetchone()[0])
for row in conn.execute('SELECT * FROM AAPL'):
    print(row)



conn.commit()

conn.close()
