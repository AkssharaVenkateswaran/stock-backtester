# Mean-Reversion Backtester (RSI + Bollinger Bands + 200-day trend filter)

A small Python backtesting engine that tests a rule-based mean-reversion strategy on daily price data, built to ask a simple question honestly: *does a strong-looking result survive being checked?*

**Stack:** Python, pandas, NumPy, yfinance

---

## The strategy

Each trading day the engine decides whether to hold the stock (signal = 1) or be in cash (signal = 0).

A buy signal needs **all** of these to be true:

1. **Price closes below the lower Bollinger Band** (20-day average minus 2 standard deviations), meaning the price is unusually low.
2. **14-day RSI is below 30**, meaning the stock has fallen sharply recently ("oversold").
3. **Price is above its 200-day moving average**, meaning the long-term trend is up. This is the *trend filter*, added to avoid "falling knives" (a company in permanent decline that keeps falling after you buy the dip).

**Avoiding lookahead bias:** the signal is shifted forward by one day (`.shift(1)`), so a signal computed from today's close is only acted on tomorrow. Strategy return = shifted signal × that day's market return.

**Known simplification:** there is no exit rule. The strategy is invested only on the day after a signal, otherwise in cash.

## Metrics

| Metric | How it's calculated |
|---|---|
| Annual return | mean daily strategy return × 252 |
| Annual volatility | standard deviation of daily returns × √252 |
| Sharpe ratio | (annual return − 4% risk-free rate) ÷ annual volatility |
| Max drawdown | largest fall from a previous peak of cumulative returns |
| Drawdown reduction | benchmark max drawdown minus strategy max drawdown, in **percentage points** |

## Files

| File | What it does |
|---|---|
| `[backtest_engine.py]` | Strategy with the 200-day trend filter, compared with **buy-and-hold of the same stock** |
| `[backtest_engine comparison without filter.py]` | Same strategy with the trend filter **removed**, to measure what the filter changes |
| `[backtest_engine SPY.py]` | Benchmarks against **SPY** (an ETF tracking the S&P 500). |



## How to run

```bash
pip install numpy pandas yfinance
python [backtester_filter_on.py]
```

Each file prints strategy performance, a benchmark comparison and trade diagnostics.

---

## Results

**Setup:** AAPL, 5-year window, 1,055 trading days after the 200-day warm-up.

### Filter on vs filter off vs buy-and-hold (AAPL)

| | Filter on | Filter off | Buy-and-hold (AAPL) |
|---|---|---|---|
| Annual return | -0.37% | 1.64% | 23.84% |
| Annual volatility | 3.07% | 8.97% | 27.12% |
| Sharpe ratio | -1.43 | -0.26 | 0.73 |
| Max drawdown | -6.23% | -12.66% | -33.36% |
| Drawdown vs buy-and-hold | 27.1 pts lower | 20.7 pts lower | n/a |
| Entries | 11 | 15 | n/a |
| Days invested | 20 (1.9%) | 31 (2.9%) | all |

### SPY comparison

| Metric | Result |
| :--- | :--- |
| Strategy max drawdown | -6.23% |
| SPY buy-and-hold max drawdown | -18.76% |
| Strategy Sharpe | -1.43 |
| SPY Sharpe | 0.84 |
| Max Drawdown Reduction | 12.5% lower than market |


### How often each condition is true (1,055 days)

| Condition | Days |
|---|---|
| Price below lower Bollinger Band | 44 |
| RSI below 30 | 115 |
| Both of the above | 31 |
| Both, plus above the 200-day average | 20 |

---

## What I found

- **The small drawdown is misleading on its own.** The strategy was invested on only 1.9% of days, so most of the low drawdown and low volatility comes from being in cash, not from a clever strategy. The Sharpe ratio (-1.43 vs 0.73 for buy-and-hold) shows this.
- **The trend filter lowered volatility and drawdown but cost return** (1.64% without it, -0.37% with it). It removed about a third of the days that qualified (31 down to 20), so those days were, on net, profitable in this sample.
- **My first assumption was only partly right.** I expected the trend filter to be the main reason the strategy traded so rarely. Without it the strategy still made only 15 entries. The bottleneck is mainly the Bollinger Band condition: the price closed below the lower band on only 44 of 1,055 days, and on 31 of those the RSI was also below 30.

## Limitations

- One stock, one five-year window, and only 11 to 15 trades, so no conclusion here is statistically strong.
- No transaction costs or slippage.
- No exit rule (the strategy holds for one day after each signal).
- No out-of-sample test: the same period is used to design and evaluate.
- The 4% risk-free rate is a fixed assumption.
- Prices come from yfinance (adjusted close).

## Next steps

- Test out of sample on a different period and on more stocks.
- Add transaction costs.
- Compare against a volatility-matched benchmark.
- Use fixed start and end dates so results are exactly reproducible.
