#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import datetime
from dateutil.relativedelta import relativedelta
import logging as logger

import pandas as pd

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')


class Seasonality:
    """
    To be used by backtester, scanning code etc.
    For example initialize once when starting scanner tool:
        seasonality = Seasonality('SPY', spy_daily)

    Then call with for every latest bar available:
        trading_day = spy_daily.loc['20151103']['Day']
        if long_conditions(spy_daily) and seasonality.average_return(trading_day, 22) > 0.0:
            enter_long()
    """
    def __init__(self, ticker, daily):
        self.data = trading_day_reindex(seasonality_returns(daily), ticker, ticker)

    def average_return(self, trading_day, forward_days):
        """
        Get the seasonality return from trading_day to forward_days.
        Should probably use multiple calls with different forward dates to get more reliable prediction.
        (dates differ year to year and seasonality df is reindexed to shortest year in analysis)
        """
        rotational_index = int(trading_day + forward_days) % len(self.data.index)
        rotations = int((trading_day + forward_days) / len(self.data.index))
        return ((self.data.iloc[rotational_index] + rotations * 100) - self.data.iloc[int(trading_day)])[0]


def rebase(prices):
    return prices / prices[0] * 100


def rebase_days(prices):
    return prices / prices[1] * 100


def normalize(df):
    return df.div(df.max())
    # Min-Max normalization
    # return (df-df.min()).div(df.max()-df.min())


def __normalized_per_year(df):
    slices = {}
    min_group = None
    min_days = 1000

    groups = df.groupby(df.index.year)
    for group in groups:
        if len(group[1]) < 240:  # will skip SPY 2001 with 225 etnries
            logger.warning("Skipping year {0} with only {1} entries".format(group[0], len(group[1])))
        else:
            closes = group[1]['Close']
            slices[group[0]] = normalize(pd.DataFrame(closes))

            if len(closes) < min_days:
                min_days = len(closes)
                min_group = group

    normalized = pd.DataFrame()
    for k in slices:
        normalized[k] = pd.Series(slices[k]['Close'].values)
    # normalized = normalized.shift(-1) # Drop first row due to log-return calculations (first day is NaN)

    logger.info("Setting seasonality index using days from {0}".format(min_group[0]))
    dates = min_group[1].index

    return normalized.dropna().set_index(dates)


def __normalized_per_month(df):
    monthly_averages = []
    month_columns = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    groups_months = df.groupby(df.index.month)
    for group_month in groups_months:
        df_month = group_month[1]
        groups_years = df_month.groupby(df_month.index.year)

        min_month = None
        min_days = 1000
        slices = {} # Will contain one month, normalzied, stored per year
        for group_years in groups_years:
            closes = group_years[1]['Close'] # Closes for one month, one year
            slices[group_years[0]] = trading_day_reindex(normalize(pd.DataFrame(closes)), group_years[0], 'Close')

            if len(closes) < min_days:
                min_days = len(closes)
                min_month = group_years[1]
            #for index, row in closes.iterrows():
            #    average.set_value(index, group[0], row.values.mean())
            #    return average
        #df = pd.DataFrame(index=[i for i in range(1,30)])
        # TODO: try different NaN methods, 'bfill', 'ffill', or drop all NaN
        df = pd.concat([slices[slice] for slice in slices], axis=1).fillna(method='ffill') #.dropna()
        average = pd.DataFrame()

        #DEBUG
        #if group_month[0] == 1:
        #    print("Jan",df)

        for index, row in df.iterrows():
            average.set_value(index, month_columns[group_month[0]], row.values.mean())

        # DEBUG
        #if group_month[0] == 1:
        #    print("Jan",average)
        monthly_averages.append(average)

    return monthly_averages


def seasonality_monthly_returns(df):
    ticker = df['Ticker'][0]
    start_year = df.index[0]
    end_year = df.index[-1]
    logger.info("{0}: using data for {1} years".format(ticker, relativedelta(end_year, start_year).years))

    normalized_monthly = __normalized_per_month(df)

    return normalized_monthly


def seasonality_returns(df):
    """
    Calculate seasonality for ticker. Years to include is based the first and last index, e.g. 2005-01-01 to 2015-12-31

    The result will be a new time series with normalized returns (0 to 1).
    Dataframe will be reindexed to the year with shortest trading days, e.g. 2012 when analyzing SPY.
    """

    ticker = df['Ticker'][0]
    start_year = df.index[0]
    end_year = df.index[-1]
    logger.info("{0}: using data for {1} years".format(ticker, relativedelta(end_year, start_year).years))

    # returns = pd.DataFrame(np.log(df['Close']).diff(), columns=['Close'])
    normalized = __normalized_per_year(df)

    average = pd.DataFrame(columns=[ticker])
    for index, row in normalized.iterrows():
        average.set_value(index, ticker, row.values.mean())
    return average


def trading_day_reindex(df, ticker, column):
    """
    Reindex df with consecutive numbering
    :param df: DataFrame
    :param ticker: new column name
    :param column: column in df to select
    :return:
    """
    days = range(1, len(df) - 1)
    return pd.DataFrame({ticker: df.ix[:, column].values}).reindex(days)

