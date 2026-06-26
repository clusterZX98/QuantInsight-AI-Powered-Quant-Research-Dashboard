import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# 1. Page Configuration (MUST be the very first line)
st.set_page_config(page_title="Pro Stock Analysis", layout="wide", page_icon="📈")

# 2. Data Caching for Performance
@st.cache_data(ttl=3600)
def fetch_stock_data(ticker, period):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        return data, stock.info
    except Exception:
        return None, None
    
#  News Sentiment Analysis (Basic Keyword-Based)
def analyze_news_impact(news_items):
    positive_words = [
        "profit", "growth", "gain", "gains", "strong", "beat", "beats",
        "upgrade", "expansion", "record", "surge", "bullish", "positive",
        "approval", "rally", "higher", "buy", "robust", "order book"
    ]

    negative_words = [
        "loss", "fall", "falls", "drop", "weak", "miss", "downgrade",
        "fraud", "investigation", "decline", "crash", "bearish",
        "negative", "sell", "lawsuit", "concern", "lower", "delay",
        "pressure", "margin pressure"
    ]

    analyzed_news = []
    total_score = 0

    for item in news_items[:10]:
        content = item.get("content", {})

        title = content.get("title", "No title")
        summary = content.get("summary", "")

        provider = content.get("provider", {})
        publisher = provider.get("displayName", "Unknown")

        canonical_url = content.get("canonicalUrl", {})
        link = canonical_url.get("url", "")

        text = f"{title} {summary}".lower()

        score = 0

        for word in positive_words:
            if word in text:
                score += 1

        for word in negative_words:
            if word in text:
                score -= 1

        if score > 0:
            sentiment = "Positive"
        elif score < 0:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        total_score += score

        analyzed_news.append({
            "Title": title,
            "Publisher": publisher,
            "Sentiment": sentiment,
            "Impact Score": score,
            "Link": link
        })

    return analyzed_news, total_score

# Combine all factors into a single opportunity score (0-100) and label

def calculate_opportunity_score(news_score, technical_trend, recent_return, max_drawdown, volatility):
    # 1. News factor: max 25 points
    news_factor = min(max(news_score * 10, 0), 25)

    # 2. Trend factor: max 20 points
    trend_factor = 20 if technical_trend == "Bullish" else 0

    # 3. Momentum factor: max 20 points
    if recent_return > 5:
        momentum_factor = 20
    elif recent_return > 0:
        momentum_factor = 10
    else:
        momentum_factor = 0

    # 4. Drawdown risk factor: max 20 points
    if max_drawdown > -15:
        risk_factor = 20
    elif max_drawdown > -30:
        risk_factor = 10
    else:
        risk_factor = 0

    # 5. Volatility factor: max 15 points
    if volatility < 20:
        vol_factor = 15
    elif volatility < 35:
        vol_factor = 8
    else:
        vol_factor = 0

    opportunity_score = (
        news_factor +
        trend_factor +
        momentum_factor +
        risk_factor +
        vol_factor
    )

    if opportunity_score >= 85:
        label = "🔥 High Conviction"
    elif opportunity_score >= 70:
        label = "🟢 Interesting Setup"
    elif opportunity_score >= 50:
        label = "🟡 Watchlist"
    else:
        label = "🔴 Avoid / Weak Setup"

    factors = {
        "News Factor": news_factor,
        "Trend Factor": trend_factor,
        "Momentum Factor": momentum_factor,
        "Drawdown Risk Factor": risk_factor,
        "Volatility Factor": vol_factor
    }

    return opportunity_score, label, factors

