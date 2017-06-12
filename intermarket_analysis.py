#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import datetime
import logging as logger

import matplotlib.pyplot as plt
import click
import pandas as pd
import ffn

from qa_dataprovider.web_dataprovider import CachedWebDataProvider
from utils import argutils
from technical_analysis import ta

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')


@click.command()
@click.argument('function', metavar="<function>", type=click.STRING)
@click.option('--start', type=click.STRING, default="2010-01-01", help='starting date.',
              required=True)
@click.option('--end', type=click.STRING, default="today", help='ending date')
@click.option('--tickers', default=False, help='Comma separated list of tickers')
@click.option('--file', type=click.Path(exists=True), help="Read tickers from file")
@click.option('--provider', type=click.Choice(['yahoo', 'google']), default='google')
def main(function, start, end, tickers, file, provider):
    """Simple tool (based on https://github.com/pmorissette/ffn) for intermarket analysis.

    <function>: Available analysis methods:
    
    'average': display average combined returns

    'heat': display correlations heatmap

    'scatter': display scatter matrix

    """

    start_date, end_date, get_quotes = argutils.parse_dates(start, end)
    tickers = argutils.tickers_list(file, tickers)

    click.echo("Fetching data for {0} tickers".format(len(tickers)))

    data_provider = CachedWebDataProvider(provider, expire_days=0, quote=get_quotes)
    df_list = data_provider.get_data(tickers, start_date, end_date, max_workers=10)

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

    if data_provider.errors > 0:
        logger.warning("Missing data for {0} tickers.".format(provider.errors))


if __name__ == '__main__':
    main()
