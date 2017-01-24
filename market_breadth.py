#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import pandas as pd

from dataprovider.web_dataprovider import WebDataprovider
import talib

# Ex:
# $ python breadth.py --function 200DMA --from 2010-01-01 --to 2017-01-22


# Historical values:
# Number of stocks below 200DMA
# Number of stocks making new 50D high/low
# Number of stocks making new 20D high/low

def get_tickers(file):
    with open(file) as f:
        return [ticker.rstrip() for ticker in f.readlines()]

def breadth_new_highs(from_date, to_date):
    provider = WebDataprovider('breadth',expire_days=0)

    tickers = get_tickers('sp500.txt')
    #tickers = ['MMM', 'ABT', 'ABBV', 'ACN', 'ATVI', 'AYI']
    dataframes = []

    for ticker in tickers:
        try:
            dataframes.append(provider.get_data(ticker,from_date,to_date))
        except Exception as e:
            print("Skipping {ticker}: {error}".format(ticker=ticker, error=e))

    mmm = dataframes[0]
    output = talib.MOM(mmm['Close'], timeperiod=5)


if __name__ == '__main__':
    breadth_new_highs('2010-01-01','2017-01-01')