def main():
    st.title("📈 Advanced Stock Analysis Dashboard")

    # 3. Sidebar for User Controls
    st.sidebar.header("Dashboard Parameters")
    ticker = st.sidebar.text_input("Ticker Symbol", value="HDFCBANK.NS").upper()
    period = st.sidebar.selectbox("Time Period", options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
    
    ma_short_window = st.sidebar.slider("Short Moving Average", min_value=5, max_value=50, value=20)
    ma_long_window = st.sidebar.slider("Long Moving Average", min_value=50, max_value=200, value=50)

    if ticker:
        with st.spinner(f"Fetching data for {ticker}..."):
            data, info = fetch_stock_data(ticker, period)
        try:
            stock_obj = yf.Ticker(ticker)
            news_items = stock_obj.news
        except Exception:
            news_items = []

        if data is None or data.empty:
            st.error(f"Could not find data for ticker '{ticker}'.")
            return

        # --- STEP 1: CALCULATE INDICATORS ---
        # Moving Averages
        data[f"MA{ma_short_window}"] = data["Close"].rolling(window=ma_short_window).mean()
        data[f"MA{ma_long_window}"] = data["Close"].rolling(window=ma_long_window).mean()

        # RSI Calculation
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))

        # Risk & Volatility
        daily_return = data['Close'].pct_change()
        volatility = daily_return.std() * (252**0.5) * 100
        data['Cumulative_Return'] = (1 + daily_return).cumprod()
        data['Running_Max'] = data['Cumulative_Return'].cummax()
        data['Drawdown'] = (data['Cumulative_Return'] / data['Running_Max'] - 1) * 100
        max_drawdown = data['Drawdown'].min()
        var_95 = daily_return.quantile(0.05) * 100

        # Clean up NaNs
        data.dropna(inplace=True)

        # --- STRATEGY SIGNALS ---

        # Create signal column
        data['Signal'] = 0

        # Buy signal when short MA > long MA
        data.loc[
        data[f"MA{ma_short_window}"] >
        data[f"MA{ma_long_window}"],
        'Signal'] = 1

        # Detect trade entries/exits
        data['Position'] = data['Signal'].diff()
    
         # --- BACKTESTING ENGINE ---

         # Daily market return
        data['Market_Return'] = data['Close'].pct_change()

         # Strategy return
        # shift(1) prevents look-ahead bias:
        # we use yesterday's signal to trade today's return
        data['Strategy_Return'] = data['Market_Return'] * data['Signal'].shift(1)

         # Cumulative performance
        data['Buy_Hold_Return'] = (1 + data['Market_Return']).cumprod()
        data['Strategy_Equity'] = (1 + data['Strategy_Return']).cumprod()

         # Total returns
        buy_hold_total_return = (data['Buy_Hold_Return'].iloc[-1] - 1) * 100
        strategy_total_return = (data['Strategy_Equity'].iloc[-1] - 1) * 100

         # Sharpe Ratio
        strategy_sharpe = (
         data['Strategy_Return'].mean() / data['Strategy_Return'].std()
         ) * (252 ** 0.5)



        # --- STEP 2: KPI METRICS ---
        current_price = data['Close'].iloc[-1]
        previous_price = data['Close'].iloc[-2]
        price_change = current_price - previous_price
        pct_change = (price_change / previous_price) * 100
        
        # Dynamic currency
        curr_symbol = info.get('currency', '₹')
        if curr_symbol == 'INR': curr_symbol = '₹'
        elif curr_symbol == 'USD': curr_symbol = '$'

        
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
        company_name = info.get('shortName', ticker)
        
        col1.metric("Company", company_name)
        col2.metric("Latest Close", f"{curr_symbol}{current_price:.2f}", f"{price_change:.2f} ({pct_change:.2f}%)")
        col3.metric("52W High", f"{curr_symbol}{info.get('fiftyTwoWeekHigh', 'N/A')}")
        col4.metric("Max Drawdown", f"{max_drawdown:.1f}%")
        col5.metric("Volatility", f"{volatility:.1f}%") 
        col6.metric("VaR (95%)", f"{var_95:.1f}%")
        col7.metric("Strategy Return", f"{strategy_total_return:.1f}%")
        col8.metric("Sharpe Ratio", f"{strategy_sharpe:.2f}")

    st.divider()
    tab1, tab2 = st.tabs(["📈 Technical Dashboard", "🧠 News Impact"])

        # --- STEP 3: THE CHART ---
    with tab1:
        fig = make_subplots(
             rows=5,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.04,
    row_heights=[0.35, 0.1, 0.18, 0.17, 0.2],
    subplot_titles=(
        "Price Action",
        "Volume",
        "Momentum (RSI)",
        "Risk (Drawdown %)",
        "Backtest: Strategy vs Buy & Hold"))
           
        fig.add_trace(go.Candlestick(x=data.index, open=data["Open"], high=data["High"],
                                     low=data["Low"], close=data["Close"], name="Price"), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{ma_short_window}"], 
                                 line=dict(color='orange', width=1.5), name="Short MA"), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{ma_long_window}"], 
                                 line=dict(color='blue', width=1.5), name="Long MA"), row=1, col=1)
        
        # Buy Signals
        buy_signals = data[data['Position'] == 1]

        fig.add_trace(
        go.Scatter(
        x=buy_signals.index,
        y=buy_signals['Close'],
        mode='markers',
        marker=dict(symbol='triangle-up', color='green', size=12),
        name='Buy Signal'),row=1, col=1)

        # Sell Signals
        sell_signals = data[data['Position'] == -1]

        fig.add_trace(
        go.Scatter(
        x=sell_signals.index,
        y=sell_signals['Close'],
        mode='markers',
        marker=dict(symbol='triangle-down', color='red', size=12),
        name='Sell Signal'), row=1, col=1)

        colors = ['red' if row['Open'] > row['Close'] else 'green' for index, row in data.iterrows()]
        fig.add_trace(go.Bar(x=data.index, y=data['Volume'], marker_color=colors, name="Volume"), row=2, col=1)

        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], line=dict(color='purple', width=2), name="RSI"), row=3, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="green", row=3, col=1)

        fig.add_trace(go.Scatter(x=data.index,y=data['Buy_Hold_Return'],name="Buy & Hold",line=dict(width=2)
                                 ),row=5, col=1)

        fig.add_trace(go.Scatter( x=data.index, y=data['Strategy_Equity'], name="Strategy Equity", line=dict(width=2)
                                 ),row=5,col=1)
        
        fig.update_layout(height=1200, xaxis_rangeslider_visible=False, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    

    with tab2:
        st.subheader("🧠 News Impact Feature")

    if news_items:
        analyzed_news, news_score = analyze_news_impact(news_items)

        recent_return = data["Close"].pct_change(5).iloc[-1] * 100

        if data[f"MA{ma_short_window}"].iloc[-1] > data[f"MA{ma_long_window}"].iloc[-1]:
            technical_trend = "Bullish"
            trend_score = 1
        else:
            technical_trend = "Bearish"
            trend_score = -1

        final_score = news_score + trend_score

        opportunity_score, opportunity_label, opportunity_factors = calculate_opportunity_score(
        news_score,
        technical_trend,
        recent_return,
        max_drawdown,
        volatility)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("News Score", news_score)
        c2.metric("5-Day Reaction", f"{recent_return:.2f}%")
        c3.metric("Technical Trend", technical_trend)

        if final_score >= 3:
            quant_view = "Bullish Bias"
            explanation = "Recent news sentiment and technical trend are supportive."
        elif final_score <= -3:
            quant_view = "Bearish Bias"
            explanation = "Recent news sentiment and technical trend are weak."
        else:
            quant_view = "Caution / Wait"
            explanation = "Signals are mixed. Market confirmation is not strong."

        c4.metric("Impact View", quant_view)

        st.info(explanation)

        st.subheader("🎯 Quant Opportunity Score")

        o1, o2 = st.columns(2)

        o1.metric("Opportunity Score",
        f"{opportunity_score:.0f}/100")

        o2.metric("Setup Quality",
        opportunity_label)

        factor_df = pd.DataFrame(
        list(opportunity_factors.items()),
        columns=["Factor", "Points"])

        st.dataframe(
         factor_df,
        use_container_width=True)

        news_df = pd.DataFrame(analyzed_news)

        st.dataframe(
            news_df[["Title", "Publisher", "Sentiment", "Impact Score"]],
            use_container_width=True)
        
        
    else:
        st.warning("No recent news found for this ticker.")



        # --- STEP 4: FUNDAMENTALS ---
        st.subheader("📊 Key Fundamental Data")
        f1, f2, f3, f4 = st.columns(4)
        f1.write(f"**Trailing P/E:** {info.get('trailingPE', 'N/A')}")
        f2.write(f"**Price to Book:** {info.get('priceToBook', 'N/A')}")
        f3.write(f"**Debt to Equity:** {info.get('debtToEquity', 'N/A')}")
        f4.write(f"**Dividend Yield:** {info.get('dividendYield', 0)*100:.2f}%")

# --- THE MOST IMPORTANT PART ---
# If this part is missing or indented wrong, the page stays blank!
if __name__ == "__main__":
    main()


