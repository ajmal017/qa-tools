#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import random

import pandas as pd
import click
import matplotlib.pyplot as plt
import ffn

"""

For the first test, I assumed an account size of $2,500.00.
I ran the Monte Carlo test using Build Alpha which created 1,000 new drawdowns and the picture below.
For example, the first Monte Carlo run (1 of 1000) might have calculated a $275.00 drawdown on the reshuffled trades or
an 11% drawdown (275/2500). The second Monte Carlo run (2 of 1000) would reshuffle the trades and might recalculate
the drawdown to be $450.00 on this random ordering of the trades; that would be an 18% drawdown (450/2500).
After 1000 reshuffles we are left with the image below - all done instantly.
"""


class MonteCarloTest:

    def __init__(self, trades_df):
        self.trades_df = trades_df

    def reshuffle_trades(self, trades):
        # TODO: simulate trades by reshuffling order
        """
        A quick recap of what a simple Monte Carlo test can be... we will reshuffle the order of the trades 1,000 times.
        Each time we will re-create an equity curve by adding the newly shuffled trades up one by one.
        Each time we will calculate a max drawdown as if the trades had actually happened in this shuffled order.
        """
        return pd.DataFrame(trades, columns=["Trade","PnL"])

    def simulate_fixed_trades(self, simulations, p_win, p_mid, profit, mid_loss, loss):
        trades = []

        # generate trades based on probabilities
        for i in range(0, simulations):
            rand = random.random()
            if rand <= p_win:
                pnl = profit
            elif rand <= p_win + p_mid:
                pnl = -mid_loss
            else:
                pnl = -loss

            trades.append({"Trade": 1 + i, "PnL": pnl})

        return pd.DataFrame(trades, columns=["Trade", "PnL"])

    def simulate_trades(self, simulations, p_win, profit, loss, start_equity, risk, dynamic_size):
        trades = []

        r_win = profit/loss

        # generate trades based on probabilities
        equity = start_equity
        for i in range(0, simulations):
            rand = random.random()

            if rand <= p_win:
                pnl = (equity*risk*r_win)
            else:
                pnl = -(equity*risk)

            if dynamic_size:
                equity += pnl

            trades.append({"Trade":1+i, "PnL": pnl})

        return pd.DataFrame(trades, columns=["Trade","PnL"])

    def simulate(self, p_high, p_mid, profit, loss_mid, loss, trade_count=100, equity=10000, risk=0.0,
                 dynamic_size=False, sim_count=100, plot=False):
        if risk == 0.0:
            # Use Kelly sizing:  W – ((1 – W) / R)
            r = (profit/loss)
            risk = p_high - (1.0 - p_high)/r
            #risk *= 0.01
            risk_type = "Kelly size"
        else:
            risk_type = "% of Cap."

        click.echo("Running {0} simulations with {1}% risk ({2}) of {3} starting equity.".format(sim_count, round(risk*100,2), risk_type, equity))
        if dynamic_size:
            click.echo("Adding profits/losses cumulatiely to equity")

        trade_simulations = []

        if p_mid > 0.0:
            click.echo("P_high={0}, P_mid={1}, Avg.Profit={2}, Avg.Loss={3}, MaxLoss={4}".format(p_high, p_mid, profit, loss_mid, loss))
            avg_pnl = 0
            for i in range(0, sim_count):
                sim = self.simulate_fixed_trades(trade_count, p_high, p_mid, profit, loss_mid, loss)
                trade_simulations.append(sim)
                avg_pnl += sim['PnL'].mean()
            avg_pnl /= sim_count
            click.echo("Average PnL per trade: {0}".format(avg_pnl))

        else:
            click.echo("P_win={0}, Avg.Profit={1}, Avg.Loss={2}".format(p_high, profit, loss))
            for i in range(0, sim_count):
                trade_simulations.append(
                    self.simulate_trades(trade_count, p_high, profit, loss, equity, risk, dynamic_size))

        # Generate equity curves from trades
        equity_curves = MonteCarloTest.portfolio_simulations(equity, trade_simulations)

        # Get statistics from generated equity curves
        stats = MonteCarloTest.equity_curve_stats(equity_curves)
        click.echo("Min equity: {0}".format(round(stats['equity_min'],1)))
        click.echo("Max equity: {0}".format(round(stats['equity_max'],1)))
        click.echo("Performance avg: {0}%".format(round(stats['perf_avg_pct'], 1)))
        click.echo("Max Drawdown: {0}%".format(round(stats['dd_max_pct'],2)))
        click.echo("Average Max Drawdown: {0}%".format(round(stats['dd_max_avg_pct'],2)))
        click.echo("Risk of ruin: {0}%".format(round(stats['risk_ruin'], 8)))

        #TODO: monte carlo analysis of performance, i.e. end_value-start_value (in percent)
        # 1. Generate equity curves, i.e. 1000 performance values
        # 2. Plot histogram
        # 3. Plot cumulative distribution Mark where 95% of all performances are higher than
        if plot:
            MonteCarloTest.plot_equity_curves(equity_curves)
            #for eq in equity_curves:
            #    eq['EQ'].plot()
            #plt.show()

    @staticmethod
    def portfolio_simulations(start_equity, trade_simulations):

        equity_curves = []

        for sim in trade_simulations:
            eq = pd.DataFrame(columns=['EQ'], index=sim.index)
            equity = start_equity+0.1 # In case first trade wipes out everthing
            for index, row in sim.iterrows():
                if equity > 0:
                    equity += row['PnL']
                    eq.set_value(index, 'EQ', equity)
                else:
                    # Stop here or just set the rest to zero?
                    eq.set_value(index, 'EQ', 0)


            #if eq['EQ'].iloc[-1] == 0:
            #    print(sim)
            equity_curves.append(eq)
            #TODO: what more from ffn lib?

        return equity_curves

    @staticmethod
    def equity_curve_stats(equity_curves):
        stats = {}
        end_equity = [eq['EQ'].iloc[-1] for eq in equity_curves]
        stats['equity_max'] = max(end_equity)
        stats['equity_min'] = min(end_equity)

        # Drawdown stats:
        stats['dd_max_avg_pct'] = 0
        stats['dd_max_pct'] = 0
        stats['perf_avg_pct'] = 0
        stats['risk_ruin'] = 0
        for eq in equity_curves:
            eq_curve = eq['EQ']

            if eq_curve.iloc[-1] == 0:
                stats['risk_ruin'] += 1

            stats['perf_avg_pct'] += ((eq_curve.iloc[-1] - eq_curve.iloc[0]) / eq_curve.iloc[0])*100
            max_dd = -ffn.calc_max_drawdown(eq_curve)*100
            stats['dd_max_pct'] = max(max_dd,stats['dd_max_pct'])
            stats['dd_max_avg_pct'] += max_dd

        stats['dd_max_avg_pct'] /= len(equity_curves)
        stats['perf_avg_pct'] /= len(equity_curves)
        stats['risk_ruin'] = stats['risk_ruin']*100 / len(equity_curves)

        return stats

    @staticmethod
    def plot_equity_curves(equity_curves):
        fig, ax = plt.subplots()
        for curve in equity_curves:
            #ax = curve['PnL'].cumsum().plot(ax=ax)
            ax = curve['EQ'].plot(ax=ax)

        ax.set_ylabel("Equity")
        ax.set_xlabel("# Trades")
        plt.title( "{0} Monte Carlo Simulations".format(len(equity_curves)))
        plt.show()


