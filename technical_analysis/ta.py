import numpy as np
import pandas as pd


def ma_column_name(lookback):
    return "{n}DMA".format(n=lookback)

def ma_slope_column_name(lookback):
    return "{n}DMA_slope".format(n=lookback)

def add_ma(dataframe, days):
    dataframe[ma_column_name(days)] = np.round(dataframe["Close"].rolling(window=days, center=False).mean(), 2)
    return dataframe

def add_ma_slope(dataframe, lookback):
    mean = np.round(dataframe["Close"].rolling(window=lookback, center=False).mean(), 2)
    dataframe[ma_slope_column_name(lookback)] = (mean-mean.shift()).apply(lambda x: 1 if x > 0 else -1)
    return dataframe

# Deprecated??
def dates_below_ma(ma, dataframe):
    dates = []

    for index, row in dataframe.iterrows():
        if row['Close'] < row[ma_column_name(ma)]:
            dates.append(row.name.date().__str__())

    return dates

def highest(df):
    """ Get the highest order of the last entry """

    last = df.ix[len(df) - 1]
    for i in range(0,len(df)-1):
        cmp = df.ix[len(df)-2-i]
        if (cmp > last):
            return i
    return len(df)-1


def lowest(df):
    """ Get the lowest order of the last entry """

    last = df.ix[len(df) - 1]
    for i in range(0,len(df)-1):
        cmp = df.ix[len(df)-2-i]
        if (cmp < last):
            return i
    return len(df)-1