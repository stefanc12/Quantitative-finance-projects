# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 16:11:03 2026

@author: XYZW

1. Daily returns of each share 
2. Weekly returns of each share
"""

import yfinance as yf
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression as LinReg
import xlwings as xw
import pandas as pd
import matplotlib.pyplot as plt
#%%
"""
Download data for APPLE (AAPL), AMAZON (AMZN), GOOGLE, Microsoft, Tesla and 
S&P500 (GSPC)
"""
share_data = yf.download("AAPL AMZN GOOG MSFT TSLA ^GSPC",start = "2022-01-01",end = "2026-03-21")
share_data = share_data['Close']
share_returns = share_data.iloc[1:,]/np.array(share_data.iloc[0:-1,:])-1
share_returns_1W = share_data.iloc[5:,]/np.array(share_data.iloc[0:-5,:])-1
#%%
wb = xw.Book()
wb.save('share_data.xlsx')
wb.sheets.add("Returns")
wb.sheets["Input"].range(1,1).value = share_data
wb.sheets["Returns"].range(1,1).value = share_returns
#%%

#%%
"""
Fit and predict returns using ARMA(1,1) and ARIMA(1,1,1) models. 
"""
arma_mdl11 = sm.tsa.ARIMA(share_returns.iloc[:,5],order = (1,0,1)).fit()
arima_mdl111 = sm.tsa.ARIMA(share_returns.iloc[:,5],order = (1,1,1)).fit()
arma11_params = arma_mdl11.params
arima111_params = arima_mdl111.params

snp_for10d = arma_mdl11.forecast(10)
snp_for10d_bis = arima_mdl111.forecast(10)
snp_prices = share_data.iloc[-1,-1]*np.cumprod(1+snp_for10d)
snp_prices2 = share_data.iloc[-1,-1]*np.cumprod(1+snp_for10d_bis)
#%%
"""
Find beta of each share w.r.t S&P500 index. 

Method 1 (when working with non-correlated returns): 
    Annualized variance-covariance matrix of returns => Betas
    This way one can find betas based on daily returns. 
    
Method 2: Using linear regressions. (CAPM model without risk-free rate)
"""
cov_rets_last252 = share_returns.iloc[-252:,].cov()*252
betas = cov_rets_last252.iloc[0:5,-1]/cov_rets_last252.iloc[5,5]
reg_mdls =[LinReg().fit(np.array(share_returns.iloc[-252:,-1],ndmin = 2).T, 
                        np.array(share_returns.iloc[-252:,i],ndmin = 2).T) for i in range(0,5)]
coeffs = [reg_mdls[i].coef_[0][0] for i in range(0,5)]

"""
Erorile regresiei liniare pentru fiecare actiune, pe baza ultimelor 252 de zile.
"""

errors = [np.array(share_returns.iloc[-252:,i],ndmin = 2).T - reg_mdls[i].predict(np.array(share_returns.iloc[-252:,-1],ndmin = 2).T) for i in range(0,5)]
#%%
def err_reg(X,y):
    """
    Parameters:
        
        X and y are 2dim numpy arrays (column matrices)
    
    Returns:
        A column matrix of errors. 
        
    """
    if len(np.shape(X))==1:
        X = np.array(X,ndmin = 2).T
    
    if len(np.shape(y))==1:
        y = np.array(y,ndmin = 2).T

    reg = LinReg().fit(X,y)
    fitted_y = reg.predict(X)
    errors = fitted_y - y
    return errors
errs_apple = err_reg(share_returns.iloc[-252:,-1],share_returns.iloc[-252:,0])
errs_amzn = err_reg(share_returns.iloc[-252:,-1],share_returns.iloc[-252:,1])

plt.hist(errs_amzn)
plt.grid(True)
plt.title('Histogram of AMZN CAPM model errors')
plt.show()
#%%
df_errs = pd.DataFrame(np.hstack([err_reg(share_returns.iloc[-252:,-1],share_returns.iloc[-252:,i]) for i in range(0,5)]),
                       columns = ['AAPL','AMZN','GOOG','MSFT','TSLA'])
print(df_errs)
df_errs['S&P'] = np.array(share_returns.iloc[-252:,-1])
#%%
print((pd.Series(errs_apple[:,0])).autocorr(lag = 1))

print((pd.Series(errs_apple[:,0])).autocorr(lag = 2))

#%% 
"""CAPM model for weekly returns."""
reg_mdls_1W =[LinReg().fit(np.array(share_returns_1W.iloc[-50:,-1],ndmin = 2).T, 
                        np.array(share_returns_1W.iloc[-50:,i],ndmin = 2).T) for i in range(0,5)]
coeffs_1W = [reg_mdls_1W[i].coef_[0][0] for i in range(0,5)]
#%%
"""Dataframe with capm 1w and daily betas."""
df_betas_1W = pd.DataFrame([coeffs_1W], columns=['AAPL', 'AMZN', 'GOOG', 'MSFT', 'TSLA'])
print(df_betas_1W)
#%% 
"""Volatilities around Beta ??"""
vols_1W = share_returns_1W.iloc[-50:,:].std()
#%%
"""Randamentele la 2 saptamani, respectiv 1 luna, pentru fiecare actiune."""
returns_2W = share_data.iloc[10:,]/np.array(share_data.iloc[0:-10,:])-1
returns_1M = share_data.iloc[22:,]/np.array(share_data.iloc[0:-22,:])-1
#%%
"""
Volatilitatea randamentelor zilnice ale celor 5 actiuni pe  perioada:
    1. ultimelor 252 de zile, 
    2. ultimii 2 ani, 
    3. anul 2025 
    4. anul 2024.
