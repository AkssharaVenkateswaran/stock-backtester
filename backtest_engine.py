import numpy as np
import pandas as pd
import yfinance as yf


class BacktestEngine:
    def __init__(
        self,
        ticker: str,
        period: str = "2y",
        short_window: int = 20,
        long_window: int = 50,
    ):
        self.ticker = ticker.upper()
        self.period = period
        self.short_window = short_window
        self.long_window = long_window

        # Fetch and prepare data once during initialization
        self.data = self._fetch_and_prepare_data()

    def _fetch_and_prepare_data(self) -> pd.DataFrame:
        historical_prices = yf.Ticker(self.ticker).history(period=self.period)
        if historical_prices.empty:
            raise ValueError(f"No history available for ticker: {self.ticker}")

        historical_prices["Market_Return"] = historical_prices[
            "Close"
        ].pct_change()
        historical_prices["Short_MA"] = (
            historical_prices["Close"]
            .rolling(window=self.short_window)
            .mean()
        )
        historical_prices["Long_MA"] = (
            historical_prices["Close"].rolling(window=self.long_window).mean()
        )

        return historical_prices

    def generate_rsi_bb_signals(self) -> pd.DataFrame:
        df = self.data.copy()

        # 1. Calculate 20-day Bollinger Bands
        df["Std_20"] = df["Close"].rolling(window=20).std()
        df["Upper_Band"] = df["Short_MA"] + (2 * df["Std_20"])
        df["Lower_Band"] = df["Short_MA"] - (2 * df["Std_20"])

        # 2. Calculate 14-day RSI
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # 3. Calculate 200-day Moving Average & Filtered Buy Condition
        df["Long_MA_200"] = df["Close"].rolling(window=200).mean()

        buy_condition = (
            (df["Close"] < df["Lower_Band"])
            & (df["RSI"] < 30)
            & (df["Close"] > df["Long_MA_200"])
        )

        df["Raw_Signal"] = np.where(buy_condition, 1, 0)

        # 4. Shift signal by 1 period to prevent lookahead bias
        df["Shifted_Signal"] = df["Raw_Signal"].shift(1)

        # 5. Calculate strategy returns
        df["Strategy_Return"] = df["Shifted_Signal"] * df["Market_Return"]

        return df

    def calculate_performance(self, risk_free_rate: float = 0.04) -> dict:
        df = self.generate_rsi_bb_signals().dropna()

        # Scalar metric calculations
        strat_annual_return = df["Strategy_Return"].mean() * 252
        strat_vol = df["Strategy_Return"].std() * np.sqrt(252)

        # Handle zero volatility edge cases
        strat_sharpe = (
            (strat_annual_return - risk_free_rate) / strat_vol
            if strat_vol != 0
            else 0.0
        )

        # Maximum Drawdown calculation
        df["Cum_Strategy"] = (1 + df["Strategy_Return"]).cumprod()
        df["Running_Max"] = df["Cum_Strategy"].cummax()
        df["Drawdown"] = (
            df["Cum_Strategy"] - df["Running_Max"]
        ) / df["Running_Max"]

        max_drawdown = df["Drawdown"].min()

        return {
            "Annual Return": f"{strat_annual_return:.2%}",
            "Annual Volatility": f"{strat_vol:.2%}",
            "Sharpe Ratio": round(strat_sharpe, 2),
            "Max Drawdown": f"{max_drawdown:.2%}",
        }

    def calculate_benchmark_comparison(
        self, risk_free_rate: float = 0.04
    ) -> dict:
        df = self.generate_rsi_bb_signals().dropna()

        # --- Strategy Metrics ---
        strat_annual_return = df["Strategy_Return"].mean() * 252
        strat_vol = df["Strategy_Return"].std() * np.sqrt(252)
        strat_sharpe = (
            (strat_annual_return - risk_free_rate) / strat_vol
            if strat_vol != 0
            else 0.0
        )

        df["Cum_Strategy"] = (1 + df["Strategy_Return"]).cumprod()
        df["Strat_Peak"] = df["Cum_Strategy"].cummax()
        strat_mdd = ((df["Cum_Strategy"] - df["Strat_Peak"]) / df["Strat_Peak"]).min()

        # --- Benchmark (Market / Buy-and-Hold) Metrics ---
        bench_annual_return = df["Market_Return"].mean() * 252
        bench_vol = df["Market_Return"].std() * np.sqrt(252)
        bench_sharpe = (
            (bench_annual_return - risk_free_rate) / bench_vol
            if bench_vol != 0
            else 0.0
        )

        df["Cum_Bench"] = (1 + df["Market_Return"]).cumprod()
        df["Bench_Peak"] = df["Cum_Bench"].cummax()
        bench_mdd = ((df["Cum_Bench"] - df["Bench_Peak"]) / df["Bench_Peak"]).min()

        # --- Reduction in Drawdown (Percentage Point Difference) ---
        mdd_reduction = (abs(bench_mdd) - abs(strat_mdd)) * 100

        return {
            "Strategy Sharpe Ratio": round(strat_sharpe, 2),
            "Benchmark Sharpe Ratio": round(bench_sharpe, 2),
            "Strategy Max Drawdown": f"{strat_mdd:.2%}",
            "Benchmark Max Drawdown": f"{bench_mdd:.2%}",
            "Max Drawdown Reduction": f"{mdd_reduction:.1f}% lower than market",
        }


if __name__ == "__main__":
    engine = BacktestEngine(ticker="AAPL", period="5y")

    print("--- Strategy Performance ---")
    print(engine.calculate_performance())

    print("\n--- Strategy vs Benchmark Comparison ---")
    print(engine.calculate_benchmark_comparison())

