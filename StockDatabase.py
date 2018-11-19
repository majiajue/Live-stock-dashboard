
import requests
import sqlite3
import numpy as np

symbol = "MSFT"
API_KEY = "2T4QNO4SC2HDHUH6"

def msft_hundredDays():
    StockDict = {"date": [], "open": [], "high": [], "low": [], "close": [], "volume": []}
    func = "TIME_SERIES_DAILY"
    parameters = {"function": func, "symbol": symbol, "apikey": API_KEY} 
    r = requests.get("https://www.alphavantage.co/query", params=parameters)
    if r.status_code != 200:
        return (None, 'error')
    result = r.json()
    TimeSeriesDaily = result['Time Series (Daily)']
    for date in TimeSeriesDaily: 
        #dataForSingleDate = dataForAllDays[date]
        StockDict["date"].append(date)
        StockDict["open"].append(float(TimeSeriesDaily[date]['1. open']))
        StockDict["high"].append(float(TimeSeriesDaily[date]['2. high']))
        StockDict["low"].append(float(TimeSeriesDaily[date]['3. low']))
        StockDict["close"].append(float(TimeSeriesDaily[date]['4. close']))
        StockDict["volume"].append(float(TimeSeriesDaily[date]['5. volume']))
    
    stock_tuples = list(zip(StockDict['date'], StockDict['open'], StockDict['high'], 
                            StockDict['low'], StockDict['close'], StockDict['volume']))

    #Writing to the SQLite database
    conn = sqlite3.connect('Stocks.db') 
    c = conn.cursor()  
    c.execute('DROP TABLE IF EXISTS MSFT') 
    c.execute('CREATE TABLE MSFT(date text, open REAL, high REAL, low REAL, close REAL, volume REAL)') 
    c.executemany('INSERT INTO MSFT VALUES(?,?,?,?,?,?)', stock_tuples)
    conn.commit()
    conn.close()

    #Reading from the SQLite database
    conn = sqlite3.connect('Stocks.db') 
    c = conn.cursor()
    c.execute('SELECT open, high, low, close FROM MSFT')
    table_content = c.fetchall()
    conn.commit()
    conn.close()

    table_content = np.array(table_content, dtype=np.float32)
    stock_avg = list(np.mean(table_content, axis=0))
    
    return (stock_avg, 'success')

def msft_minute():
    parameters = {"function": "TIME_SERIES_INTRADAY", "symbol": symbol, 
                   "interval": "1min","apikey": API_KEY} 
    r = requests.get("https://www.alphavantage.co/query", params=parameters)
    if r.status_code != 200:
        return (0, 0, 'error')
    result = r.json()
    TimeSeriesDict = result["Time Series (1min)"]
    dates =  sorted([k for k, v in TimeSeriesDict.items()])
    results = [float(TimeSeriesDict[date]['1. open']) for date in dates]
    dates_time_only = [k.split(' ')[-1] for k in dates]
    return (results, dates_time_only)



