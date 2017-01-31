from dataprovider.local_dataprovider import TestDataprovider
from technical_analysis import ta
from technical_analysis.column_names import *
from technical_analysis.market_internal import MarketInternals


class TestMarketInternals:

    testdata_provider = TestDataprovider()

    def test_market_breadth(self):
        aapl = self.testdata_provider.get_data(ticker="AAPL", from_date='2010-01-01', to_date='2017-01-01')
        msft = self.testdata_provider.get_data(ticker="MSFT", from_date='2010-01-01', to_date='2017-01-01')
        gm = self.testdata_provider.get_data(ticker="GM", from_date='2010-01-01', to_date='2017-01-01')
        tickers = [aapl, msft, gm]

        internals = MarketInternals()
        market_breadth = internals.breadth_daily(tickers, 50,'2010-01-01','2017-01-01')

        #print(market_breadth)
        assert 0 == market_breadth.loc['20161223'][day_low_name(50)]


    def test_market_breadth_dma(self):
        aapl = self.testdata_provider.get_data(ticker="AAPL", from_date='2010-01-01', to_date='2017-01-01')
        msft = self.testdata_provider.get_data(ticker="MSFT", from_date='2010-01-01', to_date='2017-01-01')
        gm = self.testdata_provider.get_data(ticker="GM", from_date='2010-01-01', to_date='2017-01-01')
        tickers = [aapl, msft, gm]

        for ticker in tickers:
            ta.add_ma(ticker, 200)

        internals = MarketInternals()
        breadth = internals.breadth_dma(tickers,200)
        assert 3 == breadth.loc['20161223'][above_dma_name(200)]
        assert 0 == breadth.loc['20161223'][below_dma_name(200)]