"""
vols_1Y = share_returns.iloc[-252:,:].std()
vols_2Y = share_returns.iloc[-504:,:].std()
vols_2025 = share_returns[share_returns.index.year == 2025].std()
vols_2024 = share_returns[share_returns.index.year == 2024].std()

df_vols = pd.concat([vols_1Y,vols_2Y,vols_2025,vols_2024],axis = 1)
df_vols.columns = ['Vol last Year','Vol last 2 years','Vol 2025','Vol 2024']
wb.sheets['Returns'].range("J1").value = df_vols*np.sqrt(252)
#%%
"""
predictie a randamentelor si preturilor s&p500 pe urmatoarele 10, 20, resp 30 de zile
folosind AR(1), AR(2), AR(3)
"""
ar1_mdl = sm.tsa.ARIMA(share_returns.iloc[:,5],order = (1,0,0)).fit()
ar2_mdl = sm.tsa.ARIMA(share_returns.iloc[:,5],order = (2,0,0)).fit()
ar3_mdl = sm.tsa.ARIMA(share_returns.iloc[:,5],order = (3,0,0)).fit()

ar1_for10d = ar1_mdl.forecast(10)  
ar2_for10d = ar2_mdl.forecast(10)
ar3_for10d = ar3_mdl.forecast(10)

ar1_for20d = ar1_mdl.forecast(20)
ar2_for20d = ar2_mdl.forecast(20)
ar3_for20d = ar3_mdl.forecast(20)

ar1_for30d = ar1_mdl.forecast(30)
ar2_for30d = ar2_mdl.forecast(30)
ar3_for30d = ar3_mdl.forecast(30)

snp_prices_ar1_10d = share_data.iloc[-1,-1]*np.cumprod(1+ar1_for10d)
snp_prices_ar2_10d = share_data.iloc[-1,-1]*np.cumprod(1+ar2_for10d)
snp_prices_ar3_10d = share_data.iloc[-1,-1]*np.cumprod(1+ar3_for10d)

snp_prices_ar1_20d = share_data.iloc[-1,-1]*np.cumprod(1+ar1_for20d)
snp_prices_ar2_20d = share_data.iloc[-1,-1]*np.cumprod(1+ar2_for20d)
snp_prices_ar3_20d = share_data.iloc[-1,-1]*np.cumprod(1+ar3_for20d)

snp_prices_ar1_30d = share_data.iloc[-1,-1]*np.cumprod(1+ar1_for30d)
snp_prices_ar2_30d = share_data.iloc[-1,-1]*np.cumprod(1+ar2_for30d)
snp_prices_ar3_30d = share_data.iloc[-1,-1]*np.cumprod(1+ar3_for30d)    
#%%
print(ar1_mdl.params)
print(ar2_mdl.params)
#%%

#%%
"""
predictie a randamentelor si preturilor celor 5 actiuni pe urmatoarele 10, 20, resp 30 de zile
folosind AR(1), AR(2), AR(3)
"""
ar_mdls_1 = [sm.tsa.ARIMA(share_returns.iloc[:,i],order = (1,0,0)).fit() for i in range(0,5)]
ar_mdls_2 = [sm.tsa.ARIMA(share_returns.iloc[:,i],order = (2,0,0)).fit() for i in range(0,5)]
ar_mdls_3 = [sm.tsa.ARIMA(share_returns.iloc[:,i],order = (3,0,0)).fit() for i in range(0,5)]

ar_for10d = [ar_mdls_1[i].forecast(10) for i in range(0,5)]
ar_for20d = [ar_mdls_1[i].forecast(20) for i in range (0,5)]
ar_for30d = [ar_mdls_1[i].forecast(30) for i in range(0,5)]   

ar2_for10d = [ar_mdls_2[i].forecast(10) for i in range(0,5)]
ar2_for20d = [ar_mdls_2[i].forecast(20) for i in range(0,5)]
ar2_for30d = [ar_mdls_2[i].forecast(30) for i in range(0,5)]

ar3_for10d = [ar_mdls_3[i].forecast(10) for i in range(0,5)]
ar3_for20d = [ar_mdls_3[i].forecast(20) for i in range(0,5)]
ar3_for30d = [ar_mdls_3[i].forecast(30) for i in range(0,5)]

stock_prices_ar1_10d = [share_data.iloc[-1,i]*np.cumprod(1+ar_for10d[i]) for i in range(0,5)]
stock_prices_ar1_20d = [share_data.iloc[-1,i]*np.cumprod(1+ar_for20d[i]) for i in range(0,5)]
stock_prices_ar1_30d = [share_data.iloc[-1,i]*np.cumprod(1+ar_for30d[i]) for i in range(0,5)]

stock_prices_ar2_10d = [share_data.iloc[-1,i]*np.cumprod(1+ar2_for10d[i]) for i in range(0,5)]
stock_prices_ar2_20d = [share_data.iloc[-1,i]*np.cumprod(1+ar2_for20d[i]) for i in range(0,5)]
stock_prices_ar2_30d = [share_data.iloc[-1,i]*np.cumprod(1+ar2_for30d[i]) for i in range(0,5)]

stock_prices_ar3_10d = [share_data.iloc[-1,i]*np.cumprod(1+ar3_for10d[i]) for i in range(0,5)]
stock_prices_ar3_20d = [share_data.iloc[-1,i]*np.cumprod(1+ar3_for20d[i]) for i in range(0,5)]
stock_prices_ar3_30d = [share_data.iloc[-1,i]*np.cumprod(1+ar3_for30d[i]) for i in range(0,5)]

# %%
