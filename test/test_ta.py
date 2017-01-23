from dataprovider.local_dataprovider import LocalDataprovider
from technical_analysis import ta

class TestTechnicalAnalysis:

    local_provider = LocalDataprovider()

    def test_ma_slope(self):
        spy_daily = self.local_provider.get_data(ticker="spy", from_date='2010-01-01', to_date='2017-01-01')

        assert "2010-01-04 00:00:00" == spy_daily.iloc[0].name.__str__()
        assert "2010-01-06 00:00:00" == spy_daily.iloc[2].name.__str__()

        df = ta.add_ma_slope(spy_daily, 50)

        assert -1 == df.loc['20160115'][ta.ma_slope_column_name(50)]


