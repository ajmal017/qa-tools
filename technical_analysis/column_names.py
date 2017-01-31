def ma_name(lookback):
    return "{n}DMA".format(n=lookback)

def ma_slope_name(lookback):
    return "{n}DMA_SLOPE".format(n=lookback)

def day_high_name(lookback):
    return "DAY_HIGH_{n}".format(n=lookback)

def day_low_name(lookback):
    return "DAY_LOW_{n}".format(n=lookback)

def day_high_perc_name(lookback):
    return "DAY_HIGH_PERC_{n}".format(n=lookback)

def day_low_perc_name(lookback):
    return "DAY_LOW_PERC_{n}".format(n=lookback)

def above_dma_name(lookback):
    return "ABOVE_{n}DMA".format(n=lookback)

def below_dma_name(lookback):
    return "BELOW_{n}DMA".format(n=lookback)