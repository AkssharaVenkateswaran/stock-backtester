# Quantitative Strategy Backtesting Engine & Dashboard

A Python-based quantitative backtesting engine and interactive dashboard built to evaluate statistical mean-reversion trading strategies on equity historical data while guarding against lookahead bias and structural market downtrends.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-FF4B4B)
![Plotly](https://img.shields.io/badge/Plotly-5.0%2B-3F4F75)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458)

---

## Key Features

* **Vectorized Technical Analysis:** Fast backtesting powered by NumPy and Pandas vectorization.
* **Mean-Reversion Signal Engine:** Combines 20-day Bollinger Bands ($2\sigma$) with 14-day Relative Strength Index (RSI) to identify statistical oversold entry opportunities.
* **Falling Knife Protection:** Incorporates a 200-day Simple Moving Average ($\text{SMA}_{200}$) regime filter to ensure trades are only initiated within long-term uptrends.
* **Zero Lookahead Bias:** Formally shifts trading signals by $T+1$ execution periods to prevent lookahead bias in performance metrics.
* **Risk-Adjusted Performance Metrics:** Calculates Annualized Return, Annualized Volatility, Sharpe Ratio, and Maximum Drawdown peak-to-trough analysis.
* **Interactive Web GUI:** Real-time visualization dashboard built with Streamlit and dual-axis synced Plotly subplots.

---

## Quantitative Strategy Rules

The strategy seeks high-probability pullback entries by identifying short-term price and momentum exhaustion within a long-term bull trend.

1. **Entry Rules (Long Signal = 1):**
   * **Price Extremity:** $\text{Close} < \text{Lower Bollinger Band } (\text{SMA}_{20} - 2\sigma)$
   * **Momentum Exhaustion:** $\text{RSI}_{14} < 30$
   * **Trend Filter Guardrail:** $\text{Close} > \text{SMA}_{200}$
2. **Execution Timing:** Signals generated at market close on Day $T$ are executed at open on Day $T+1$.
3. **Exit Rules:** Position closes when RSI rises back above $50$ or price crosses back over the moving average.

---

## Tech Stack

* **Language:** Python
* **Data Processing & Stats:** Pandas, NumPy
* **Market Data Source:** `yfinance` API
* **Interactive Visualization:** Plotly Graph Objects
* **Web UI Framework:** Streamlit

---

## System Architecture & File Structure

```text
├── backtest_engine.py   # Core OOP class handling data fetch, indicators, signal logic, & metrics
├── app.py               # Streamlit application entry point & interactive Plotly visualization
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## Installation & Set up

1. **Clone the repository**
```bash
git clone [https://github.com/YOUR_USERNAME/stock-backtester.git](https://github.com/YOUR_USERNAME/stock-backtester.git)
cd stock-backtester
```

2. **Set Up Virtual Environment**
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```
---

# Usage
**Run Engine Terminal Benchmark**
- To verify performance logic directly via Python:
```bash
python backtest_engine.py
```
- Launch Interactive Streamlit Dashboard
```bash
streamlit run app.py
```

---

# Sample Performance Output

```bash
{
  "Annual Return": "1.36%",
  "Annual Volatility": "3.59%",
  "Sharpe Ratio": -0.73,
  "Max Drawdown": "-3.08%"
}
```
