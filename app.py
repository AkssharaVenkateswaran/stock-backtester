import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from backtest_engine import BacktestEngine

# 1. Page Config
st.set_page_config(
    page_title="Quant Backtesting Dashboard", layout="wide"
)

st.title("📈 Quantitative Strategy Backtesting Engine")
st.markdown(
    "Evaluate statistical mean-reversion strategies with zero lookahead bias and dynamic trend filtering."
)

# 2. Sidebar controls
st.sidebar.header("Parameters")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL").upper()
period = st.sidebar.selectbox(
    "Historical Lookback", ["1y", "2y", "5y"], index=1
)
risk_free_rate = (
    st.sidebar.slider("Risk-Free Rate (%)", 0.0, 10.0, 4.0, 0.5) / 100
)

# 3. Initialise engine and generate data
try:
    engine = BacktestEngine(ticker=ticker, period=period)
    metrics = engine.calculate_performance(risk_free_rate=risk_free_rate)
    df = engine.generate_rsi_bb_signals().dropna()

    # 4. Metric cards Display
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Annual Return", metrics["Annual Return"])
    col2.metric("Annual Volatility", metrics["Annual Volatility"])
    col3.metric("Sharpe Ratio", metrics["Sharpe Ratio"])
    col4.metric("Max Drawdown", metrics["Max Drawdown"])

    st.markdown("---")

    # 5. Visual charts
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(f"{ticker} Price and Bollinger Bands", "RSI (14-Day)"),
        row_heights=[0.7, 0.3],
    )

    # Subplot 1: Price and Bands
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df["Close"], name="Close Price", line=dict(color="blue")
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Upper_Band"],
            name="Upper Band",
            line=dict(color="gray", dash="dash"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Lower_Band"],
            name="Lower Band",
            line=dict(color="gray", dash="dash"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Long_MA_200"],
            name="200-day MA",
            line=dict(color="orange"),
        ),
        row=1,
        col=1,
    )

    buy_signals = df[df["Raw_Signal"] == 1]
    fig.add_trace(
        go.Scatter(
            x=buy_signals.index,
            y=buy_signals["Close"],
            mode="markers",
            name="Buy Signal",
            marker=dict(symbol="triangle-up", size=12, color="green"),
        ),
        row=1,
        col=1,
    )

    # Subplot 2: RSI
    fig.add_trace(
        go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="purple")),
        row=2,
        col=1,
    )

    # FIX: changed add_fline to add_hline
    fig.add_hline(
        y=30, line_dash="dash", line_color="red", annotation_text="Oversold (30)", row=2, col=1
    )

    fig.add_hline(
        y=70, line_dash="dash", line_color="green", annotation_text="Overbought (70)", row=2, col=1
    )

    fig.update_layout(height=650, showlegend=True, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error executing backtest: {e}")