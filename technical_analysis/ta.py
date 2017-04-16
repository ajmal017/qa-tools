#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import numpy as np
import talib

import technical_analysis.column_names as ta_columns


def add_ma(dataframe, lookback):
    dataframe[ta_columns.ma_name(lookback)] = np.round(dataframe["Close"].rolling(window=lookback, center=False).mean(), 2)
    return dataframe


def add_ma_slope(dataframe, lookback):
    mean = np.round(dataframe["Close"].rolling(window=lookback, center=False).mean(), 2)
    dataframe[ta_columns.ma_slope_name(lookback)] = (mean - mean.shift()).apply(lambda x: 1 if x > 0 else -1)
    return dataframe


def add_rocp(df, lookback):
    df.fillna(inplace=True, method='ffill')
    df[ta_columns.rocp_name(lookback)] = talib.ROCP(df['Close'].values, timeperiod=lookback)
    return df


def add_atr(dataframe, lookback):
    dataframe.fillna(inplace=True, method='ffill')
    atr = talib.ATR(dataframe['High'].values, dataframe['Low'].values, dataframe['Close'].values, timeperiod=lookback)
    dataframe[ta_columns.atr_name(lookback)] = atr
    # dataframe['tmp'] = np.round(dataframe[atr_name(lookback)].rolling(window=5, center=False).mean(), 2)
    return dataframe


def highest(df):
    """ Get the highest order of the last entry """
    last = df.ix[len(df) - 1]
    for i in range(0, len(df) - 1):
        cmp = df.ix[len(df) - 2 - i]
        if cmp > last:
            return i
    return len(df) - 1


def lowest(df):
    """ Get the lowest order of the last entry """
    last = df.ix[len(df) - 1]
    for i in range(0, len(df) - 1):
        cmp = df.ix[len(df) - 2 - i]
        if cmp < last:
            return i
    return len(df) - 1
