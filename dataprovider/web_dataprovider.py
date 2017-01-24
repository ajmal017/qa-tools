from datetime import datetime, timedelta

import time
import pandas as pd
import requests_cache
import pandas_datareader.data as web

class WebDataprovider:
    """
    """

    def __init__(self, cache_name='cache', expire_days=3):
        expire_after = (None if expire_days is (None or 0) else timedelta(days=expire_days))

        self.session = requests_cache.CachedSession(cache_name=cache_name, backend='sqlite', expire_after=expire_after)

    def get_data(self,ticker, from_date, to_date, timeframe='day', provider='google'):
        # TODO: info log
        # TODO: log cache usage
        print("%s: %s to %s, provider=%s, cached=%s" % (ticker, from_date, to_date, provider, self.session))
        #data = web.DataReader(ticker, provider, start=datetime(2013,1,1),
        #                      end=datetime(2016,12,31),
        #                      session=self.session)
        start = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d")
        data = web.DataReader(ticker, provider, start=start, end=end, session=self.session,pause=1)

        # From: http://blog.yhat.com/posts/stock-data-python.html
        transdat = data.loc[:, ["Open", "High", "Low", "Close"]]
        if timeframe == 'week':
            transdat["week"] = pd.to_datetime(transdat.index).map(lambda x: x.isocalendar()[1]) # Identify weeks
            transdat["year"] = pd.to_datetime(transdat.index).map(lambda x: x.isocalendar()[0])

            grouped = transdat.groupby(list(set(["year","week"]))) # Group by year and other appropriate variable
            dataframes = pd.DataFrame({"Open": [], "High": [], "Low": [], "Close": []})
            for name, group in grouped:
                df = pd.DataFrame({"Open": group.iloc[0,0],"High": max(group.High), "Low": min(group.Low),"Close": group.iloc[-1,3]},index = [group.index[0]])
                dataframes = dataframes.append(df)

            sorted = dataframes.sort_index()
            #print(sorted)
            return sorted
        else:
            return transdat


