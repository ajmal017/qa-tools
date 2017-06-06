#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime

import click
import matplotlib.pyplot as plt
import pandas as pd

from technical_analysis.column_names import rocp_name
from technical_analysis import ta

"""
From: http://wwwjonnywebspider.blogspot.com/2012/03/3-weeks-tight-pattern.html
RULES FOR 3 WEEKS TIGHT PATTERN

    Price must clear the buy point on strong volume before initiating a position, do not buy just because you have seen a 3 week pattern form.

Volume on break out must be above 40% above average or greater than the last 6 weeks at least.

General market must be in a confirmed uptrend, do not buy if market is in a correction phase.

Avoid thinly traded stocks or stocks that trade under 500,000 shares daily.

Backtesting:
1. Only analyze low spread optionable stocks
2. Plot average return and winrate X days after entry, e.g. if 3week's high is taken out on "today"
3. Average loss dictates vertical put spread size
4. Try weekly trailing stop, trailing 2x10ATR stop, etc.

"""


class WeeklyTightRange:
    def __init__(self, ticker, lookback, weekly):
        """
        :param ticker:
        :param lookback:
        :param weekly:
        """
        roc_lookback = 1

        weekly = ta.add_rocp(weekly, roc_lookback)
        self.tight_range_weeks = []
        for i in range(lookback - 1, len(weekly)):
            tight_range = True
            for j in range(0, lookback - 1):  # TODO: lookback or lookback-1?
                value = abs(weekly.iloc[i - j][rocp_name(roc_lookback)])
                if value > 0.01:
                    tight_range = False

            if tight_range:
                # print("Tight range:",weekly.iloc[i].name)
                date = weekly.iloc[i].name.date()
                data = weekly.iloc[i]
                self.tight_range_weeks.append({'calendar': date.isocalendar(), 'data': data})
                # weekdays_left = 5-date.isoweekday()
                # end_of_week = date + datetime.timedelta(days=weekdays_left)
                # while date <= end_of_week:
                #    self.tight_range_weeks.append(date)
                #    date += datetime.timedelta(days=1)
                # print("Tight ranges")
                # for i in self.tight_range_weeks:
                #    print(i)

    def get_prev_tight_range_week(self, date):
        """
        Check if the given date is within a week after a tight week range
        """
        prev_week = (date + datetime.timedelta(weeks=-1)).isocalendar()
        for week in self.tight_range_weeks:
            if week['calendar'][0] == prev_week[0] and week['calendar'][1] == prev_week[1]:
                return week

        return None


# TODO: inhereit from general analysis class?
def plot(daily):
    """
    Plot the average return X days from each entry signal
    """

    print(daily[daily['SIGNAL'] == 'BUY'])
    days = 20
    averages = pd.DataFrame()
    print(averages)

    for i in range(0, len(daily)):
        row = daily.iloc[i]
        if row['SIGNAL'] == 'BUY':
            return_series = []
            for j in range(0, days):
                ret = daily.iloc[i + 1 + j]['Close'] - row['Close']
                ret_pct = ret / row['Close'] * 100
                return_series.append(ret_pct)
            averages[row.name.date()] = pd.Series(return_series)

    averages.index.name = 'Days'
    averages['Avg. return'] = averages.mean(axis=1)
    print(averages)
    averages['Avg. return'].plot()
    # averages.plot()
    plt.show()


def add_signals(ticker, from_date, to_date, daily, weekly):
    """
    Get DataFrame with daily buy signal bars. May contain consecutive entry days.
    """
    wtr = WeeklyTightRange(ticker, 3, weekly)

    daily['SIGNAL'] = 'NA'
    for i in range(0, len(daily)):
        row = daily.iloc[i]
        tight_week = wtr.get_prev_tight_range_week(row.name.date())
        if tight_week:
            if row['Close'] > tight_week['data']['High']:
                daily.set_value(daily.index[i], 'SIGNAL', 'BUY')
                # print("{0}: {1} break prev weeks tight range high {2}".format(row.name.date(), row['Close'], tight_week['data']['High']))

    # Reset consecutive BUY signals
    for i in range(0, len(daily)):
        row = daily.iloc[i]
        if row['SIGNAL'] == 'BUY':
            daily.set_value(daily.index[i + 1], 'SIGNAL', 'NA')
            daily.set_value(daily.index[i + 2], 'SIGNAL', 'NA')
            daily.set_value(daily.index[i + 3], 'SIGNAL', 'NA')
            daily.set_value(daily.index[i + 4], 'SIGNAL', 'NA')

    return daily


# @click.command(options_metavar='<options>')
@click.option('--start', required=True, default="2010-01-01", help='Starting date.')
@click.option('--end', required=True, default="today", help='Ending date')
@click.option('--ticker', required=True, default="today", help='Ticker to analyze')
@click.option('--provider', type=click.Choice(['yahoo', 'google']), default='google')
def main(start, end, ticker, provider):
    p = CachedDataProvider(cache_name="weekly_tight_range", expire_days=0)
    weekly = p.get_data_parallel([ticker], start, end, timeframe="week", provider=provider)[0]
    daily = p.get_data_parallel([ticker], start, end, timeframe="day", provider=provider)[0]

    signals = add_signals([ticker], start, end, daily, weekly)
    plot(daily)


if __name__ == '__main__':
    main('2005-01-01', '2016-12-31', 'RL', 'google')
