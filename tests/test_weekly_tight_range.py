#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset:4 -*-

import unittest

import sys
sys.path.append("../")

from qa_dataprovider.web_dataprovider import CachedWebDataProvider
from technical_analysis.weekly_tight_range import WeeklyTightRange



class TestWeeklyTightRange(unittest.TestCase):
    local_provider = CachedWebDataProvider('google', cache_name='tests', expire_days=0, trading_days=True)

    def test_previous_week_is_tight_range(self):
        aapl_daily = self.local_provider.get_data(['AAPL'], from_date='2011-08-01', to_date='2016-01-01',
                                                  timeframe='day')[0]
        aapl_weekly = self.local_provider.get_data(['AAPL'], from_date='2011-08-01', to_date='2016-01-01',
                                                   timeframe='week')[0]

        wtr = WeeklyTightRange('appl', 3, aapl_weekly)
        assert wtr.get_prev_tight_range_week(aapl_daily.loc['20120123'].name.date())  # Breaking previous weeks high?
        assert wtr.get_prev_tight_range_week(aapl_daily.loc['20120124'].name.date())
        assert wtr.get_prev_tight_range_week(aapl_daily.loc['20120125'].name.date())
        assert wtr.get_prev_tight_range_week(aapl_daily.loc['20120126'].name.date())
        assert wtr.get_prev_tight_range_week(aapl_daily.loc['20120127'].name.date())

        assert not wtr.get_prev_tight_range_week(aapl_daily.loc['20150127'].name.date())


if __name__ == '__main__':
    unittest.main()
