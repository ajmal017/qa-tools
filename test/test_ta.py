import unittest

from dataprovider.dataprovider import CachedDataProvider
from technical_analysis import ta
from technical_analysis.column_names import *


class TestTechnicalAnalysis(unittest.TestCase):

    local_provider = CachedDataProvider(cache_name='test_ta', expire_days=0)

    def test_ma_slope(self):
        spy_daily = self.local_provider.get_data(ticker="spy", from_date='2010-01-01', to_date='2017-01-01')

        assert "2010-01-04 00:00:00" == spy_daily.iloc[0].name.__str__()
        assert "2010-01-06 00:00:00" == spy_daily.iloc[2].name.__str__()

        df = ta.add_ma_slope(spy_daily, 50)

        assert -1 == df.loc['20160115'][ma_slope_name(50)]

    def test_highest(self):
        spy_daily = self.local_provider.get_data(ticker="spy", from_date='2010-01-01', to_date='2017-01-01')
        assert ta.highest(spy_daily.loc[:'20161205']['Close']) < 50

        #for index, row in spy_daily.iterrows():
        #    print(index,":", row['Close'], " ", ta.highest(spy_daily.loc[:index]['Close']))

    def test_lowest(self):
        spy_daily = self.local_provider.get_data(ticker="spy", from_date='2010-01-01', to_date='2017-01-01')
        assert ta.lowest(spy_daily.loc[:'20161222']['Close']) == 3

        #for index, row in spy_daily.iterrows():
        #    print(index,":", row['Close'], " ", ta.lowest(spy_daily.loc[:index]['Close']))

    def test_seasonality(self):
        spy_daily = self.local_provider.get_data(ticker="spy", from_date='2010-01-01', to_date='2016-01-01')
        seasonality = ta.seasonality([spy_daily])

        #SPY: Nov to May
        assert seasonality.average_return('spy','2015-11-05','1M') > 0.0 # Avg. return to beginning of Dec.
        assert seasonality.average_return('spy', '2015-11-05', '2M') > 0.0 # Avg return to beginning of Jan.
        assert seasonality.average_return('spy', '2015-11-05', '3M') > 0.0  # Avg return to beginning of Feb.
        assert seasonality.average_return('spy', '2015-11-05', '4M') > 0.0  # Avg return to beginning of Mar.
        assert seasonality.average_return('spy', '2015-11-05', '5M') > 0.0  # Avg return to beginning of May

        #assert seasonality.py.average_return('spy', '2016-11-05', '5M') > 0.0  # Throw error, lookahead bias?


if __name__ == '__main__':
    unittest.main()