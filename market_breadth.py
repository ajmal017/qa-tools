#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import datetime
import logging as logger

import click
import pandas as pd

import matplotlib

from utils.context import Context

try:
    import tkinter  # should fail on AWS images with no GUI available
    import matplotlib.pyplot as plt
except:
    matplotlib.use('Agg')

from qa_dataprovider import AVAILABLE_PROVIDERS
from technical_analysis import ta
import technical_analysis.column_names as ta_columns
from qa_dataprovider.web_dataprovider import CachedWebDataProvider
from technical_analysis.market_internal import MarketInternals
from utils import argutils



def do_plot(df, ticker, lower_column, higher_column, pct_levels, title):
    """
    Plot data
    
    :param (pd.DataFrame) df: dataframe to plot 
    :param (str) ticker: the ticker to plot versus with regular line style
    :param (str) lower_column: columns in df to mark where data point < pct_levels
    :param (str) higher_column: columns in df to mark where data point > pct_levels 
    :param (list) pct_levels: the percent levels to use as threshold for plot
    :param (str) title: plot title 
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
        ax1.plot(item.index, item[[ticker]], 'r.', label=">{0}{1}".
                 format(pct_levels[i], lower_column), markersize=(4 + (i * 2)))

    for i, item in enumerate(highs):
        ax1.plot(item.index, item[[ticker]], 'g.', label=">{0}{1}".
                 format(pct_levels[i], higher_column), markersize=(4 + (i * 2)))

    legend = ax1.legend(loc='upper left', shadow=False, fontsize=8)
    # legend.get_frame().set_facecolor('#00FFCC')
    plt.title(title)
    plt.show()


def dma_analysis(lookback, start_date, end_date, df_list, plot_vs_df, plot_pct_levels):
    """
    Stocks above/below DMA levels
    
    :param str lookback: lookback period
    :param str start_date: e.g. '2016-01-01'
    :param str end_date: e.g. '2017-01-01'
    :param list df_list: a list of dataframes  
    :param pd.DataFrame plot_vs_df: data with to compare in plot 
    :param list plot_pct_levels: list with percent levels, e.g. ['20,'30']    
    :return: 
    """

    internals = MarketInternals()
    fun = MarketInternals.dma
    column_mappings = ta_columns.pos_neg_columns_mapping(lookback, fun.__name__)
    df_with_ta = [ta.add_ma(df, lookback) for df in df_list]

    click.echo("Running market breadth function 'dma'")
    t0 = datetime.datetime.now()
    res = internals.breadth(df_with_ta, int(lookback), start_date, end_date, fun)
    logger.info("Function 'dma' completed in {}".format(datetime.datetime.now() - t0))

    if plot_vs_df is not None:
        plot_vs = plot_vs_df['Ticker'][0]

        # Prepare compare dataframe
        plot_vs_df = pd.DataFrame(plot_vs_df['Close']).rename(columns={'Close': plot_vs})

        # Select above/below percentage columns
        plot_data = res[[column_mappings['neg_pct'], column_mappings['pos_pct']]]

        # Skip all zero data points
        plot_data = plot_data[(plot_data > 0)]

        # join percentage values on valid trading days for compare
        df = pd.concat([plot_vs_df, plot_data], axis=1,join='inner')

        plot_title = "% of stocks above/below {0}-DMA".format(lookback)
        do_plot(df, plot_vs, column_mappings['neg_pct'], column_mappings['pos_pct'],
                plot_pct_levels, plot_title)
    else:
        click.echo(res)


def hilo_analysis(lookback, start_date, end_date, df_list, plot_vs_df, plot_pct_levels):
    """
    New highs and lows analysis
    
    :param str lookback: lookback period
    :param str start_date: e.g. '2016-01-01'
    :param str end_date: e.g. '2017-01-01'
    :param list df_list: a list of dataframes  
    :param pd.DataFrame plot_vs_df: data with to compare in plot 
    :param list plot_pct_levels: list with percent levels, e.g. ['20,'30']      
    """
    internals = MarketInternals()
    fun = MarketInternals.hilo
    column_mapping = ta_columns.pos_neg_columns_mapping(lookback, fun.__name__)

    click.echo("Running market breadth function 'hilo")
    t0 = datetime.datetime.now()
    res = internals.breadth(df_list, int(lookback), start_date, end_date, fun)
    logger.info("Function 'hilo' completed in {}".format(datetime.datetime.now() - t0))

    if plot_vs_df is not None:
        plot_vs = plot_vs_df['Ticker'][0]
        plot_vs_df = pd.DataFrame(plot_vs_df['Close']).rename(columns={'Close': plot_vs})
        plot_data = res[[column_mapping['neg_pct'], column_mapping['pos_pct']]]
        plot_data = plot_data[(plot_data > 0)]  # Skip all zero data points
        df = pd.concat([plot_vs_df, plot_data], axis=1, join='inner')

        plot_title = "% of Stocks at {:d}-Day Highs/Lows".format(lookback)
        do_plot(df, plot_vs, column_mapping['neg_pct'], column_mapping['pos_pct'],
                plot_pct_levels, plot_title)

    else:
        click.echo(res[-lookback:])


@click.command(options_metavar='<options>')
@click.argument('function', metavar="<function>", type=click.STRING)
@click.argument('lookback', metavar="<lookback>", type=click.INT)
@click.option('--start', default="2010-01-01", help='starting date.')
@click.option('--end', default="today", help='ending date')
@click.option('--tickers', default=False, help='Comma separated list of tickers')
@click.option('--file', type=click.Path(exists=True), help="Read tickers from file")
@click.option('--provider', type=click.Choice(AVAILABLE_PROVIDERS),
              default='google',
              help='Default is "google".See qa-dataprovider lib for more info'.format(AVAILABLE_PROVIDERS))
@click.option('--plot-vs', type=click.STRING, help='Which Stock/ETF to visualize breadth, e.g. \'SPY\'')
@click.option('--plot-pct-levels', default='20,30,40', type=click.STRING,
              help='Comma separated list, e.g. \'75,90\' to visulize when 75% and 90% of stocks making 20-Day highs/lows')
@click.option('-v', '--verbose',count=True, help="'v' for INFO (default). 'vv' for DEBUG.")
def main(function, lookback, start, end, tickers, file, provider, plot_vs, plot_pct_levels, verbose):
    """
    Tool for analyzing and plotting market internals

    <lookback>: Integer to specify lookback period

    <function>: Available analysis methods

    'hilo': to calculate number of stocks at X-day highs/lows.

    'dma': calculate number of stocks below/above any moving average.

    """
    context = Context(start, end, tickers, file, provider, verbose)
    df_list = context.data_frames

    click.echo("Fetching data for {:d} tickers".format(len(df_list)))
    
    plot_vs_df = None
    if plot_vs:
        plot_vs_df = context.data_provider.get_data([plot_vs], from_date=context.start_date,
                                                    to_date=context.end_date)[0]
    if function == 'hilo':
        hilo_analysis(lookback, context.start_date, context.end_date, df_list, plot_vs_df, plot_pct_levels.split(","))

    if function == 'dma':
        # Similar to SPXA50R http://stockcharts.com/h-sc/ui?s=$SPXA50R
        dma_analysis(lookback, context.start_date, context.end_date, df_list, plot_vs_df, plot_pct_levels.split(","))

    if context.data_provider.errors > 0:
        logger.warning("Missing data for {:d} tickers.".format(provider.errors))


if __name__ == '__main__':
    main()
