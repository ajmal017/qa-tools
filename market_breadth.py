#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import logging as logger

import click
import pandas as pd
import talib

from dataprovider.web_dataprovider import WebDataprovider
from technical_analysis.market_internal import MarketInternals

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')


def get_tickers(file):
    with open(file) as f:
        return [ticker.rstrip() for ticker in f.readlines()]


def breadth(kwargs):
    # TODO: test redis and other backend storages
    internals = MarketInternals()
    provider = WebDataprovider(cache_name='breadth', expire_days=0)

    logger.info("breadth for {0} tickers".format(len(kwargs['tickers'])))


def hilo(kwargs):
    internals = MarketInternals()
    provider = WebDataprovider(cache_name='breadth', expire_days=0)

    logger.info("hilo for {0} tickers".format(len(kwargs['tickers'])))

    df_list = provider.get_data_parallel(kwargs['tickers'], from_date=kwargs['start'], to_date=kwargs['end'], provider=kwargs['provider'])
    res = internals.breadth_daily(df_list, int(kwargs['lookback']), kwargs['start'], kwargs['end'])
    print(res)



@click.command(options_metavar='<options>')
@click.argument('function', metavar="<function>", type=click.STRING)
@click.argument('lookback', metavar="<lookback>", type=click.INT)
@click.option('--start', default="2010-01-01", help='starting date.')
@click.option('--end', default="today", help='ending date')
@click.option('--tickers', default=False, help='Comma separated list of tickers')
@click.option('--file',type=click.Path(exists=True), help="Read tickers from file")
@click.option('--provider',type=click.Choice(['yahoo', 'google']), default='google')
def market_internals(function, lookback, start, end, tickers, file, provider):
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

    fun_params = {
        'function': function,
        'lookback': lookback,
        'start_dt': start_datetime,
        'start': start_datetime.strftime('%Y-%m-%d'),
        'end_dt': end_datetime,
        'end': end_datetime.strftime('%Y-%m-%d'),
        'provider': provider
    }
    logger.info("{function}: {start} to {end} with lookack {lookback}".format(**fun_params))

    if file:
        fun_params['tickers'] = get_tickers(file)
    else:
        if not tickers:
            raise Exception("Must provide list of tickers or tickers file")
        else:
            fun_params['tickers'] = tickers.split(",")

    if function == 'hilo':
        hilo(fun_params)

    if function == 'breadth':
        breadth()


if __name__ == '__main__':
    market_internals()
