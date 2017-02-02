#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import logging as logger

import matplotlib.pyplot as plt
import matplotlib
import click
import pandas as pd
import talib

from technical_analysis.column_names import *

from dataprovider.dataprovider import CachedDataProvider
from technical_analysis.market_internal import MarketInternals

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')


def get_tickers(file):
    with open(file) as f:
        return [ticker.rstrip() for ticker in f.readlines()]


def breadth(kwargs):
    # TODO: test redis and other backend storages
    internals = MarketInternals()
    provider = CachedDataProvider(cache_name='breadth', expire_days=0)

    logger.info("breadth for {0} tickers".format(len(kwargs['tickers'])))


def hilo(kwargs):
    internals = MarketInternals()
    provider = CachedDataProvider(cache_name='breadth', expire_days=0, quote=kwargs['quotes'])

    logger.info("hilo for {0} tickers".format(len(kwargs['tickers'])))

    df_list = provider.get_data_parallel(kwargs['tickers'], from_date=kwargs['start'], to_date=kwargs['end'], provider=kwargs['provider'])
    res = internals.breadth_daily(df_list, int(kwargs['lookback']), kwargs['start'], kwargs['end'])
    if kwargs['plot']:
        #TODO: add SPY to plot?

        plot_data = res[[day_low_perc_name(kwargs['lookback']),day_high_perc_name(kwargs['lookback'])]]
        matplotlib.style.use('ggplot')

        plot_data.plot()
        plt.show()
    else:
        print(res[-3:])


@click.command(options_metavar='<options>')
@click.argument('function', metavar="<function>", type=click.STRING)
@click.argument('lookback', metavar="<lookback>", type=click.INT)
@click.option('--start', default="2010-01-01", help='starting date.')
@click.option('--end', default="today", help='ending date')
@click.option('--tickers', default=False, help='Comma separated list of tickers')
@click.option('--file',type=click.Path(exists=True), help="Read tickers from file")
@click.option('--provider',type=click.Choice(['yahoo', 'google']), default='google')
@click.option('--quotes', is_flag=True, help='Add intraday (possibly delayed) quotes, e.g. for analyzing during market opening hours.')
@click.option('--plot', is_flag=True, help='Plot analyzed data')
def market_internals(function, lookback, start, end, tickers, file, provider, quotes, plot):
    """
    Calculate market internals such as market breadth etc.

    Positional arguments

    function:

    'hilo': to calculate all stocks making new <lookback> highs/lows
    'breadth': calculate all stocks below/above <lookback> MA

    lookback:
    Integer to specify lookback period

    """
    if end is 'today':
        end_datetime = datetime.datetime.now()
    else:
        end_datetime = datetime.datetime.strptime(end, '%Y-%m-%d')

    start_datetime = datetime.datetime.strptime(start, '%Y-%m-%d')

    fun_kwargs = {
        'function': function,
        'lookback': lookback,
        'start_dt': start_datetime,
        'start': start_datetime.strftime('%Y-%m-%d'),
        'end_dt': end_datetime,
        'end': end_datetime.strftime('%Y-%m-%d'),
        'provider': provider,
        'quotes': (True if quotes else False),
        'plot': (True if plot else False)
    }
    logger.info("{function}: {start} to {end} with lookack {lookback}".format(**fun_kwargs))

    if file:
        fun_kwargs['tickers'] = get_tickers(file)
    else:
        if not tickers:
            raise Exception("Must provide list of tickers or tickers file")
        else:
            fun_kwargs['tickers'] = tickers.split(",")

    if function == 'hilo':
        hilo(fun_kwargs)

    if function == 'breadth':
        breadth()


if __name__ == '__main__':
    market_internals()
