import unittest

from dataprovider.dataprovider import CachedDataProvider
from technical_analysis import seasonality


class TestSeasonality(unittest.TestCase):
    local_provider = CachedDataProvider(cache_name='test_seasonality', expire_days=0, trading_days=True)

    def test_average_return(self):
        spy_daily = self.local_provider.get_data(ticker="spy", from_date='2010-01-01', to_date='2016-01-01')

        df = seasonality.trading_day_reindex(seasonality.seasonality_returns(spy_daily), "SPY", "SPY")

        # Bullish Nov to May
        assert seasonality.average_return(df, spy_daily.loc['20151103']['Day'], 22) > 0.0  # Nov-Dec
        assert seasonality.average_return(df, spy_daily.loc['20151103']['Day'], 22 * 2) > 0.0  # Nov-Jan
        assert seasonality.average_return(df, spy_daily.loc['20151103']['Day'], 22 * 3) > 0.0  # Nov-Feb
        assert seasonality.average_return(df, spy_daily.loc['20151103']['Day'], 22 * 4) > 0.0  # Nov-Mar
        assert seasonality.average_return(df, spy_daily.loc['20151103']['Day'], 22 * 5) > 0.0  # Nov-May

        # Bearish May to Nov
        assert seasonality.average_return(df, spy_daily.loc['20150501']['Day'], 22) < 0.0  # May-June
        assert seasonality.average_return(df, spy_daily.loc['20150501']['Day'], 22 * 2) < 0.0  # May-Jul
        assert seasonality.average_return(df, spy_daily.loc['20150501']['Day'], 22 * 5) < 0.0  # May-Oct

        # assert seasonality.py.average_return('spy', '2016-11-05', '5M') > 0.0  # Throw error, lookahead bias?


if __name__ == '__main__':
    unittest.main()
