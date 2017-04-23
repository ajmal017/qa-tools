def ma_name(lookback):
    return "{0}DMA".format(lookback)


def ma_slope_name(lookback):
    return "{0}DMA_SLOPE".format(lookback)


def day_high_name(lookback):
    return "DAY_HIGH_{0}".format(lookback)


def day_low_name(lookback):
    return "DAY_LOW_{0}".format(lookback)


def day_high_pct_name(lookback):
    return "% {:d}-day highs".format(lookback)


def day_low_pct_name(lookback):
    return "% {:d}-day lows".format(lookback)


def above_dma_name(lookback):
    return "ABOVE_{0}DMA".format(lookback)


def below_dma_name(lookback):
    return "BELOW_{0}DMA".format(lookback)


def above_dma_pct_name(lookback):
    return "% above {:d}-DMA".format(lookback)


def below_dma_pct_name(lookback):
    return "% below {:d}-DMA".format(lookback)


def atr_name(lookback):
    return "{0}-ATR".format(lookback)


def rocp_name(lookback):
    return "{0}-ROC_PCT".format(lookback)


def pos_neg_columns_mapping(lookback, function):
    if function == 'hilo':
        return {
            'pos': day_high_name(lookback),
            'pos_pct': day_high_pct_name(lookback),
            'neg': day_low_name(lookback),
            'neg_pct': day_low_pct_name(lookback)
        }

    if function == 'dma':
        return {
            'pos': above_dma_name(lookback),
            'pos_pct': above_dma_pct_name(lookback),
            'neg': below_dma_name(lookback),
            'neg_pct': below_dma_pct_name(lookback)
        }
