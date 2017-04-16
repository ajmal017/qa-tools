#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset:4 -*-

import unittest

from dataprovider.dataprovider import CachedDataProvider

from technical_analysis import ta
import technical_analysis.column_names as ta_columns
from technical_analysis.market_internal import MarketInternals

class TestMarketInternals(unittest.TestCase):

    testdata_provider = CachedDataProvider(cache_name='tests', expire_days=0,quote=False)

    def test_market_breadth(self):
        aapl = self.testdata_provider.get_data(ticker="AAPL", from_date='2016-01-01', to_date='2017-01-01')
        msft = self.testdata_provider.get_data(ticker="MSFT", from_date='2016-01-01', to_date='2017-01-01')
        gm = self.testdata_provider.get_data(ticker="GM", from_date='2016-01-01', to_date='2017-01-01')
        tickers = [aapl, msft, gm]

        columns = {
            'high_or_above': ta_columns.day_high_name(50),
            'high_or_above_pct': ta_columns.day_high_pct_name(50),
            'low_or_below': ta_columns.day_low_name(50),
            'low_or_below_pct': ta_columns.day_low_pct_name(50)
        }
        breadth = MarketInternals().breadth(tickers, 50, '2016-01-01', '2017-01-01', columns, MarketInternals.hilo)
        assert 0 == breadth.loc['20161223'][ta_columns.day_low_name(50)]


    def test_market_breadth_dma(self):
        aapl = self.testdata_provider.get_data(ticker="AAPL", from_date='2010-01-01', to_date='2017-01-01')
        msft = self.testdata_provider.get_data(ticker="MSFT", from_date='2010-01-01', to_date='2017-01-01')
        gm = self.testdata_provider.get_data(ticker="GM", from_date='2010-01-01', to_date='2017-01-01')
        tickers = [aapl, msft, gm]

        for ticker in tickers:
            ta.add_ma(ticker, 200)

        columns = {
            'high_or_above': ta_columns.above_dma_name(200),
            'high_or_above_pct': ta_columns.above_dma_pct_name(200),
            'low_or_below': ta_columns.below_dma_name(200),
            'low_or_below_pct': ta_columns.below_dma_pct_name(200)
        }
        breadth = MarketInternals().breadth(tickers,200,'2010-01-01', '2017-01-01', columns, MarketInternals.dma)
        assert 3 == breadth.loc['20161223'][ta_columns.above_dma_name(200)]
        assert 0 == breadth.loc['20161223'][ta_columns.below_dma_name(200)]


if __name__ == '__main__':
    unittest.main()