from multiprocessing import Process
from multiprocessing import Pool

import datetime

import pandas as pd

from technical_analysis import ta
from technical_analysis.column_names import *

class MarketInternals:


    def __breadth_inner(self, df, res, lookback):
        t0 = datetime.datetime.now()
        for index, row in df.iterrows():
            if index not in res.index:
                res.set_value(index, day_high_name(lookback), 0)
                res.set_value(index, day_low_name(lookback), 0)

            if ta.highest(df[:index]['Close']) >= lookback:
                res.set_value(index, day_high_name(lookback), res.get_value(index, day_high_name(lookback)) + 1)
            if ta.lowest(df[:index]['Close']) >= lookback:
                res.set_value(index, day_low_name(lookback), res.get_value(index, day_low_name(lookback)) + 1)

        diff = datetime.datetime.now() - t0
        #print("Done in: {0} secs".format(diff))

    def breadth_daily(self, tickers, lookback):
        """ Calculate the market breadth for all tickers in provider list of dataframes"""
        res = pd.DataFrame()

        for df in tickers:
            self.__breadth_inner(df, res, lookback)

        return res

    def breadth_dma(self, tickers, lookback):
        """ Calculate the number of tickers below and above X lookback MA"""
        res = pd.DataFrame()

        for df in tickers:
            if not ma_name(lookback) in df.columns:
                raise Exception("Missing {n}DMA calculations".format(n=lookback))

            for index, row in df.iterrows():
                if index not in res.index:
                    res.set_value(index, above_dma_name(lookback), 0)
                    res.set_value(index, below_dma_name(lookback), 0)

                if row['Close'] < row[ma_name(lookback)]:
                    res.set_value(index, below_dma_name(lookback), res.get_value(index, below_dma_name(lookback)) + 1)
                else:
                    res.set_value(index, above_dma_name(lookback), res.get_value(index, above_dma_name(lookback)) + 1)

            # TODO: print time taken for this df

        return res

