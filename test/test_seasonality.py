import unittest

from dataprovider.dataprovider import CachedDataProvider
from technical_analysis import seasonality


class TestSeasonality(unittest.TestCase):

    local_provider = CachedDataProvider(cache_name='test_seasonality', expire_days=0)

    def test_average_return(self):
        spy_daily = self.local_provider.get_data(ticker="spy", from_date='2010-01-01', to_date='2016-01-01')
        df = seasonality.seasonality(spy_daily)

        #TODO: df should contain columns ["day as time obj", "avg return between 0 and 1"]
        #Test SPY: Nov to May
        assert seasonality.average_return('spy','2015-11-05','1M') > 0.0 # Avg. return to beginning of Dec.
        assert seasonality.average_return('spy', '2015-11-05', '2M') > 0.0 # Avg return to beginning of Jan.
        assert seasonality.average_return('spy', '2015-11-05', '3M') > 0.0  # Avg return to beginning of Feb.
        assert seasonality.average_return('spy', '2015-11-05', '4M') > 0.0  # Avg return to beginning of Mar.
        assert seasonality.average_return('spy', '2015-11-05', '5M') > 0.0  # Avg return to beginning of May

        #assert seasonality.py.average_return('spy', '2016-11-05', '5M') > 0.0  # Throw error, lookahead bias?


    def test_win_rate(self):
        spy_daily = self.local_provider.get_data(ticker="spy", from_date='2010-01-01', to_date='2016-01-01')
        df = seasonality.seasonality(spy_daily)

if __name__ == '__main__':
    unittest.main()