#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import logging as logger

import matplotlib.pyplot as plt
import matplotlib
import click
import pandas as pd

from dataprovider.dataprovider import CachedDataProvider
from technical_analysis import seasonality

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')

# https://ismayc.github.io/moderndiver-book/4-viz.html
# Facets: per month

@click.option('--start', type=click.STRING, help='Starting year, e.g. \'2005-01-01\'')
@click.option('--end', type=click.STRING, help='Ending year, e.g. \'2015-12-31\'')
@click.option('--ticker', default=False, help='Ticker to analyze, e.g. \'SPY\'')
@click.option('--provider',type=click.Choice(['yahoo', 'google']), default='google')
def seasonality_analysis(ticker, provider, start, end):
    click.echo("Fetching data for {0}".format(ticker))
    provider = CachedDataProvider(cache_name='seasonality', expire_days=0)
    df = provider.get_data(ticker, start, end)
    s = seasonality.seasonality_returns(df)
    #TODO: normalize to first entry = 100?
    print(s)
    s.plot()
    plt.show()


if __name__ == '__main__':
    # Example:
    # $ seasonality.py --ticker=SPY --start=2005 --end=2010
    seasonality_analysis("SPY","google","2000-01-01","2016-12-31")