def float_range(ctx, param, value):
    if value <= 1.0 and value >= 0.0:
        return value
    raise click.BadParameter('Risk: 0 <= 1')


@click.command()
@click.option('--prob-win', required=True, type=click.FLOAT, help='Probability for winning trade, e.g. 0.65 for 65%')
@click.option('--profit-avg', required=True, type=click.FLOAT, help='The average profit, e.g. "100" for $100')
@click.option('--loss-avg', required=True, type=click.FLOAT, help='The average loss, e.g. "50" for -$50')
@click.option('--trades', default=100, type=click.INT, help='Number of trades used in simulations')
@click.option('--equity', default=1000, type=click.INT, help='Starting equity, e.g 10000 for $10000')
@click.option('--risk', default=0.0, type=click.FLOAT,  callback=float_range, help='Percent of portfolio to risk, e.g. 0.02 for 2%. If 0 use kelly sizing')
@click.option('--dynamic-size', is_flag=True, help='Add profits/losses cumulatively to equity and increase position size')
@click.option('--simulations', default=10, type=click.INT, help='Number of simulations, e.g. 10')
@click.option('--plot', is_flag=True, help="Plot equity curves")
def main(prob_win, profit_avg, loss_avg, trades, equity, risk, dynamic_size, simulations, plot):
    """Command line tool for simulating equity curves."""

    MonteCarloTest(None).simulate(prob_win, 0, profit_avg, 0, loss_avg,
                                  trade_count=trades, equity=equity, risk=risk,
                                  dynamic_size=dynamic_size, sim_count=simulations, plot=plot)


if __name__ == '__main__':
    main()