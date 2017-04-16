#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import datetime
import logging as logger

import matplotlib.pyplot as plt
import click
import pandas as pd
import ffn

from dataprovider.dataprovider import CachedDataProvider

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')


def get_tickers(file):
    with open(file) as f:
        return [ticker.rstrip() for ticker in f.readlines()]


@click.command()
@click.option('--start', type=click.STRING, default="2010-01-01", help='starting date.', required=True)
@click.option('--end', type=click.STRING, default="today", help='ending date')
@click.option('--tickers', default=False, help='Comma separated list of tickers')
@click.option('--file', type=click.Path(exists=True), help="Read tickers from file")
@click.option('--provider', type=click.Choice(['yahoo', 'google']), default='google')
@click.option('--quotes', is_flag=True,
              help='Add intraday (possibly delayed) quotes, e.g. for analyzing during market opening hours')
def main(start, end, tickers, file, provider, quotes):
    """Simple tool (based on https://github.com/pmorissette/ffn) for inter market analysis."""

    if end is 'today':
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    else:
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d').strftime('%Y-%m-%d')

    start_date = datetime.datetime.strptime(start, '%Y-%m-%d').strftime('%Y-%m-%d')

    if file:
        tickers = get_tickers(file)
    else:
        if not tickers:
            raise Exception("Must provide list of tickers or tickers file")
        else:
            tickers = tickers.split(",")

    click.echo("Fetching data for {0} tickers".format(len(tickers)))

    data_provider = CachedDataProvider(cache_name='intermarket', expire_days=0, quote=quotes)
    df_list = data_provider.get_data_parallel(tickers, from_date=start_date, to_date=end_date,
                                              provider=provider, max_workers=10)
    closes = []
    for df in df_list:
        closes.append(df['Close'].rename(df['Ticker'][0]))

    # TODO: plot rebased etc??
    # g = ffn.GroupStats(df_list[0]['Close'], df_list[1]['Open'])
    g = ffn.GroupStats(*closes)
    g.plot_correlation()
    # g.plot()

    plt.show()

    if data_provider.errors > 0:
        logger.warning("Missing data for {0} tickers.".format(provider.errors))


if __name__ == '__main__':
    main()
