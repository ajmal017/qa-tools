#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import logging as logger

import datetime

import matplotlib.pyplot as plt
import click
import pandas as pd
import ffn

from qa_dataprovider.web_dataprovider import CachedWebDataProvider
from qa_dataprovider import AVAILABLE_PROVIDERS
from utils import argutils
from technical_analysis import ta
from utils.context import Context


@click.command()
@click.argument('function', metavar="<function>", type=click.STRING)
@click.option('--start', type=click.STRING, default="2010-01-01",
              help='starting date. Default '"2010-01-01", required=True)
@click.option('--end', type=click.STRING, default="today", help='ending date. Default "today"')
@click.option('--tickers', default=False, help='Comma separated list of tickers')
@click.option('--file', type=click.Path(exists=True), help="Read tickers from file")
@click.option('--provider', type=click.Choice(AVAILABLE_PROVIDERS),
              default='google',
              help='Default is "google".See qa-dataprovider lib for more info'.format(AVAILABLE_PROVIDERS))
@click.option('-v', '--verbose',count=True, help="'v' for INFO (default). 'vv' for DEBUG.")
def main(function, start, end, tickers, file, provider, verbose):
    """Simple tool (based on https://github.com/pmorissette/ffn) for intermarket analysis.

    <function>: Available analysis methods:
    
    'average': display average combined returns

    'heat': display correlations heatmap

    'scatter': display scatter matrix

    """
    context = Context(start, end, tickers, file, provider, verbose)
    df_list = context.data_frames

    if len(df_list) < 1:
        click.echo("No dataframes. Exiting.")
        return

    closes = []
    for df in df_list:
        closes.append(df['Close'].rename(df['Ticker'][0]))

    if function == 'heat':
        g = ffn.GroupStats(*closes)
        g.plot_correlation()
        plt.show()

    elif function == 'scatter':
        g = ffn.GroupStats(*closes)
        axes = g.plot_scatter_matrix()
        plt.show()

    elif function == 'average':
        col = "Close"
        tickers = "Average: " + ", ".join([df['Ticker'][0] for df in df_list])
        rebased_merged = ffn.core.merge(*[ffn.core.rebase(c) for c in closes])

        average = pd.DataFrame(columns=[col])
        for index, row in rebased_merged.iterrows():
            average.set_value(index, col, row.values.mean())

        average = ta.add_ma(average, 200)

        average.plot()
        plt.title(tickers)
        plt.show()

    else:
        click.echo("{:s} not recognized".format(function))

    if context.data_provider.errors > 0:
        logger.warning("Missing data for {0} tickers.".format(provider.errors))


if __name__ == '__main__':
    main()
