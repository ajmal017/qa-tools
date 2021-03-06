#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset:4 -*-

import unittest

from qa_dataprovider.web_dataprovider import CachedWebDataProvider

import sys
sys.path.append("../")

from technical_analysis import ta
import technical_analysis.column_names as ta_columns
from technical_analysis.market_internal import MarketInternals


class TestMarketInternals(unittest.TestCase):
    testdata_provider = CachedWebDataProvider('google', cache_name='tests', expire_days=0, quote=False)

    def test_market_breadth(self):
        aapl = self.testdata_provider.get_data(['AAPL'], from_date='2016-01-01', to_date='2017-01-01')[0]
        msft = self.testdata_provider.get_data(['MSFT'], from_date='2016-01-01', to_date='2017-01-01')[0]
        gm = self.testdata_provider.get_data(['GM'], from_date='2016-01-01', to_date='2017-01-01')[0]
        tickers = [aapl, msft, gm]

        breadth = MarketInternals().breadth(tickers, 50, '2016-01-01', '2017-01-01', MarketInternals.hilo)
        assert 0 == breadth.loc['20161223'][ta_columns.day_low_name(50)]

    def test_market_breadth_dma(self):
        aapl = self.testdata_provider.get_data(['AAPL'], from_date='2010-01-01', to_date='2017-01-01')[0]
        msft = self.testdata_provider.get_data(['MSFT'], from_date='2010-01-01', to_date='2017-01-01')[0]
        gm = self.testdata_provider.get_data(['GM'], from_date='2010-01-01', to_date='2017-01-01')[0]
        tickers = [aapl, msft, gm]

        for ticker in tickers:
            ta.add_ma(ticker, 200)

        breadth = MarketInternals().breadth(tickers, 200, '2010-01-01', '2017-01-01', MarketInternals.dma)
        assert 3 == breadth.loc['20161223'][ta_columns.above_dma_name(200)]
        assert 0 == breadth.loc['20161223'][ta_columns.below_dma_name(200)]


if __name__ == '__main__':
    unittest.main()
