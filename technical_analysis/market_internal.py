import concurrent.futures
from datetime import datetime, timedelta

import pandas as pd

from technical_analysis import ta
from technical_analysis.column_names import *


def breadth_inner_parallel(df, results, lookback):
    highs = []
    lows = []
    results[df['Ticker'][0]] = {'highs': highs, 'lows': lows}

    t0 = datetime.now()
    for index, row in df.iterrows():
        if ta.highest(df[:index]['Close']) >= lookback:
            highs.append(row.name)
        if ta.lowest(df[:index]['Close']) >= lookback:
            lows.append(row.name)

    #TODO: some progress bar/verbose switch output
    print("{0} done in {1}".format(df['Ticker'][0], (datetime.now()-t0)))



class MarketInternals:


    def __process_results(self, results, lookback, from_date, to_date):
        """
            results example:
            {
                'SPY':
                    {
                    'highs':['2016-12-04',2016-12-05',...]
                    'lows':['2016-11-05',2016-11-06',...]
                    },
                'AAPL':
                    {
                    'highs':['2016-12-04',2016-12-05',...]
                    'lows':['2016-11-05',2016-11-06',...]
                    }
            }
        """
        start = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d")

        index = pd.date_range(start, end) #TODO: make series from actual trading days?
        columns = [day_high_name(lookback), day_high_pct_name(lookback), day_low_name(lookback), day_low_pct_name(lookback)]

        sum = pd.DataFrame(index=index, columns=columns)
        sum = sum.fillna(0.0)

        for key, value in results.items():

            for high_date in value['highs']:
                sum.set_value(high_date, day_high_name(lookback), sum.get_value(high_date, day_high_name(lookback)) + 1)

                perc = float(sum.get_value(high_date, day_high_name(lookback))) / float((len(results)))
                sum.set_value(high_date, day_high_pct_name(lookback), perc * 100.0)

            for low_date in value['lows']:
                sum.set_value(low_date, day_low_name(lookback), sum.get_value(low_date, day_low_name(lookback)) + 1)

                perc = float(sum.get_value(low_date, day_low_name(lookback))) / float(len(results))
                sum.set_value(low_date, day_low_pct_name(lookback), perc * 100.0)

        return sum


    def __breadth_inner(self, df, res, lookback):
        #TODO: try ta_lib if faster for highest/lowest??
        t0 = datetime.now()
        for index, row in df.iterrows():
            if index not in res.index:
                res.set_value(index, day_high_name(lookback), 0)
                res.set_value(index, day_low_name(lookback), 0)

            if ta.highest(df[:index]['Close']) >= lookback:
                res.set_value(index, day_high_name(lookback), res.get_value(index, day_high_name(lookback)) + 1)
            if ta.lowest(df[:index]['Close']) >= lookback:
                res.set_value(index, day_low_name(lookback), res.get_value(index, day_low_name(lookback)) + 1)

        diff = datetime.now() - t0
        #print("Done in: {0} secs".format(diff))

    #TODO: cache call in pickle file? then use in backtests:
    # if (res['2016-02-20'][day_low_pct_name(lookback)] > 20) and longCondition:
    #   go_long()
    def breadth_daily(self, tickers, lookback, from_date, to_date):
        """ Calculate the market breadth for all tickers in provider list of dataframes"""

        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            tmp = {executor.submit(breadth_inner_parallel, df, results, lookback): df for df in tickers}

        res = self.__process_results(results, lookback, from_date, to_date)

        return res

    #TODO: cache call in pickle file?
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

        return res

