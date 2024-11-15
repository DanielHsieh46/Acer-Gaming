#!/usr/bin/env python
# coding: utf-8

# In[7]:


import requests
import pandas as pd
from bs4 import BeautifulSoup
import yfinance as yf

#數據轉換
def parse_value(element):
    if element:
        value = float(element.get_text(strip=True).replace(",", ""))
        if element.get("sign") == "-":
            value = -value
        return value
    else:
        value = 0
        return value
    
#從 yfinance 取得股價  
def grabstock(ticker):
    try:
        try:
            stock_name = ticker + ".TW"
            data = yf.Ticker(stock_name)
            latest_price = data.history(period="1d")["Close"].iloc[-1]
        except:
            stock_name = ticker + ".TWO"
            data = yf.Ticker(stock_name)
            latest_price = data.history(period="1d")["Close"].iloc[-1]
    except:
        latest_price = ""
    return latest_price

#從 yfinance 取得流通在外股數
def grabshares(ticker):
    exchanges = [".TW", ".TWO"]
    for exchange in exchanges:
        stock_name = ticker + exchange
        data = yf.Ticker(stock_name)
        info = data.info
        shares_outstanding = info.get('sharesOutstanding')
        if shares_outstanding:
            return shares_outstanding
    return ""

#從 yfinance 取得發放股利
def grab_dividend_per_year(ticker, year):
    exchanges = [".TW", ".TWO"]
    for exchange in exchanges:
        stock_name = ticker + exchange
        data = yf.Ticker(stock_name)       
        dividends = data.dividends
        if not dividends.empty:  
            yearly_dividends = dividends[dividends.index.year == year]
            
            if not yearly_dividends.empty:
                total_dividends = yearly_dividends.sum()  
                return total_dividends    
    return ""  

#日期輸入邏輯
target_season = "2024,Q2"  #可變部分
current_yr = target_season.split(",")[0]
prior_yr = str(int(current_yr) - 1)

if target_season.split(",")[1] == "Q2":
    url_date = "&SYEAR=" + current_yr +"&SSEASON=2&REPORT_ID=C"
    url2_date = "&SYEAR=" + prior_yr +"&SSEASON=4&REPORT_ID=C"
    IS_Range = "From" + current_yr + "0101To" + current_yr +"0630"
    Prior_IS_Range = "From" + prior_yr + "0101To" + prior_yr +"1231"
    End_BS_Date = 'AsOf' + current_yr + '0630'
    Beg_BS_Date = 'AsOf' + prior_yr + '1231'
    HY_Multiplier = 2
    
elif target_season.split(",")[1] == "Q4":
    url_date = "&SYEAR=" + current_yr +"&SSEASON=4&REPORT_ID=C"
    url2_date = "&SYEAR=" + prior_yr +"&SSEASON=4&REPORT_ID=C"
    IS_Range = "From" + current_yr + "0101To" + current_yr +"1231"
    Prior_IS_Range = "From" + prior_yr + "0101To" + prior_yr +"1231"
    End_BS_Date = 'AsOf' + current_yr + '1231'
    Beg_BS_Date = 'AsOf' + prior_yr + '1231'   
    HY_Multiplier = 1
else:
    print("only support half year or full year report")

#主程式

t_dict = {
    "6908": "宏碁遊戲",
    "2353": "宏碁",
    "6776": "展碁國際",
    "2347": "聯強國際",
    "6180": "橘子",
    "3546": "宇峻奧汀",
    "5478": "智冠科技",
    "4946": "辣椒娛樂",
    "6111": "大宇資"
}#可變部分

t_list = [i for i in t_dict.keys()] 
index_list = [f"{key} {value}" for key, value in t_dict.items()]


data = {"營業毛利率": [],
        "營業利益率": [],
        "淨利率": [],
        "EPS": [],
        "ROA":[],
        "ROE":[],
        "Dupont: 淨利率":[],
        "Dupont: 資產周轉率":[],
        "Dupont: 財務槓桿": [],
        "存貨周轉率": [],
        "應收帳款周轉率": [],
        "總資產周轉率": [],
        "總資產": [],
        "負債(%)": [],
        "權益(%)": [],
        "PE Ratio": [],
        "PB Ratio": [],
        "本年度發放股利": [],
        "前年度eps": [],
        "股利發放率": []
       } 

