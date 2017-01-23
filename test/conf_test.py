# content of conftest.py
import pytest
from dataprovider.local_dataprovider import LocalDataprovider

@pytest.fixture(scope="module")
def local_provider():
    return LocalDataprovider