from technical_analysis.market_internal import MarketInternals
from dataprovider.local_dataprovider import TestDataprovider

class TestMarketInternals:

    testdata_provider = TestDataprovider()


    def test_market_breadth_50D_highs(self):
        aapl = self.testdata_provider.get_data(ticker="AAPL", from_date='2010-01-01', to_date='2017-01-01')
        msft = self.testdata_provider.get_data(ticker="MSFT", from_date='2010-01-01', to_date='2017-01-01')
        gm = self.testdata_provider.get_data(ticker="GM", from_date='2010-01-01', to_date='2017-01-01')
        tickers = [aapl, msft, gm]

        internals = MarketInternals()
        market_breadth = internals.breadth_daily(tickers, 50)

        print(market_breadth)
        #assert 0 == market_breadth.loc['20161223'][internals.DAY_HIGH_50]