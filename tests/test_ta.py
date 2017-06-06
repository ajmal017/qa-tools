#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset:4 -*-

import unittest

from qa_dataprovider.web_dataprovider import CachedWebDataProvider
from technical_analysis import ta
import technical_analysis.column_names as ta_columns


class TestTechnicalAnalysis(unittest.TestCase):
    local_provider = CachedWebDataProvider('google', cache_name='tests', expire_days=0)

    def test_ma_slope(self):
        spy_daily = self.local_provider.get_data(['SPY'], from_date='2010-01-01', to_date='2017-01-01')[0]

        assert "2010-01-04 00:00:00" == spy_daily.iloc[0].name.__str__()
        assert "2010-01-06 00:00:00" == spy_daily.iloc[2].name.__str__()

        df = ta.add_ma_slope(spy_daily, 50)

        assert -1 == df.loc['20160115'][ta_columns.ma_slope_name(50)]

    def test_highest(self):
        spy_daily = self.local_provider.get_data(['SPY'], from_date='2010-01-01', to_date='2017-01-01')[0]
        assert ta.highest(spy_daily.loc[:'20161205']['Close']) < 50

        # for index, row in spy_daily.iterrows():
        #    print(index,":", row['Close'], " ", ta.highest(spy_daily.loc[:index]['Close']))

    def test_lowest(self):
        spy_daily = self.local_provider.get_data(['SPY'], from_date='2010-01-01', to_date='2017-01-01')[0]
        assert ta.lowest(spy_daily.loc[:'20161222']['Close']) == 3

        # for index, row in spy_daily.iterrows():
        #    print(index,":", row['Close'], " ", ta.lowest(spy_daily.loc[:index]['Close']))

    def test_atr_weekly(self):
        spy_weekly = self.local_provider.get_data(['SPY'], from_date='2010-01-01', to_date='2016-01-01',
                                                  timeframe='week')[0]
        ta.add_atr(spy_weekly, 2)
        # print(spy_weekly)


if __name__ == '__main__':
    unittest.main()
