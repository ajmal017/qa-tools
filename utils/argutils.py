import datetime

import click


def get_tickers(file):
    with open(file) as f:
        return [ticker.rstrip() for ticker in f.readlines()]


# TODO: move to qa_tools.utils
def parse_dates(start, end):
    """
    Parse and verify dates and return as string

    :param start: String with date on standard format
    :param end: String with date on standard format or 'today' to generate correct string format
    :return: Tuple with Strings, e.g. ('2016-12-10','2016-12-31')
    """
    if end is 'today':
        end_datetime = datetime.datetime.now().strftime('%Y-%m-%d')
    else:
        end_datetime = datetime.datetime.strptime(end, '%Y-%m-%d').strftime('%Y-%m-%d')

    start_datetime = datetime.datetime.strptime(start, '%Y-%m-%d').strftime('%Y-%m-%d')

    return start_datetime, end_datetime


def tickers_list(file, tickers):
    """
    Return a list of tickers from file or comma separated list
    
    :param file: 
    :param tickers: 
    :return: 
    """
    if file:
        return get_tickers(file)
    else:
        if not tickers:
            raise Exception("Must provide list of tickers or tickers file")
        else:
            return tickers.split(",") #TODO: strip spaces from each string token


def float_range(ctx, param, value):
    if 1.0 >= value >= 0.0:
        return value
    raise click.BadParameter('Risk: 0 <= 1')
