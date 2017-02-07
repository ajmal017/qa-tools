import concurrent.futures
from datetime import datetime, timedelta
import logging as logger
import pandas as pd

from technical_analysis import ta
import technical_analysis.column_names as ta_names

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')

#Deprecated?
# def breadth_dma_inner_parallel(df, results, lookback):
#     ticker = df['Ticker'][0]
#     above = []
#     below = []
#     results[ticker] = {'above': above, 'below': below}
#
#     if not ta_names.ma_name(lookback) in df.columns:
#         raise Exception("Missing {0}DMA calculations for {1}".format(lookback,ticker))
#
#     for index, row in df.iterrows():
#         if row['Close'] < row[ta_names.ma_name(lookback)]:
#             below.append(row.name)
#         else:
#             above.append(row.name)


class MarketInternals:

    # #Deprecated
    # @staticmethod
    # def breadth_inner_parallel(df, results, lookback):
    #     ticker = df['Ticker'][0]
    #     highs = []
    #     lows = []
    #     results[ticker] = {'highs': highs, 'lows': lows}
    #
    #     t0 = datetime.now()
    #     for index, row in df.iterrows():
    #         if ta.highest(df[:index]['Close']) >= lookback:
    #             highs.append(row.name)
    #         if ta.lowest(df[:index]['Close']) >= lookback:
    #             lows.append(row.name)
    #         print(ticker, "C")
    #     # TODO: some progress bar/verbose switch output
    #
    #     print("{0} done in {1}".format(ticker, (datetime.now() - t0)))
    #
    #
    #
    #
    #
    # def __breadth_inner(self, df, res, lookback):
    #     t0 = datetime.now()
    #     for index, row in df.iterrows():
    #         if index not in res.index:
    #             res.set_value(index, ta_names.day_high_name(lookback), 0)
    #             res.set_value(index, ta_names.day_low_name(lookback), 0)
    #
    #         if ta.highest(df[:index]['Close']) >= lookback:
    #             res.set_value(index, ta_names.day_high_name(lookback), res.get_value(index, ta_names.day_high_name(lookback)) + 1)
    #         if ta.lowest(df[:index]['Close']) >= lookback:
    #             res.set_value(index, ta_names.day_low_name(lookback), res.get_value(index, ta_names.day_low_name(lookback)) + 1)
    #
    #     diff = datetime.now() - t0
    #     #print("Done in: {0} secs".format(diff))
    #
    # #TODO: cache call in pickle file? then use in backtests:
    # # if (res['2016-02-20'][day_low_pct_name(lookback)] > 20) and longCondition:
    # #   go_long()
    # def breadth_daily(self, tickers, lookback, from_date, to_date):
    #     """ Calculate the market breadth for all tickers in provider list of dataframes"""
    #
    #     results = {}
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    #         tmp = {executor.submit(MarketInternals.breadth_inner_parallel, df, results, lookback): df for df in tickers}
    #
    #     res = self.__process_results(results, lookback, from_date, to_date)
    #
    #     return res
    #
    #
    #
    # #TODO: cache call in pickle file?
    # def breadth_dma(self, tickers, lookback, from_date, to_date):
    #     """ Calculate the number of tickers below and above X lookback MA"""
    #     res = pd.DataFrame()
    #
    #     for df in tickers:
    #         if not ta_names.ma_name(lookback) in df.columns:
    #             raise Exception("Missing {n}DMA calculations".format(n=lookback))
    #
    #         for index, row in df.iterrows():
    #             if index not in res.index:
    #                 res.set_value(index, ta_names.above_dma_name(lookback), 0)
    #                 res.set_value(index, ta_names.below_dma_name(lookback), 0)
    #
    #             if row['Close'] < row[ta_names.ma_name(lookback)]:
    #                 res.set_value(index, ta_names.below_dma_name(lookback), res.get_value(index, ta_names.below_dma_name(lookback)) + 1)
    #             else:
    #                 res.set_value(index, ta_names.above_dma_name(lookback), res.get_value(index, ta_names.above_dma_name(lookback)) + 1)
    #
    #     return res

    #### Deprecate above here ####


    def breadth(self, df_list, lookback, from_date, to_date, columns, fun):
        """ Calculate breadth using function for all tickers in df_list"""
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fun, df, lookback): df for df in df_list}

            for future in concurrent.futures.as_completed(futures):
                df = futures[future]
                try:
                    ticker = df['Ticker'][0]
                    res = future.result()
                    results[ticker] = res
                except Exception as exc:
                    print("Error: {0}. Data: {1}".format(exc,futures[future]))

        logger.info("Processing results")
        t0 = datetime.now()
        res = self.__process_results(results, lookback, from_date, to_date, columns)
        logger.info("Done in {0}".format(datetime.now()-t0))
        return res


    def __process_results(self, results, lookback, from_date, to_date, columns):
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

        index = pd.date_range(start, end) # make series from actual trading days?
        #columns = [day_high_name(lookback), day_high_pct_name(lookback), day_low_name(lookback), day_low_pct_name(lookback)]
        cols = [columns['high_or_above'],columns['high_or_above_pct'],columns['low_or_below'],columns['low_or_below_pct']]
        sum = pd.DataFrame(index=index, columns=cols)
        sum = sum.fillna(0.0)

        for key, value in results.items():
            for high_date in value['high_or_above']:
                sum.set_value(high_date, columns['high_or_above'], sum.get_value(high_date, columns['high_or_above']) + 1)

                perc = float(sum.get_value(high_date, columns['high_or_above'])) / float((len(results)))
                sum.set_value(high_date, columns['high_or_above_pct'], perc * 100.0)

            for low_date in value['low_or_below']:
                sum.set_value(low_date, columns['low_or_below'], sum.get_value(low_date, columns['low_or_below']) + 1)

                perc = float(sum.get_value(low_date, columns['low_or_below'])) / float(len(results))
                sum.set_value(low_date, columns['low_or_below_pct'], perc * 100.0)

        return sum

    @staticmethod
    def hilo(df, lookback):
        ticker = df['Ticker'][0]
        highs = []
        lows = []
        results = {'high_or_above': highs, 'low_or_below': lows}

        t0 = datetime.now()
        for index, row in df.iterrows():
            if ta.highest(df[:index]['Close']) >= lookback:
                highs.append(row.name)
            if ta.lowest(df[:index]['Close']) >= lookback:
                lows.append(row.name)
        # TODO: some progress bar/verbose switch output

        print("{0} done in {1}".format(ticker, (datetime.now() - t0)))
        return results

    @staticmethod
    def dma(df, lookback):
        #ticker = df['Ticker'][0]

        above = []
        below = []
        results = {'high_or_above': above, 'low_or_below': below}

        t0 = datetime.now()
        for index, row in df.iterrows():
            if row['Close'] < row[ta_names.ma_name(lookback)]:
                below.append(row.name)
            else:
                above.append(row.name)
        #print("{0} done in {1}".format(ticker, (datetime.now() - t0)))
        return results

