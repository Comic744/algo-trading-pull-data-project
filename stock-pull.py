import yfinance as yf
import sqlite3
import sys
import os


sqlite3_file = os.environ.get("DB_PATH","stocks.db")

symbols = ["AAPL", "MSFT"]


def get_last_date(symbol, conn):
     return conn.execute('SELECT MAX(Date) FROM STOCKS WHERE Symbol = ?', (symbol,)).fetchone()[0]

def fetch(symbol, start_date, period=None):
     return yf.download(symbol, period=period, interval='1d', rounding=True, start=start_date)

def to_list_of_tuples(data, symbol):
     data_list = []
     for row in data.itertuples(name=None):
           data_list.append((symbol,) + row)
     return data_list

def store():
     return 1

if __name__ == "__main__":

     conn = sqlite3.connect(sqlite3_file)
     conn.execute('''CREATE TABLE IF NOT EXISTS STOCKS (
     Symbol TEXT,
     Date TEXT,
     Close REAL,
     High REAL,
     Low REAL,
     Open REAL,   
     Volume INTEGER,
     PRIMARY KEY (Symbol, Date)
     )''')
     
     print(conn.execute('SELECT COUNT(*) FROM STOCKS').fetchone()[0])

     failed = []

     for symbol in symbols:
          start_date = get_last_date(symbol, conn)
          print(start_date, symbol)

          if start_date is None:
               data = fetch(symbol, None, '1mo')
          else:
               data = fetch(symbol, start_date)
          if data.empty:
               print(f"No new data, nothing written for the symbol {symbol}")
               failed.append(symbol)
               continue
          data.columns = data.columns.get_level_values(0) # Flatten the multi-level columns
          data.index = data.index.strftime('%Y-%m-%d')

          formated_data = to_list_of_tuples(data, symbol)
          conn.executemany('INSERT OR REPLACE INTO STOCKS (Symbol, Date, Close, High, Low, Open, Volume) VALUES (?, ?, ?, ?, ?, ?, ?)', formated_data)


     print(conn.execute('SELECT COUNT(*) FROM STOCKS').fetchone()[0])

     conn.commit()
     conn.close()

     if failed:                                                       
          print(f"Failed symbols: {', '.join(failed)}")               
          sys.exit(1)    # 1 = failure 
