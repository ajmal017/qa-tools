#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import datetime
import logging as logger

import click
import pandas as pd

import matplotlib
try:
    import tkinter # should fail on AWS images with no GUI available
    import matplotlib.pyplot as plt
except:
    matplotlib.use('Agg')


from technical_analysis import ta
import technical_analysis.column_names as ta_columns
from dataprovider.dataprovider import CachedDataProvider
from technical_analysis.market_internal import MarketInternals

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')


def get_tickers(file):
    with open(file) as f:
        return [ticker.rstrip() for ticker in f.readlines()]


def do_plot(df, ticker, lower_column, higher_column, threshold, pct_levels, title):
    """
    ticker: datatframe column to plot with regular line style
    lower_column/higher_columns: dataframe columns to mark in plot where data point is > threshold
    """

    lows = []
    highs = []
    for level in pct_levels:
        lower = df[[lower_column]]
        lower = lower[(lower > int(level))].dropna()
        lows.append(pd.concat([lower, df[[ticker]]], axis=1, join='inner'))

    for level in pct_levels:
        higher = df[[higher_column]]
        higher = higher[(higher > int(level))].dropna()
        highs.append(pd.concat([higher, df[[ticker]]], axis=1, join='inner'))


    fig, ax1 = plt.subplots()
    ax1.plot(df[[ticker]].index, df[[ticker]], 'b-', label=ticker)

    for i, item in enumerate(lows):
        ax1.plot(item.index, item[[ticker]], 'r.', label="{0}% {1}".format(pct_levels[i], lower_column), markersize=(4+(i*2)))

    for i, item in enumerate(highs):
        ax1.plot(item.index, item[[ticker]], 'g.', label="{0}% {1}".format(pct_levels[i], higher_column), markersize=(4+(i*2)))

    legend = ax1.legend(loc='upper left', shadow=False, fontsize=8)
    #legend.get_frame().set_facecolor('#00FFCC')
    plt.title(title)
    plt.show()

def dma_analysis(kwargs, df_list, plot_vs):
    lookback = kwargs['lookback']
    internals = MarketInternals()
    fun = MarketInternals.dma
    column_mappings = ta_columns.pos_neg_columns_mapping(lookback, fun.__name__)

    t0 = datetime.datetime.now()
    df_with_ta = [ta.add_ma(df, lookback) for df in df_list]
    logger.info("TA for dataframes done: {0}".format(datetime.datetime.now() - t0))

    click.echo("Running market breadth function '{0}'".format(kwargs['function']))
    t0 = datetime.datetime.now()
    res = internals.breadth(df_with_ta, int(lookback), kwargs['start'], kwargs['end'], fun)
    logger.info("Function '{0}' completed in {1}".format(kwargs['function'],datetime.datetime.now()-t0))

    if kwargs['plot_vs']:
        plot_vs = pd.DataFrame(plot_vs['Close']).rename(columns={'Close': kwargs['plot_vs']}) # Prepare compare dataframe
        plot_data = res[[column_mappings['neg_pct'], column_mappings['pos_pct']]] # Select above/below percentage columns
        plot_data = plot_data[(plot_data > 0)] # Skip all zero data points
        df = pd.concat([plot_vs, plot_data], axis=1, join='inner') # join percentage values on valid trading days for compare

        plot_title = "% of Stocks above/below {0}DMA".format(lookback)
        do_plot(df, kwargs['plot_vs'], column_mappings['neg_pct'], column_mappings['pos_pct'], lookback, kwargs['plot_pct_levels'], plot_title)
    else:
        click.echo(res)


def hilo_analysis(kwargs, df_list, plot_vs):
    internals = MarketInternals()
    lookback = kwargs['lookback']
    fun = MarketInternals.hilo
    column_mapping = ta_columns.pos_neg_columns_mapping(lookback, fun.__name__)

    click.echo("Running market breadth function '{0}'".format(kwargs['function']))
    t0 = datetime.datetime.now()
    res = internals.breadth(df_list, int(lookback), kwargs['start'], kwargs['end'], fun)
    logger.info("Function '{0}' completed in {1}".format(kwargs['function'],datetime.datetime.now()-t0))

    if kwargs['plot_vs']:
        plot_vs = pd.DataFrame(plot_vs['Close']).rename(columns={'Close':kwargs['plot_vs']})
        plot_data = res[[column_mapping['neg_pct'], column_mapping['pos_pct']]]
        plot_data = plot_data[(plot_data > 0)] # Skip all zero data points
        df = pd.concat([plot_vs,plot_data],axis=1, join='inner')

        plot_title = "% of Stocks Making New {0} Day Highs/Lows".format(lookback)
        do_plot(df, kwargs['plot_vs'], column_mapping['neg_pct'], column_mapping['pos_pct'], lookback, kwargs['plot_pct_levels'], plot_title)

    else:
        click.echo(res[-lookback:])


@click.command(options_metavar='<options>')
@click.argument('function', metavar="<function>", type=click.STRING)
@click.argument('lookback', metavar="<lookback>", type=click.INT)
@click.option('--start', required=True, default="2010-01-01", help='starting date.')
@click.option('--end', default="today", help='ending date')
@click.option('--tickers', default=False, help='Comma separated list of tickers')
@click.option('--file',type=click.Path(exists=True), help="Read tickers from file")
@click.option('--provider',type=click.Choice(['yahoo', 'google']), default='google')
@click.option('--quotes', is_flag=True, help='Add intraday (possibly delayed) quotes, e.g. for analyzing during market opening hours')
@click.option('--plot-vs', type=click.STRING, help='Which Stock/ETF to visualize breadth, e.g. \'SPY\'')
@click.option('--plot-pct-levels', default='50,75,90', type=click.STRING, help='Comma separated list, e.g. \'75,90\' to visulize when 75% and 90% of stocks making 20-Day highs/lows')
def main(function, lookback, start, end, tickers, file, provider, quotes, plot_vs, plot_pct_levels):
    """
    Tool for analyzing and plotting market internals

    <lookback>: Integer to specify lookback period

    <function>: Available analysis methods

    'hilo': to calculate all stocks making new daily highs/lows.

    'dma': calculate all stocks below/above any moving average.

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
        'plot_vs':plot_vs,
        'plot_pct_levels': plot_pct_levels.split(",")
    }

    if file:
        fun_kwargs['tickers'] = get_tickers(file)
    else:
        if not tickers:
            raise Exception("Must provide list of tickers or tickers file")
        else:
            fun_kwargs['tickers'] = tickers.split(",")

    click.echo("Fetching data for {0} tickers".format(len(fun_kwargs['tickers'])))
    provider = CachedDataProvider(cache_name='breadth', expire_days=0, quote=fun_kwargs['quotes'])
    df_list = provider.get_data_parallel(fun_kwargs['tickers'], from_date=fun_kwargs['start'], to_date=fun_kwargs['end'],
                                         provider=fun_kwargs['provider'], max_workers=10)

    if fun_kwargs['plot_vs']:
        plot_vs = provider.get_data(fun_kwargs['plot_vs'], from_date=fun_kwargs['start'], to_date=fun_kwargs['end'],
                                provider=fun_kwargs['provider'])
    if function == 'hilo':
        hilo_analysis(fun_kwargs, df_list, plot_vs)

    if function == 'dma':
        # Similar to SPXA50R http://stockcharts.com/h-sc/ui?s=$SPXA50R
        dma_analysis(fun_kwargs, df_list, plot_vs)

    if provider.errors > 0:
        logger.warning("Missing data for {0} tickers.".format(provider.errors))



if __name__ == '__main__':
    main()
