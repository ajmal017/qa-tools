# content of conftest.py
import pytest
from dataprovider.local_dataprovider import TestDataprovider

@pytest.fixture(scope="module")
def local_provider():
    return TestDataprovider