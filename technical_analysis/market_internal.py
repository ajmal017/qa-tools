import pandas as pd
from technical_analysis import ta

class MarketInternals:

    DAY_HIGH_50 = "50D_HIGH"

    def breadth_daily(self, tickers, lookback):
        """ Calculate the market breadth for all tickers in provider list of dataframes"""
        res = pd.DataFrame()

        for df in tickers:
            for index, row in df.iterrows():
                if index not in res.index:
                    res.set_value(index, MarketInternals.DAY_HIGH_50, 0)

                if ta.highest(df[:index]['Close']) >= lookback:
                    res.set_value(index, MarketInternals.DAY_HIGH_50, res.get_value(index,MarketInternals.DAY_HIGH_50)+1)
        return res