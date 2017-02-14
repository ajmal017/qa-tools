from dateutil.relativedelta import relativedelta
import logging as logger

import numpy as np
import pandas as pd

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')


# Compare to SPY verifed edge, NOV-MAY, http://archive.aweber.com/awlist3824363/5qoFy/h/Closer_look_at_the.htm
# "Predictive Average-kurvan baserad på de 3 föregående årens data visa negativ avkastning kommande månad"

# During Nov-May, sell SPY ITM and closest OTM strike at close of third week each month
# - check average loss, limited by 0.5, 1.0, 1.5 etc (the protection)

#TA indicator:
# Rating colums (winrate): 1w, 2w, 3w, 4w, 2m, 3m, 4m, 5m, etc.
# Average returns: 1w, 2w, 3w, 4w, 2m, 3m, 4m, 5m, etc.
# example rule: only long if rating from todays close to 2w up to 2m is > 50


def rebase(prices):
    return prices/prices[0]*100

def normalize(df):
    return df.div(df.max())
    # Min-Max normalization
    #return (df-df.min()).div(df.max()-df.min())

def normalized_per_year(df):
    slices = {}
    min_group = None
    min_days = 1000

    groups = df.groupby(df.index.year)
    for group in groups:
        if len(group[1]) < 240: # will skip SPY 2001 with 225 etnries
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
    #normalized = normalized.shift(-1) # Drop first row due to log-return calculations (first day is NaN)

    logger.info("Setting seasonality index using days from {0}".format(min_group[0]))
    dates = min_group[1].index

    return normalized.dropna().set_index(dates)

def seasonality_returns(df, market_regime):
    #TODO: market regime
    ticker=df['Ticker'][0]
    start_year = df.index[0]
    end_year = df.index[-1]
    logger.info("{0}: using data for {1} years".format(ticker,relativedelta(end_year,start_year).years))

    #returns = pd.DataFrame(np.log(df['Close']).diff(), columns=['Close'])
    normalized = normalized_per_year(df)

    average = pd.DataFrame(columns=[ticker])
    for index, row in normalized.iterrows():
        average.set_value(index,ticker, row.values.mean())
    return average


def average_return(df, today, forward):
    pass

def win_rate(df, today, forward):
    pass

