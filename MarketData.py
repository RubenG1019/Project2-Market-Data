import yfinance as yf
import requests
import sqlalchemy as db
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import colorama
from colorama import Fore, Back, Style


colorama.init(autoreset=True)
 
print(Fore.RED + Style.BRIGHT + "Not financial advise, invest at your own risk.")
print(Fore.RED + Style.BRIGHT + "Note: Longer timeframes are more indicative of general trends, looking at what a stock does in 5 min intervals during the day wont reflect how it reacts next week")
inputstring = str(input("Input a ticker symbol you would like to know more about (Ex: aapl, jpm, btc-usd, msft):\n"))
querystring = inputstring.upper()
timeperiod = input("Enter a time period (Ex: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max):\n")
timeinterval = input("Enter a time interval (Ex: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo):\n")

engine = db.create_engine('sqlite:///Market_Data.db')


ticker = yf.Ticker(querystring)
# get historical market data
hist = ticker.history(period = timeperiod, interval = timeinterval)
hist = hist.reset_index(level = 0)
if 'index' in hist:
    hist.rename(columns = {'index':'Date'}, inplace = True)
if 'Datetime' in hist:
    hist.rename(columns = {'Datetime':'Date'}, inplace = True)
hist.to_sql(querystring.replace("-", ""), con=engine, if_exists='replace', index=False)


def get_recs(symbol, print_recs=True):
    headers = {
    'x-api-key': "UULSxaV3C11PcBPvYr2co1z9Vc9UESaZ4KFGUNFJ"
    }
   
    base_rec_url = "https://yfapi.net/v6/finance/recommendationsbysymbol/"
    
    rec_dict = {}
    rec_url = base_rec_url + symbol.upper()
    recs = requests.request("GET", rec_url,
                            headers=headers)
    recs.raise_for_status()
    rec_dict[symbol] = recs.json()

    print('Recommended stocks given your prefrences:', end = " ")
    
    for ticker in rec_dict[querystring]['finance']['result'][0]['recommendedSymbols']:
        print(Fore.CYAN + Style.BRIGHT + ticker['symbol'], end = " ")
    print()



