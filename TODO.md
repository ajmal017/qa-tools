#### TODO: seasonality_analysis.py:
* Accept file with tickers and save figure with plot-vs for each ticker


#### TODO: technical_analysis/market_internal.py
* use ffn.utils.memoize for all intensive functions
* https://github.com/shaypal5/cachier
* https://github.com/joblib/joblib
* Click progress bar


#### TODO: technical_analysis/weekly_tight_range.py:
* Finalize cmdline analysis with statistics
* Make general methods
* Add RVOL, ADV, etc. according to original rules


#### TODO: monter_carlo_analysis.py:
* Use bootstrap https://github.com/facebookincubator/bootstrapped with all equity curves to estimate with 95%
* Simulate trades by reshuffling order
* Estimate the mean performance using bootstrap vs. just taking the mean of performances
* Generate equity curves, i.e. 1000 performance values
    * Plot histogram
    * Plot cumulative distribution, Mark where 95% of all performances are higher than


#### TODO: technical_analysis/ehlers.py
* super smoother
* cycle analysis
* high pass filter


#### TODO: market_breadth_analysis.py:
* Extend plot into future to better visualize most recent hilo value
* Add subplots to visualize hilo 20 historical values


#### TODO: intermarket_analysis.py


#### TODO:
* in-sample returns vs out of sample returns:
    * scatter plot and regress is vs oos

   
#### TODO:
* ipynb in examples folder instead of examples in readme.md (http://nbviewer.jupyter.org/github/bpsmith/tia/blob/master/examples/backtest.ipynb)
  
   
#### TODO: spp
* http://www.statistrade.com/support-files/spp_wagner_award_2014_dave_walton.pdf
* system parameter permutation
* http://bettersystemtrader.com/system-parameter-permutation-a-better-alternative/

