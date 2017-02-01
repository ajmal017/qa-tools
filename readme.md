

## Installation
```
$ git clone ....
$ virtualenv ... 
$ pip3 install -r requirements.txt
```

## Tools
#### Market breadth

Examples:

Market breadth from 2016-12-01 until today for all SP500 stocks:
```
$ python3 market_breadth.py --start 2016-12-01 --file sp500.txt hilo 20 --provider=yahoo
```
