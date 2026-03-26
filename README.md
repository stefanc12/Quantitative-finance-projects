#   In the file named share_analysis.py you will find an Equity Market Analysis & Time Series Forecasting

## Overview

This project implements a financial data analysis and modeling pipeline for major US equities and the S&P 500 index. It focuses on return analysis, volatility estimation, CAPM modeling, and time series forecasting using classical econometric techniques.

The goal is to explore statistical properties of financial time series and apply predictive models commonly used in quantitative finance.

---

##  Data

Market data is retrieved using the `yfinance` API for the following assets:

* AAPL (Apple)
* AMZN (Amazon)
* GOOG (Google)
* MSFT (Microsoft)
* TSLA (Tesla)
* ^GSPC (S&P 500 Index)

Time range:

* January 2022 – March 2026

---

## ⚙️ Features

### 1. Return Computation

* Daily returns
* Weekly returns
* Multi-horizon returns:

  * 2-week returns
  * 1-month returns

---

### 2. Volatility Analysis

* Annualized volatility computed over:

  * Last 252 trading days (1Y)
  * Last 504 trading days (2Y)
  * Year-specific (2024, 2025)

---

### 3. CAPM Modeling

Two approaches are used to estimate beta:

#### Covariance-based method

* Uses annualized variance-covariance matrix

#### Regression-based method

* Linear regression of asset returns vs market returns
* Residuals analyzed for:

  * distribution
  * autocorrelation

---

### 4. Time Series Modeling

Implemented models:

* AR(1), AR(2), AR(3)
* ARMA(1,1)
* ARIMA(1,1,1)

Applications:

* Forecasting returns for S&P 500
* Forecasting returns for individual equities
* Generating forward price paths:

  * 10 days
  * 20 days
  * 30 days

---

### 5. Model Diagnostics

* Residual analysis
* Autocorrelation checks
* Error distribution visualization (histograms)

---

### 6. Excel Integration

* Automated export of:

  * price data
  * returns
  * volatility metrics
* Implemented using `xlwings`

---

##  Key Concepts

* Time Series Analysis
* CAPM (Capital Asset Pricing Model)
* Linear Regression
* Volatility Estimation
* Statistical Diagnostics
* Financial Data Analysis

---

##  Tech Stack

**Languages**

* Python

**Libraries**

* NumPy
* Pandas
* Statsmodels
* Scikit-learn
* Matplotlib
* yfinance
* xlwings

---


##  Future Improvements

* Backtesting trading strategies based on forecasts
* Performance evaluation (Sharpe ratio, drawdown)
* Benchmark comparison (e.g., buy-and-hold vs model-based strategy)
* More advanced models (GARCH, stochastic processes)

---


