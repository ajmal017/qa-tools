#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import logging as logger

import matplotlib.pyplot as plt

from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.dates as mdates



import click
import pandas as pd

from dataprovider.dataprovider import CachedDataProvider
from technical_analysis import seasonality

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')

# https://ismayc.github.io/moderndiver-book/4-viz.html
# Facets: per month

@click.command(options_metavar='<options>')
@click.option('--start', type=click.STRING, help='Starting year, e.g. \'2005-01-01\'')
@click.option('--end', type=click.STRING, help='Ending year, e.g. \'2015-12-31\'')
@click.option('--ticker', default=False, help='Ticker to analyze, e.g. \'SPY\'')
@click.option('--provider',type=click.Choice(['yahoo', 'google']), default='google')
@click.option('--plot-vs', type=click.STRING, help='Which Stock/ETF to visualize in same plot, e.g. \'SPY\'')
@click.option('--plot-facets', type=click.BOOL, help='Plot monthly facets')
@click.option('--plot-label', type=click.Choice(['day', 'month']), default='month',
              help='Label for x-axis. Use \'Day\' for trading day of year')
#TODO: skip regime?
#@click.option('--market-regime', type=click.Choice(['bull', 'bear','both']), default='both',
#              help='Filter seasonality based on market regime, i.e. 200DMA bull/bear filter.')
def seasonality_analysis(ticker, provider, start, end, plot_vs, plot_label, plot_facets):
    click.echo("Seasonality for {0}".format(ticker))

    data_provider = CachedDataProvider(cache_name='seasonality', expire_days=0)
    df = data_provider.get_data(ticker, start, end, provider=provider)

    plot_data = seasonality.seasonality_returns(df).apply(seasonality.rebase)

    fig, ax = plt.subplots()
    if plot_label == 'month':
        ax.plot(plot_data, label="{0} {1}-{2}".format(ticker,df.index[0].year,df.index[-1].year))
        #months = mdates.MonthLocator()  # every month
        yearsFmt = mdates.DateFormatter('%b')
        ax.xaxis.set_major_formatter(yearsFmt)
        #ax.xaxis.set_minor_locator(months)
        days = mdates.DayLocator()
        ax.xaxis.set_minor_locator(days)
        fig.autofmt_xdate()
        title = "{0} Seasonality".format(ticker)

        if plot_vs:
            plot_vs_start = "{0}-01-01".format(datetime.datetime.now().year)
            plot_vs_end = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
            plot_vs_df = data_provider.get_data(ticker, plot_vs_start, plot_vs_end, provider=provider)['Close']

            new_series = plot_vs_df.values
            new_index = plot_data.index[0:len(plot_vs_df)]
            col = "{0} until {1}".format(ticker, plot_vs_end)
            df = pd.DataFrame(new_series, index=new_index, columns=[col])
            df = seasonality.normalize(df).apply(seasonality.rebase)
            ax.plot(df, label=col)

            minorLocator = MultipleLocator(1)
            ax.xaxis.set_minor_locator(minorLocator)
            title = "{0} Seasonality vs {0}".format(ticker)

    elif plot_label == 'day':
        days = range(1,len(plot_data)-1)
        plot_data_days = pd.DataFrame({ticker:plot_data[ticker].values}).reindex(days)
        plot_data_days = seasonality.normalize(plot_data_days).apply(seasonality.rebase_days)
        ax.plot(plot_data_days, label="{0} {1}-{2}".format(ticker,df.index[0].year,df.index[-1].year))

        minorLocator = MultipleLocator(1)
        ax.xaxis.set_minor_locator(minorLocator)
        ax.set_xlabel("trading day")
        title = "{0} Seasonality".format(ticker)

        if plot_vs:
            plot_vs_start = "{0}-01-01".format(datetime.datetime.now().year)
            plot_vs_end = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
            plot_vs_df = data_provider.get_data(ticker, plot_vs_start, plot_vs_end, provider=provider)['Close']

            vs_days = range(1, len(plot_vs_df) - 1)
            df = pd.DataFrame({ticker:plot_vs_df.values}).reindex(vs_days)

            df = seasonality.normalize(df).apply(seasonality.rebase_days)
            col = "{0} until {1}".format(ticker, plot_vs_end)
            ax.plot(df, label=col)
            title = "{0} Seasonality vs {0}".format(ticker)


    legend = ax.legend(loc='upper left', shadow=False, fontsize=12)
    plt.title(title)
    plt.show()

if __name__ == '__main__':
    #seasonality_analysis("SPY","google","2000-01-01","2016-12-31","SPY","day","both")
    seasonality_analysis()
