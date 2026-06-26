# QuantInsight-AI-Powered-Quant-Research-Dashboard
Overview

QuantInsight is a Python-based quantitative stock research dashboard built with Streamlit. It combines technical analysis, risk analytics, quantitative strategy testing, and news impact analysis into one interactive application.

The goal of this project is not simply to display stock prices, but to help analyze whether a stock presents an interesting investment opportunity by combining multiple quantitative factors.

The dashboard is designed for students, traders, and anyone interested in quantitative finance who wants to understand how different market factors work together before making a decision.

Features
Market Dashboard

The dashboard provides real-time market data using Yahoo Finance.

It displays:

Live stock prices
Company information
Candlestick chart
Volume analysis
Moving averages
RSI
Price history
Technical Analysis

The dashboard calculates commonly used technical indicators including:

Short and Long Moving Averages
RSI
Price Trend
Buy and Sell Signal Generation

The moving average crossover strategy is also used to identify possible entry and exit points.

Strategy Backtesting

A simple quantitative trading strategy is implemented to compare:

Buy and Hold returns
Strategy returns

The dashboard calculates:

Strategy Return
Sharpe Ratio
Cumulative Equity Curve

This allows users to evaluate whether the strategy performs better than simply holding the stock.

Risk Analytics

Several risk metrics are included to better understand market behavior.

The dashboard calculates:

Annualized Volatility
Maximum Drawdown
Value at Risk (95%)

These metrics help measure downside risk instead of looking only at returns.

News Impact Analysis

One of the unique parts of this project is the News Impact module.

The application fetches the latest company news directly from Yahoo Finance.

Each news article is analyzed using a rule-based sentiment engine.

News is classified as:

Positive
Neutral
Negative

The dashboard also combines news sentiment with technical trend and recent price movement to understand how the market is reacting.

This helps answer questions such as:

Is the market supporting the news?
Is the stock ignoring good news?
Is bad news already priced into the market?
Quant Opportunity Score

Instead of giving direct Buy or Sell recommendations, the dashboard generates an Opportunity Score between 0 and 100.

The score is calculated using multiple quantitative factors including:

News Sentiment
Technical Trend
Price Momentum
Maximum Drawdown
Volatility

The score helps prioritize stocks for further research rather than making automatic trading decisions.

Example interpretation:

0–30 → Weak Setup
30–50 → Watch Carefully
50–70 → Watchlist
70–85 → Interesting Opportunity
85–100 → High Conviction Setup
Technologies Used
Python
Streamlit
Pandas
NumPy
Plotly
yFinance
Project Structure
QuantInsight/
│
├── app.py
├── requirements.txt
├── README.md
├── assets/
└── screenshots/
What I Learned

While building this project I learned how quantitative finance combines market data, statistics, technical indicators, and news analysis to evaluate investment opportunities.

I also learned how to build an interactive financial dashboard using Streamlit, implement a basic backtesting engine, calculate important risk metrics, and create a scoring model that combines multiple market signals into a single opportunity score.

This project helped me understand that successful investing is not about relying on one indicator, but about analyzing several factors together before making a decision.

Future Improvements

I plan to continue improving this dashboard by adding:

Machine Learning based price prediction
Portfolio optimization
Multi-stock opportunity ranking
Factor investing models
Monte Carlo simulations
Options analytics
Sector comparison
AI-powered news summarization using large language models
Interactive portfolio management
Professional backtesting with transaction costs and position sizing

This project is created for educational and research purposes only. The opportunity score and market analysis are based on quantitative models and should not be considered financial advice. Users should perform their own research before making investment decisions.
