import pandas as pd

from technical_analysis import ta
from technical_analysis.column_names import *

class MarketInternals:

    def breadth_daily(self, tickers, lookback):
        """ Calculate the market breadth for all tickers in provider list of dataframes"""
        res = pd.DataFrame()

        for df in tickers:
            for index, row in df.iterrows():
                if index not in res.index:
                    res.set_value(index, day_high_name(lookback), 0)
                    res.set_value(index, day_low_name(lookback), 0)

                if ta.highest(df[:index]['Close']) >= lookback:
                    res.set_value(index, day_high_name(lookback), res.get_value(index,day_high_name(lookback))+1)
                if ta.lowest(df[:index]['Close']) >= lookback:
                    res.set_value(index, day_low_name(lookback), res.get_value(index, day_low_name(lookback))+1)
        return res