for company in t_list:
    url = "https://mops.twse.com.tw/server-java/t164sb01?step=1&CO_ID=" + company + url_date
    url2 = "https://mops.twse.com.tw/server-java/t164sb01?step=1&CO_ID=" + company + url2_date

    response = requests.get(url)
    response2 = requests.get(url2)
    

    if response.status_code == 200 and response2.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        soup2 = BeautifulSoup(response2.text, 'html.parser')
        
        #爬需要的數據
        Revenue = soup.find('ix:nonfraction', {'name': 'ifrs-full:Revenue','contextref': IS_Range,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})
        Gross_Profit = soup.find('ix:nonfraction', {'name': 'ifrs-full:GrossProfit','contextref': IS_Range,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})
        PL_From_OA = soup.find('ix:nonfraction', {'name': 'ifrs-full:ProfitLossFromOperatingActivities','contextref': IS_Range,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})
        Net_Income = soup.find('ix:nonfraction', {'name': 'ifrs-full:ProfitLossFromContinuingOperations','contextref': IS_Range,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})
        EPS = soup.find('ix:nonfraction', {'name': 'ifrs-full:BasicEarningsLossPerShare','contextref': IS_Range,'format': 'ixt:numdotdecimal','scale': '0','decimals': '2','unitref': 'EarningsPerShare'})
        End_Asset = soup.find('ix:nonfraction', {'name': 'ifrs-full:Assets','contextref': End_BS_Date,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})
        Beg_Asset = soup.find('ix:nonfraction', {'name': 'ifrs-full:Assets','contextref': Beg_BS_Date,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})
        End_Equity = soup.find('ix:nonfraction', {'name': 'ifrs-full:Equity','contextref': End_BS_Date,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})        
        Beg_Equity = soup.find('ix:nonfraction', {'name': 'ifrs-full:Equity','contextref': Beg_BS_Date,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})
        COGS = soup.find('ix:nonfraction', {'name': 'tifrs-bsci-ci:OperatingCosts','contextref': IS_Range,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})
        End_Inventory = soup.find('ix:nonfraction', {'name': 'ifrs-full:Inventories','contextref': End_BS_Date,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})
        Beg_Inventory = soup.find('ix:nonfraction', {'name': 'ifrs-full:Inventories','contextref': Beg_BS_Date,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})
        End_AR = soup.find('ix:nonfraction', {'name': 'tifrs-bsci-ci:AccountsReceivableNet','contextref': End_BS_Date,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})        
        Beg_AR = soup.find('ix:nonfraction', {'name': 'tifrs-bsci-ci:AccountsReceivableNet','contextref': Beg_BS_Date,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})
        End_AR_RP = soup.find('ix:nonfraction', {'name': 'tifrs-bsci-ci:AccountsReceivableDuefromRelatedPartiesNet','contextref': End_BS_Date,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})        
        Beg_AR_RP = soup.find('ix:nonfraction', {'name': 'tifrs-bsci-ci:AccountsReceivableDuefromRelatedPartiesNet','contextref': Beg_BS_Date,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})        
        End_Liabi = soup.find('ix:nonfraction', {'name': 'ifrs-full:Liabilities','contextref': End_BS_Date,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})        
        Stock_Price = grabstock(company) #只能取最新數據
        End_NCI = soup.find('ix:nonfraction', {'name': 'ifrs-full:NoncontrollingInterests','contextref': End_BS_Date,'format': 'ixt:numdotdecimal','scale': '3','decimals': '-3','unitref': 'TWD'})        
        Shares = grabshares(company) #只能取最新數據
        Dividend = grab_dividend_per_year(company, int(current_yr))
        Prior_EPS = soup2.find('ix:nonfraction', {'name': 'ifrs-full:BasicEarningsLossPerShare','contextref': Prior_IS_Range,'format': 'ixt:numdotdecimal','scale': '0','decimals': '2','unitref': 'EarningsPerShare'})
        
        
        #數據轉換
        Revenue = parse_value(Revenue)
        Gross_Profit = parse_value(Gross_Profit)
        PL_From_OA = parse_value(PL_From_OA)
        Net_Income = parse_value(Net_Income)
        EPS = parse_value(EPS)
        End_Asset = parse_value(End_Asset)
        Beg_Asset = parse_value(Beg_Asset)
        End_Equity = parse_value(End_Equity)
        Beg_Equity = parse_value(Beg_Equity)  
        COGS = parse_value(COGS)
        End_Inventory =  parse_value(End_Inventory)
        Beg_Inventory =  parse_value(Beg_Inventory)
        End_AR = parse_value(End_AR)
        Beg_AR = parse_value(Beg_AR)
        End_AR_RP = parse_value(End_AR_RP)
        Beg_AR_RP = parse_value(Beg_AR_RP)
        End_Liabi = parse_value(End_Liabi)
        End_NCI = parse_value(End_NCI)
        Prior_EPS = parse_value(Prior_EPS)


        
        #計算財務指標
        try:
            Gross_Margin = 100 * Gross_Profit / Revenue
        except:
            Gross_Margin = ""

        try:
            Operating_Profit_Margin = 100 * PL_From_OA / Revenue
        except:
            Operating_Profit_Margin = ""

        try:
            Net_Profit_Margin = 100 * Net_Income / Revenue
        except:
            Net_Profit_Margin = ""

        try:
            ROA = 100 * Net_Income / ((Beg_Asset + End_Asset) / 2)
        except:
            ROA = ""

        try:
            ROE = 100 * Net_Income / ((Beg_Equity + End_Equity) / 2)
        except:
            ROE = ""

        try:
            Asset_Turnover = Revenue / ((Beg_Asset + End_Asset) / 2)
        except:
            Asset_Turnover = ""

        try:
            Financial_Leverage = ((Beg_Asset + End_Asset) / 2) / ((Beg_Equity + End_Equity) / 2)
        except:
            Financial_Leverage = ""

        try:
            Inventory_Turnover = HY_Multiplier * COGS / ((Beg_Inventory + End_Inventory) / 2)
        except:
            Inventory_Turnover = ""
            
        try:
            AR_Turnover = HY_Multiplier * Revenue / ((Beg_AR + Beg_AR_RP + End_AR + End_AR_RP)/2)
        except:
            AR_Turnover = ""
        
        try:
            Debt_Ratio = 100 * End_Liabi / End_Asset
        except:
            Debt_Ratio = ""
        
        try: 
            Equity_Ratio = 100 * End_Equity / End_Asset
        except:
            Equity_Ratio = ""
            
        try:
            PE_Ratio = Stock_Price / EPS
        except:
            PE_Ratio = ""
            
        try: 
            PB_Ratio = Stock_Price / (1000 * (End_Equity - End_NCI) / Shares)
        except:
            PB_Ratio = ""
            
        try: 
            Dividend_Payout_Ratio = 100 * Dividend / Prior_EPS
        except:
            Dividend_Payout_Ratio = ""


        data["營業毛利率"].append(Gross_Margin)
        data["營業利益率"].append(Operating_Profit_Margin)
        data["淨利率"].append(Net_Profit_Margin)
        data["EPS"].append(EPS)
        data["ROA"].append(ROA)
        data["ROE"].append(ROE)
        data["Dupont: 淨利率"].append(Net_Profit_Margin)
        data["Dupont: 資產周轉率"].append(Asset_Turnover)
        data["Dupont: 財務槓桿"].append(Financial_Leverage)
        data["存貨周轉率"].append(Inventory_Turnover)
        data["應收帳款周轉率"].append(AR_Turnover)
        data["總資產周轉率"].append(Asset_Turnover)
        data["總資產"].append(End_Asset)
        data["負債(%)"].append(Debt_Ratio)
        data["權益(%)"].append(Equity_Ratio)
        data["PE Ratio"].append(PE_Ratio)
        data["PB Ratio"].append(PB_Ratio)
        data["本年度發放股利"].append(Dividend)
        data["前年度eps"].append(Prior_EPS)
        data["股利發放率"].append(Dividend_Payout_Ratio)
            
        
    else:
        print("Failed")
        
df_origin = pd.DataFrame(data, index = index_list).T
df2 = pd.DataFrame(data, index = index_list)

df_origin.to_excel('output.xlsx', index=True)
df2.to_excel('output_2.xlsx', index=True)
print("Successfully Saved!!!")


# In[ ]:




