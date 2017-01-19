#!/usr/bin/python

import matplotlib.pyplot as plt
import pandas as pd
from dataprovider.web_dataprovider import WebDataprovider

BUCKET_SIZE = 0.5

def usage():
    print("./strikes.py --strike-size 0.5 --direction short --round up")


def strikes():
    # TODO:
    # 1. Load weekly data, e.g. SVXY
    # 2. For each week:
    #   - how many strikes above or below does this week close from last week
    #   - SVXY: should be like at most 1 strike below like 20-30% of weeks
    # 3. plot number of strikes, X, below or above last weeks close.
    pass



def find_nearest_strike(number,strike_size):
    n = int(number)
    while (n < number):
        n += strike_size
    return n

def find_nearest_itm_strike(number,strike_size):
    n = int(number)+1
    while (n > number):
        n -= strike_size
    return n

def calculate(diff):
    if diff < 0:
        s = find_nearest_itm_strike(diff, BUCKET_SIZE)
    else:
        s = find_nearest_strike(diff, BUCKET_SIZE)
    return s

def get_stats(data):
    neg = pos = avg = avg_ceiling = 0
    close_list = []
    stats = {}

    for index, row in data.iterrows():
        close_list.append(row['Close'])
        diff = float(row["Close"]) - float(row["Open"])
        if diff <= 0.0:
            neg += 1
        else:
            avg += diff
            avg_ceiling += min(diff,1)
            pos += 1

    stats['o2c'] = {"neg": neg, "pos":pos, "avg":avg/float(len(data)), "avg_ceil": avg_ceiling/float(len(data))}

    pos2 = 0
    neg2 = 0
    for i in range(0,len(close_list)-1):
        close_current_week = close_list[i+1]
        close_last_week = close_list[i]

        if float(close_current_week) - float(close_last_week) <= 0.0:
            neg2 += 1
        else:
            pos2 += 1

    stats['c2c'] = {"neg": neg2, "pos": pos2}
    print(stats)
    return stats


def calculate_bucket(data):
    itm_strikes = []
    otm_strikes = []
    o2c_strikes = []

    for week in data:
        closest_otm_strike = find_nearest_strike(week['Open'], BUCKET_SIZE)
        closest_itm_strike = find_nearest_itm_strike(week['Open'], BUCKET_SIZE)

        o2c_strikes.append(calculate(week['Close']-week['Open']))
        itm_strikes.append(calculate(week['Close'] - closest_itm_strike))
        otm_strikes.append(calculate(week['Close'] - closest_otm_strike))
        #print(itm_strikes)
        #print(otm_strikes)

    #df = pd.DataFrame(o2c_strikes)
    #df = pd.DataFrame(itm_strikes)

    df = pd.DataFrame({'o2c': o2c_strikes, 'itm': itm_strikes, 'otm': otm_strikes}, columns=['o2c','itm','otm'])
    print(df.describe())
    df.plot.hist(alpha=0.5,bins=250)
    plt.show()


    #plt.show(block=True)


def test_get_stats():
    #df = pd.DataFrame({"Open": [], "High": [], "Low": [], "Close": []})

    df = pd.DataFrame(pd.DataFrame({"Open": 10.0, "High": 11.0, "Low": 9.0, "Close": 10.5}, index=[0])) # W1
    df = df.append(pd.DataFrame({"Open": 11.0, "High": 12.0, "Low": 10.0, "Close": 11.5}, index=[0])) # W2
    df = df.append(pd.DataFrame({"Open": 11.0, "High": 11.5, "Low": 9.0, "Close": 10.6}, index=[0]))  # W3

    n = len(df)
    stats = get_stats(df)

    assert stats['o2c']['neg'] == 1
    assert stats['o2c']['pos'] == 2
    assert stats['c2c']['pos'] == 1
    assert stats['c2c']['neg'] == 1

    # print("Weekly O2C:")
    # print("Neg: %d/%d = %f" % (stats['o2c']['neg'], n, stats['o2c']['neg'] / float(n)))
    # print("Pos: %d/%d = %f" % (stats['o2c']['pos'], n, stats['o2c']['pos'] / float(n)))
    #
    # print("Weekly C2C:")
    # print(
    #     "Neg: %d/%d = %f" % (stats['c2c']['neg'], n - 1, stats['c2c']['neg'] / float(n - 1)))
    # print(
    #     "Pos: %d/%d = %f" % (stats['c2c']['pos'], n - 1, stats['c2c']['pos'] / float(n - 1)))

def test_strikes():
    assert 22 == find_nearest_strike(21.6, 0.5)
    assert 21.5 == find_nearest_strike(21.4, 0.5)

    assert 21 == find_nearest_itm_strike(21.4, 0.5)
    assert 21.5 == find_nearest_itm_strike(21.9, 0.5)

    assert -0.5 == find_nearest_itm_strike(-0.1, 0.5)
    assert -0.5 == find_nearest_itm_strike(-0.5, 0.5)
    assert 0.5 == find_nearest_strike(0.1, 0.5)
    assert 1.5 == find_nearest_strike(1.1, 0.5)

if __name__ == '__main__':
    """
    Observations:
        1. Friday close to next fridays close seems a little bit better than O2C (61% instead of 60% wins)
        2. Average loss is probably closer to 0,3 ($30) and not always max loss
        3. It seems like edge is far less for selling nearest ITM.
           The mean of all ITM strikes is 0,26 vs -0.27 for nearest OTM, i.e. nearest ITM option is more likely to close ITM than OTM!

    """

    #test_strikes()
    #test_get_stats()

    #buckets = calculate_bucket([{"open":21.6,"close":21.5},{"open":22.1, "close":21.8}, {"open":25, "close":24.8}, {"open":25, "close":27.5}]
    #data = get_data("/Users/fbjarkes/Dropbox/tickdata_weekly/NYSF_VXX.txt")

    provider = WebDataprovider()
    data = provider.get_data("VXX","2010-01-01","2016-12-31",timeframe="week", provider='yahoo')
    converted = []

    for index, row in data.iterrows():
        #print(index," Open=",row['Open'], " Close=",row["Close"])
        #print("index=",index.isoformat())

        converted.append({"Open":float(row["Open"]), "Close": float(row["Close"])})
        #print("%s: %f to %f => O2C=%f" % (index.isoformat(),row["Open"],row["Close"],(row["Close"]-row["Open"])))

    stats = get_stats(data)
    print("Weekly O2C:")
    print("Neg: %d/%d = %f" % (stats['o2c']['neg'], len(converted), stats['o2c']['neg']/float(len(converted))))
    print("Pos: %d/%d = %f" % (stats['o2c']['pos'], len(converted), stats['o2c']['pos']/float(len(converted))))
    print("Avg: %f" % (stats['o2c']['avg']))
    print("Avg (max 1): %f" % (stats['o2c']['avg_ceil'])) # This assumes an OTM strike is sold from official VXX opening price
    print("")
    print("Weekly C2C:")
    print("Neg: %d/%d = %f" % (stats['c2c']['neg'], len(converted)-1, stats['c2c']['neg'] / float(len(converted)-1)))
    print("Pos: %d/%d = %f" % (stats['c2c']['pos'], len(converted)-1, stats['c2c']['pos'] / float(len(converted)-1)))

    calculate_bucket(converted)
