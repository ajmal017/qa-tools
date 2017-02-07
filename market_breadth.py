#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import logging as logger

import matplotlib.pyplot as plt
import matplotlib
import click
import pandas as pd
import talib

from technical_analysis import ta
import technical_analysis.column_names as ta_columns
from dataprovider.dataprovider import CachedDataProvider
from technical_analysis.market_internal import MarketInternals

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')


def get_tickers(file):
    with open(file) as f:
        return [ticker.rstrip() for ticker in f.readlines()]



def do_plot(df, ticker, lower_column, higher_column, threshold):
    """
    ticker: plot with regular line style.
    lower_column: mark in plot where data point is > threshold
    higher_column: mark in plot were data point is > threshold
    """
    #TODO: titles text, labels
    percentages = [20, 30, 40, 50]
    lows = []
    highs = []
    for l in percentages:
        tmp = df[[lower_column]]
        tmp = tmp[(tmp > l)].dropna()
        tmp = pd.concat([tmp, df[[ticker]]], axis=1, join='inner')
        lows.append(tmp)

    for l in percentages:
        tmp = df[[higher_column]]
        tmp = tmp[(tmp > l)].dropna()
        tmp = pd.concat([tmp, df[[ticker]]], axis=1, join='inner')
        highs.append(tmp)

    # lows_20 = df[[lower_column]]
    # lows_20 = lows_20[(lows_20 > 20)].dropna()
    # lows_20 = pd.concat([lows_20,df[[ticker]]],axis=1, join='inner')
    #
    # lows_30 = df[[lower_column]]
    # lows_30 = lows_30[(lows_30 > 30)].dropna()
    # lows_30 = pd.concat([lows_30, df[[ticker]]], axis=1, join='inner')
    #
    # lows_40 = df[[lower_column]]
    # lows_40 = lows_40[(lows_40 > 40)].dropna()
    # lows_40 = pd.concat([lows_40, df[[ticker]]], axis=1, join='inner')
    #
    # lows_50 = df[[lower_column]]
    # lows_50 = lows_50[(lows_50 > 50)].dropna()
    # lows_50 = pd.concat([lows_50, df[[ticker]]], axis=1, join='inner')

    #highs = df[[higher_column]]
    #highs = highs[(highs > threshold)].dropna()
    #highs = pd.concat([highs,df[[ticker]]],axis=1, join='inner')

    fig, ax1 = plt.subplots()
    ax1.plot(df[[ticker]].index, df[[ticker]], 'b-', label=ticker)

    for i, item in enumerate(lows):
        ax1.plot(item.index, item[[ticker]], 'r.', label="{0}% Making New {1} Day Low".format(percentages[i], threshold), markersize=(4+(i*2)))
    #ax1.plot(lows_20.index, lows_20[[ticker]], 'r.', label="20% {0} Day low".format(threshold), markersize=4)
    #ax1.plot(lows_30.index, lows_30[[ticker]], 'r.', label="30% {0} Day low".format(threshold), markersize=8)
    #ax1.plot(lows_40.index, lows_40[[ticker]], 'r.', label="40% {0} Day low".format(threshold), markersize=12)
    #ax1.plot(lows_50.index, lows_50[[ticker]], 'r.', label="50% {0} Day low".format(threshold), markersize=16)

    for i, item in enumerate(highs):
        ax1.plot(item.index, item[[ticker]], 'g.', label="{0}% Making New {1} Day High".format(percentages[i], threshold), markersize=(4+(i*2)))

    #ax1.plot(highs.index, highs[[ticker]], 'g.', label=higher_column)
    #matplotlib.style.use('ggplot')

    legend = ax1.legend(loc='upper left', shadow=False, fontsize=8)
    #legend.get_frame().set_facecolor('#00FFCC')
    plt.title("% of Stocks Making New {0} Day High/Low".format(threshold))
    plt.show()

