#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime

import click
import pandas as pd

from dataprovider.web_dataprovider import WebDataprovider
import talib
from technical_analysis.market_internal import MarketInternals

def get_tickers(file):
    with open(file) as f:
        return [ticker.rstrip() for ticker in f.readlines()]


def breadth(kwargs):
    #TODO: test redis and other backend storages
    internals = MarketInternals()
    provider = WebDataprovider(cache_name='breadth', expire_days=0)

    print("breadth for {0}".format(kwargs['tickers']))

def hilo(kwargs):
    internals = MarketInternals()
    provider = WebDataprovider(cache_name='breadth',expire_days=0)

    print("hilo for {0}".format(kwargs['tickers']))

    df_list = []
    for ticker in kwargs['tickers']:
        try:
            df_list.append(provider.get_data(ticker,from_date=kwargs['start'], to_date=kwargs['end']))
        except Exception as e:
            print("Skipping {ticker}: {error}".format(ticker=ticker, error=e))
    #df_list = [provider.get_data(ticker=ticker, from_date=kwargs['start'], to_date=kwargs['end']) for ticker in kwargs['tickers']]

    res = internals.breadth_daily(df_list, int(kwargs['lookback']), kwargs['start'], kwargs['end'])
    print(res)

@click.command(options_metavar='<options>')
@click.argument('function', metavar="<function>")
@click.argument('lookback', metavar="<lookback>")
@click.option('--start', default="2010-01-01", help='starting date.')
@click.option('--end', default="today", help='ending date')
@click.option('--tickers', default=False, help='Comma separated list of tickers')
def market_internals(function, lookback, start, end, tickers):
    """
    Calculate market internals such as market breadth etc.

    <function> parameter:

    'hilo': to calculate all stocks making new <lookback> highs/lows
    'breadth': calculate all stocks below/above <lookback> MA

    <lookback> parameter:
    """
    if end is 'today':
        end_datetime = datetime.datetime.now()
    else:
        end_datetime = datetime.datetime.strptime(end,'%Y-%M-%d')

    start_datetime = datetime.datetime.strptime(start,'%Y-%M-%d')

    args = {
        'function':function,
        'lookback':lookback,
        'start_dt':start_datetime,
        'start': start_datetime.strftime('%Y-%m-%d'),
        'end_dt':end_datetime,
        'end': end_datetime.strftime('%Y-%m-%d')
    }

    click.echo("{function}: {start} to {end} with lookack {lookback}".format(**args))

    if not tickers:
        click.echo("Tickers: all S&P500 stock")
        args['tickers'] = get_tickers("sp500.txt")
    else:
        args['tickers'] = tickers.split(",")


    if function == 'hilo':
        hilo(args)

    if function == 'breadth':
        breadth()

if __name__ == '__main__':
    market_internals()
