#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import datetime
import logging as logger

import matplotlib.pyplot as plt
import click
import pandas as pd
import ffn


from qa_dataprovider.web_dataprovider import CachedDataProvider
from utils import argutils

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')


@click.command()
@click.argument('function', metavar="<function>", type=click.STRING)
@click.option('--start', type=click.STRING, default="2010-01-01", help='starting date.', required=True)
@click.option('--end', type=click.STRING, default="today", help='ending date')
@click.option('--tickers', default=False, help='Comma separated list of tickers')
@click.option('--file', type=click.Path(exists=True), help="Read tickers from file")
@click.option('--provider', type=click.Choice(['yahoo', 'google']), default='google')
@click.option('--quotes', is_flag=True,
              help='Add intraday (possibly delayed) quotes, e.g. for analyzing during market opening hours')
def main(function, start, end, tickers, file, provider, quotes):
    """Simple tool (based on https://github.com/pmorissette/ffn) for inter market analysis.

    <function>: Available analysis methods:

    'heat': display correlations heatmap

    'scatter': display scatter matrix

    """

    start_date, end_date = argutils.parse_dates(start, end)
    tickers = argutils.tickers_list(file, tickers)

    click.echo("Fetching data for {0} tickers".format(len(tickers)))

    data_provider = CachedDataProvider(cache_name='intermarket', expire_days=0, quote=quotes)
    df_list = data_provider.get_data_parallel(tickers, from_date=start_date, to_date=end_date,
                                              provider=provider, max_workers=10)


    closes = []
    for df in df_list:
        closes.append(df['Close'].rename(df['Ticker'][0]))

    #for c in closes:
    #    for index, item in c.iteritems():
    #        print(index,item)

    # TODO: plot rebased etc??
    if function == 'heat':
        # g = ffn.GroupStats(df_list[0]['Close'], df_list[1]['Open'])
        g = ffn.GroupStats(*closes)
        g.plot_correlation()
        # g.plot()
        plt.show()

    elif function == 'scatter':
        g = ffn.GroupStats(*closes)

        #df.corr()
        #corr = df['Close'].corr().as_matrix()
        axes = g.plot_scatter_matrix()
        #for i, j in zip(*plt.np.triu_indices_from(axes, k=1)):
        #    axes[i, j].annotate("%.3f" % corr[i, j], (0.8, 0.8), xycoords='axes fraction', ha='center', va='center')
        plt.show()

    elif function == 'plot':
        g = ffn.GroupStats(*closes)

        g.plot()
        plt.show()

    else:
        click.echo("{:s} not recognized".format(function))

    if data_provider.errors > 0:
        logger.warning("Missing data for {0} tickers.".format(provider.errors))


if __name__ == '__main__':
    main()