def dma_analysis(kwargs):
    internals = MarketInternals()
    lookback = kwargs['lookback']
    provider = CachedDataProvider(cache_name='breadth', expire_days=0, quote=kwargs['quotes'])

    if kwargs['verbose']:
        click.echo("Fetching data for {0} tickers".format(len(kwargs['tickers'])))

    columns = {
        'high_or_above': ta_columns.above_dma_name(lookback),
        'high_or_above_pct': ta_columns.above_dma_pct_name(lookback),
        'low_or_below': ta_columns.below_dma_name(lookback),
        'low_or_below_pct': ta_columns.below_dma_pct_name(lookback)
    }
    df_list = provider.get_data_parallel(kwargs['tickers'], from_date=kwargs['start'], to_date=kwargs['end'], provider=kwargs['provider'])

    t0 = datetime.datetime.now()
    df_with_ta = [ta.add_ma(df, lookback) for df in df_list]
    logger.info("TA for dataframes done: {0}".format(datetime.datetime.now() - t0))

    if kwargs['verbose']:
        click.echo("Running market breadth function '{0}'".format(kwargs['function']))
    t0 = datetime.datetime.now()
    res = internals.breadth(df_with_ta, int(lookback), kwargs['start'], kwargs['end'], columns, MarketInternals.dma)
    logger.info("Function '{0}' completed in {1}".format(kwargs['function'],datetime.datetime.now()-t0))

    if kwargs['plot_vs']:
        plot_vs = provider.get_data(kwargs['plot_vs'], from_date=kwargs['start'], to_date=kwargs['end'],
                                    provider=kwargs['provider'])
        plot_vs = pd.DataFrame(plot_vs['Close']).rename(columns={'Close': kwargs['plot_vs']}) # Prepare compare dataframe
        plot_data = res[[columns['low_or_below_pct'], columns['high_or_above_pct']]] # Select above/below percentage columns
        plot_data = plot_data[(plot_data > 0)] # Skip all zero data points
        df = pd.concat([plot_vs, plot_data], axis=1, join='inner') # join percentage values on valid trading days for compare

        do_plot(df, kwargs['plot_vs'], columns['low_or_below_pct'], columns['high_or_above_pct'], lookback)
    else:
        click.echo(res)


def hilo_analysis(kwargs):
    internals = MarketInternals()
    lookback = kwargs['lookback']
    provider = CachedDataProvider(cache_name='breadth', expire_days=0, quote=kwargs['quotes'])

    if kwargs['verbose']:
        click.echo("Fetching data for {0} tickers".format(len(kwargs['tickers'])))
    df_list = provider.get_data_parallel(kwargs['tickers'], from_date=kwargs['start'], to_date=kwargs['end'], provider=kwargs['provider'])

    columns = {
        'high_or_above':ta_columns.day_high_name(lookback),
        'high_or_above_pct': ta_columns.day_high_pct_name(lookback),
        'low_or_below': ta_columns.day_low_name(lookback),
        'low_or_below_pct': ta_columns.day_low_pct_name(lookback)
    }

    if kwargs['verbose']:
        click.echo("Running market breadth function '{0}'".format(kwargs['function']))
    t0 = datetime.datetime.now()
    res = internals.breadth(df_list, int(lookback), kwargs['start'], kwargs['end'], columns, MarketInternals.hilo)
    logger.info("Function '{0}' completed in {1}".format(kwargs['function'],datetime.datetime.now()-t0))

    if kwargs['plot_vs']:
        plot_vs = provider.get_data(kwargs['plot_vs'], from_date=kwargs['start'], to_date=kwargs['end'], provider=kwargs['provider'])
        plot_vs = pd.DataFrame(plot_vs['Close']).rename(columns={'Close':kwargs['plot_vs']})

        plot_data = res[[columns['low_or_below_pct'], columns['high_or_above_pct']]]
        plot_data = plot_data[(plot_data > 0)] # Skip all zero data points
        df = pd.concat([plot_vs,plot_data],axis=1, join='inner')

        do_plot(df, kwargs['plot_vs'], columns['low_or_below_pct'], columns['high_or_above_pct'], lookback)


        # Plot_vs as line and breadth as bar?
        #matplotlib.style.use('ggplot')
        #fig, ax = plt.subplots(2, 1)  # you can pass sharex=True, sharey=True if you want to share axes.
        #df[['SPY']].plot(kind='line', ax=ax[0])
        #df[[day_low_pct_name(kwargs['lookback']), day_high_pct_name(kwargs['lookback'])]].plot(ax=ax[1],style=['.',','],linestyle='None')
        #plt.show()

        #TODO: Try Seaborn
            #TODO: XLP,XLE,XLF etf vs. constitunts

    else:
        #TODO: how to visualize todays breadth quickly?
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
@click.option('--plot-vs', type=click.STRING, help='Plot analysis vs. stock/etf, e.g. SPY')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
def market_internals(function, lookback, start, end, tickers, file, provider, quotes, plot_vs, verbose):
    """
    Calculate market internals such as market breadth etc.

    Positional arguments

    function:

    'hilo': to calculate all stocks making new <lookback> highs/lows
    'dma': calculate all stocks below/above <lookback> MA

    lookback:
    Integer to specify lookback period

    """
    # TODO: test redis and other backend storages?
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
        'plot_vs':plot_vs,
        'verbose':verbose
    }
    #TODO: click.echo for verbose output, logger for debugging only?
    click.echo("{function}: {start} to {end} with lookack {lookback}".format(**fun_kwargs))

    if file:
        fun_kwargs['tickers'] = get_tickers(file)
    else:
        if not tickers:
            raise Exception("Must provide list of tickers or tickers file")
        else:
            fun_kwargs['tickers'] = tickers.split(",")

    if function == 'hilo':
        hilo_analysis(fun_kwargs)

    if function == 'dma':
        # AKA SPXA50R http://stockcharts.com/h-sc/ui?s=$SPXA50R
        dma_analysis(fun_kwargs)


if __name__ == '__main__':
    market_internals()