def info_statement():
    print(Fore.YELLOW + Style.BRIGHT + "You have chosen the ticker symbol " + querystring + " or " + ticker.info['shortName'])
    if ticker.info['quoteType'] == "CRYPTOCURRENCY":

        print(Fore.YELLOW + Style.BRIGHT + ticker.info['shortName'] + " is a Crypto-Currency with a Market Cap of " + str(ticker.info['marketCap']) + " and has a circulating supply of " + str(ticker.info['circulatingSupply']))

        print("Change over the " + timeperiod + " timespan: ", end = '')
        temp = hist['Close'].to_dict()
        percentchange = ((temp[len(temp)-1] - temp[0]) / temp[0]) * 100
        if percentchange > 0:
            print(Fore.GREEN + Style.BRIGHT + "" + str(percentchange) + "%")
        else:
            print(Fore.RED + Style.BRIGHT + "" + str(percentchange) + "%")

    else:    
        try:
            print(Fore.YELLOW + Style.BRIGHT + ticker.info['shortName'] + " is in the " + ticker.info['sector'] + " sector and the " + ticker.info['industry'] + " industry and has a market cap of " + str(ticker.info['marketCap']) + " and is based in " + ticker.info['city'] + ", " + ticker.info['country'])
        except:
            print("", end="")
        try:
            print(Fore.YELLOW + Style.BRIGHT + ticker.info['shortName'] + " is currently trading at " + str(ticker.info['currentPrice']) + " and has " + str(ticker.info['floatShares']) + " shares outstanding")
        except:
            print("", end="")
        try:
            print(Fore.YELLOW + Style.BRIGHT + ticker.info['shortName'] + " currently has a " + ticker.info['recommendationKey'] + " rating.\n")
        except:
            print("", end="")
        try:
            if ticker.info['52WeekChange'] != None:
                print("Yearly Change: ", end = '')
                if ticker.info['52WeekChange'] > 0:
                    print(Fore.GREEN + Style.BRIGHT + "" + str(ticker.info['52WeekChange'] * 100) + "%")
                else:
                    print(Fore.RED + Style.BRIGHT + "" + str(ticker.info['52WeekChange'] * 100) + "%")
        except:
            print("", end="")

        try:
            if timeperiod != "1y":
                print("Change over the " + timeperiod + " timespan: ", end = '')
                temp = hist['Close'].to_dict()
                percentchange = ((temp[len(temp)-1] - temp[0]) / temp[0]) * 100
                if percentchange > 0:
                    print(Fore.GREEN + Style.BRIGHT + "" + str(percentchange) + "%")
                else:
                    print(Fore.RED + Style.BRIGHT + "" + str(percentchange) + "%")
        except:
            print("", end="")
    
        try:
            if ticker.info['regularMarketVolume'] != None:
                print("Regular Market Volume: ", end = '')
                if ticker.info['regularMarketVolume'] >= 1000000:
                    print(Fore.GREEN + Style.BRIGHT + "" + str(ticker.info['regularMarketVolume']), end = "")
                else:
                    print(Fore.RED + Style.BRIGHT + "" + str(ticker.info['regularMarketVolume']), end = "")
                print(" (Above 1 Million is ideal, lower means the stock lacks liquidity)\n")
        except:
            print("", end="")
        try:   
            if ticker.info['operatingMargins'] != None:
                print("Operating Margin: ", end = '')
                if ticker.info['operatingMargins'] >= .15:
                    print(Fore.GREEN + Style.BRIGHT + "" + str(ticker.info['operatingMargins'] * 100) + "%", end = "")
                else:
                    print(Fore.RED + Style.BRIGHT + "" + str(ticker.info['operatingMargins'] * 100) + "%", end = "")
                print(" (Above 15% is ideal for most buisnesses, positive margins are a bare minimum)\n")
        except:
            print("", end="")
        try:
            if ticker.info['heldPercentInstitutions'] != None:
                print("Institutional Holdership: ", end = '')
                if ticker.info['heldPercentInstitutions'] >= .20:
                    print(Fore.GREEN + Style.BRIGHT + "" + str(ticker.info['heldPercentInstitutions'] * 100) + "%", end = "")
                else:
                    print(Fore.RED + Style.BRIGHT + "" + str(ticker.info['heldPercentInstitutions'] * 100) + "%", end = "")
                print(" (Percent of shares Institutions/Hedgefunds like BlackRock (Smart Money) are holding, these institutions have billions and thousands of analysts working for them anything above 20% is good)\n")
        except: 
            print("", end="")
        try: 
            if ticker.info['shortPercentOfFloat'] != None:
                print("Percentage of shares short: ", end = '')
                if ticker.info['shortPercentOfFloat'] < .20:
                    print(Fore.GREEN + Style.BRIGHT + "" + str(ticker.info['shortPercentOfFloat'] * 100) + "%", end = "")
                else:
                    print(Fore.RED + Style.BRIGHT + "" + str(ticker.info['shortPercentOfFloat'] * 100) + "%", end = "")
                print(" (Long story short, less is good, the higher this percentage the more the Smart Money think this stock is overvalued under 20% good.)\n")
        except:
            print("", end="")
        try:
            if ticker.info['trailingPE'] != None:
                print("Price to Earning Ratio: ", end = '')
                if ticker.info['trailingPE'] <= 25:
                    print(Fore.GREEN + Style.BRIGHT + "" + str(ticker.info['trailingPE']), end = "")
                else:
                    print(Fore.RED + Style.BRIGHT + "" + str(ticker.info['trailingPE']), end = "")
                print(" (If price to earning ratio is over 25 the stock is likely overvalued far under means its undervalued, useful metric for value investing)\n")
        except:
            print("", end="")
        try:
            if ticker.info['dividendYield'] != None:
                if ticker.info['trailingPE'] <= 25:
                    print(Fore.GREEN + Style.BRIGHT + ticker.info['shortName'] + " gives a dividend of " + str(ticker.info['dividendYield'] * 100) + "% the share price " + str(ticker.info['dividendRate']) + " times a year", end = "")
            else:
                print(Fore.RED + Style.BRIGHT + ticker.info['shortName'] + " does not give out a dividend", end = '')
            print(" (Dividends are like a gift companies give to their investors for holding shares of their stock. They are programmed a certain number of times a year and pay you a set percentage of the current share price)\n")
        except:
            print("", end="")


info_statement()
q_string_recs = get_recs(querystring)



query_result = engine.execute("SELECT Date,Close FROM " + querystring.replace("-", "") + ";").fetchall()

datadict = pd.DataFrame(query_result)
datadict.set_index(0, inplace=True)
