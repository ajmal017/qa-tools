#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import datetime
import logging as logger

import matplotlib
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator

try:
    import tkinter  # should fail on AWS images with no GUI available
    import matplotlib.pyplot as plt
except:
    print("Warning: tkinter package not installed?", sys.exc_info()[0])
    print(sys.exc_info()[1])
    matplotlib.use('Agg')

import click
import pandas as pd

from qa_dataprovider.web_dataprovider import CachedWebDataProvider
from technical_analysis import seasonality

logger.basicConfig(level=logger.INFO, format='%(filename)s: %(message)s')


@click.command(options_metavar='<options>')
@click.option('--start', type=click.STRING, help='Starting year, e.g. \'2005-01-01\'',
              default='2010-01-01')
@click.option('--end', type=click.STRING, help='Ending year, e.g. \'2015-12-31\'',
              default='2016-12-31')
@click.option('--ticker', default=False, help='Ticker to analyze, e.g. \'SPY\'')
@click.option('--provider', type=click.Choice(['yahoo', 'google']), default='google')
@click.option('--plot-vs', type=click.STRING, help='Which Stock/ETF to visualize in same plot, e.g. \'SPY\'')
@click.option('--monthly', is_flag=True, help='Subplot seasonality per month')
@click.option('--plot-label', type=click.Choice(['day', 'calendar']), default='calendar',
              help='Label for x-axis. Use \'Day\' for trading day of year')
def seasonality_analysis(ticker, provider, start, end, plot_vs, plot_label, monthly):
    click.echo("Seasonality for {0}".format(ticker))

    data_provider = CachedWebDataProvider(provider, expire_days=0)
    df = data_provider.get_data([ticker], start, end)[0]

    if monthly:
        rebased_dataframes = [df for df in seasonality.seasonality_monthly_returns(df)]

        fig = plt.figure()
        fig.suptitle("{0} montly seasonality".format(ticker), fontsize=16)
        for i, data in enumerate(rebased_dataframes):
            ax = fig.add_subplot(4, 3, i + 1)
            ax.plot(data)
            ax.set_title(data.columns[0])
            # ax.set_xticks(data.index)
            ax.set_yticks([])

        plt.tight_layout()
        plt.show()

    else:
        seasonlity_data = seasonality.seasonality_returns(df).apply(seasonality.rebase)

        fig, ax = plt.subplots()
        if plot_label == 'calendar':
            ax.plot(seasonlity_data, label="{0} {1}-{2}".format(ticker, df.index[0].year, df.index[-1].year))
            # months = mdates.MonthLocator()  # every month
            yearsFmt = mdates.DateFormatter('%b')
            ax.xaxis.set_major_formatter(yearsFmt)
            # ax.xaxis.set_minor_locator(months)
            days = mdates.DayLocator()
            ax.xaxis.set_minor_locator(days)
            fig.autofmt_xdate()
            title = "{0} Seasonality".format(ticker)

            if plot_vs:
                plot_vs_start = "{0}-01-01".format(datetime.datetime.now().year)
                plot_vs_end = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
                plot_vs_df = data_provider.get_data(plot_vs, plot_vs_start, plot_vs_end, provider=provider)['Close']

                # Reindex the the plot_vs data to seasonality_data datetimes
                new_index = seasonlity_data.index[0:len(plot_vs_df)]
                col = "{0} until {1}".format(plot_vs, plot_vs_end)
                df = pd.DataFrame(plot_vs_df.values, index=new_index, columns=[col])
                df = seasonality.normalize(df).apply(seasonality.rebase)

                ax.plot(df, label=col)

                minorLocator = MultipleLocator(1)
                ax.xaxis.set_minor_locator(minorLocator)
                title = "{0} Seasonality vs {0}".format(ticker)

        elif plot_label == 'day':
            # days = range(1,len(plot_data)-1)
            # plot_data_days = pd.DataFrame({ticker:plot_data[ticker].values}).reindex(days)

            seasonality_data_days = seasonality.trading_day_reindex(seasonlity_data, ticker, ticker)
            seasonality_data_days = seasonality.normalize(seasonality_data_days).apply(seasonality.rebase_days)
            ax.plot(seasonality_data_days, label="{0} {1}-{2}".format(ticker, df.index[0].year, df.index[-1].year))

            minorLocator = MultipleLocator(1)
            ax.xaxis.set_minor_locator(minorLocator)
            ax.set_xlabel("trading day")
            title = "{0} Seasonality".format(ticker)

            if plot_vs:
                plot_vs_start = "{0}-01-01".format(datetime.datetime.now().year)
                plot_vs_end = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
                plot_vs_df = data_provider.get_data(plot_vs, plot_vs_start, plot_vs_end, provider=provider)

                df = seasonality.trading_day_reindex(plot_vs_df, ticker, 'Close')
                df = seasonality.normalize(df).apply(seasonality.rebase_days)
                col = "{0} until {1}".format(plot_vs, plot_vs_end)
                ax.plot(df, label=col)
                title = "{0} Seasonality vs {0}".format(ticker)

        legend = ax.legend(loc='upper left', shadow=False, fontsize=12)
        plt.title(title)
        plt.show()


if __name__ == '__main__':
    # seasonality_analysis("SPY","google","2000-01-01","2016-12-31","","day",True)
    seasonality_analysis()
