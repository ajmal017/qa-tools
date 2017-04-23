#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset:4 -*-

import unittest

from qa_dataprovider.web_dataprovider import CachedDataProvider
from technical_analysis.seasonality import Seasonality


class TestSeasonality(unittest.TestCase):
    local_provider = CachedDataProvider(cache_name='tests', expire_days=0, trading_days=True)

    def test_average_return(self):
        spy_daily = self.local_provider.get_data(ticker="spy", from_date='2010-01-01', to_date='2016-01-01')
        s = Seasonality("SPY", spy_daily)

        # Bullish Nov to May
        assert s.average_return(spy_daily.loc['20151103']['Day'], 22) > 0.0  # Nov-Dec
        assert s.average_return(spy_daily.loc['20151103']['Day'], 22 * 2) > 0.0  # Nov-Jan
        assert s.average_return(spy_daily.loc['20151103']['Day'], 22 * 3) > 0.0  # Nov-Feb
        assert s.average_return(spy_daily.loc['20151103']['Day'], 22 * 4) > 0.0  # Nov-Mar
        assert s.average_return(spy_daily.loc['20151103']['Day'], 22 * 5) > 0.0  # Nov-May

        # Bearish May to Nov
        assert s.average_return(spy_daily.loc['20150501']['Day'], 22) < 0.0  # May-June
        assert s.average_return(spy_daily.loc['20150501']['Day'], 22 * 2) < 0.0  # May-Jul
        assert s.average_return(spy_daily.loc['20150501']['Day'], 22 * 5) < 0.0  # May-Oct

        # assert seasonality_analysis.py.average_return('spy', '2016-11-05', '5M') > 0.0  # Throw error, lookahead bias?


if __name__ == '__main__':
    unittest.main()
