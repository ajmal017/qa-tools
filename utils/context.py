#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import utils.logger as log_handler
import logging

from qa_dataprovider.web_dataprovider import CachedWebDataProvider
from qa_dataprovider.csv_dataprovider import CsvFileDataProvider
from qa_dataprovider import Factory
from utils import argutils


class Context:

    logger = logging.getLogger(__file__)

    @property
    def data_frames(self):
        return self._data_frames

    @property
    def data_provider(self):
        return self._data_provider

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @property
    def get_quotes(self):
        return self._get_quotes

    def __init__(self, start, end, tickers, file, provider, verbose, timeframe='day',
                 max_workers=10, clear_cache=False):
        if verbose == 1:
            log_handler.set_info()
        if verbose == 2:
            log_handler.set_debug()

        self._start_date, self._end_date, self._get_quotes = argutils.parse_dates(start, end)
        tickers = argutils.tickers_list(file, tickers)

        self.logger.info("Fetching {} tickers".format(len(tickers)))

        self._data_provider = Factory.make_provider(provider, clear_cache=clear_cache, get_quotes=self._get_quotes)

        # if provider == 'ib':
        #     self._dataprovider = IBDataProvider(expire_days=0, clear_cache=clear_cache)
        #
        # elif provider == 'quandl':
        #     self._data_provider = CsvFileDataProvider(
        #         [
        #             '../../quandl/iwm',
        #             '../quandl/iwm',
        #             '../../quandl/spy',
        #             '../quandl/spy',
        #             '../../quandl/ndx',
        #             '../quandl/ndx'
        #         ])
        #
        # elif provider == 'infront':
        #     self._data_provider = CsvFileDataProvider(
        #         [
        #             '../../infront',
        #             '../infront'
        #         ],
        #         prefix=['NSQ','NYS','NYSF','SSE']
        #     )
        #
        # elif provider == 'nasdaq':
        #     self._data_provider = CsvFileDataProvider(
        #         [
        #             '../../nasdaq',
        #             '../infront'
        #         ])
        #
        # elif provider == 'stooq':
        #     self._data_provider = CsvFileDataProvider(
        #         [
        #             '../../stooq',
        #             '../stooq'
        #         ])
        #
        # elif provider == 'sql':
        #     raise Exception("Not implemented yet")
        #
        # elif provider == 'ig':
        #     raise Exception("Not implemented yet")
        #
        # else:
        #     self._data_provider = CachedWebDataProvider(provider, expire_days=0, quote=get_quotes)
        #
        self._data_frames = self._data_provider.get_data(tickers, self._start_date, self._end_date, max_workers=max_workers)





