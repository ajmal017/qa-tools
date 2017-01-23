
from dataprovider.web_dataprovider import WebDataprovider


class LocalDataprovider(WebDataprovider):
    def __init__(self):
        super(LocalDataprovider,self).__init__(cache_name='test_data',expire_days=None)