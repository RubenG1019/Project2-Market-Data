import yfinance as yf
import requests
import sqlalchemy as db
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import colorama
from json import dumps
from colorama import Fore, Back, Style


colorama.init(autoreset=True)

# Warnings for user
print(Fore.RED + Style.BRIGHT +
      "Not financial advise, invest at your own risk.")
print(Fore.RED + Style.BRIGHT +
      "Note: Longer timeframes are more indicative of general trends, "
      "looking at what a stock does in 5 min intervals during the day "
      "wont reflect how it reacts next week")

# Prompt user for stock, time interval, and range
inputstring = str(input(
    "Input a ticker symbol you would like to know more about"
    " (Ex: aapl, jpm, btc-usd, msft):\n"))
querystring = inputstring.upper()
timeperiod = input("Enter a time period "
                   "(Ex: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max):\n")
timeinterval = input("Enter a time interval "
                     "(Ex: 1m, 2m, 5m, 15m, 30m, 60m, 90m, "
                     "1h, 1d, 5d, 1wk, 1mo, 3mo):\n")
# Ask user if they want to overwrite the existing database
overwrite = input("Do you want to overwrite the existing Market_Data database?"
                  "\nTrue / False: ")
if overwrite == "True":
    overwrite = True
else:
    overwrite = False


# Create ticker object for given stock, used  for retrieving all stock info
ticker = yf.Ticker(querystring)
# get historical market data
hist = ticker.history(period=timeperiod, interval=timeinterval)
hist = hist.reset_index(level=0)
if 'index' in hist:
    hist.rename(columns={'index': 'Date'}, inplace=True)
if 'Datetime' in hist:
    hist.rename(columns={'Datetime': 'Date'}, inplace=True)

if overwrite:
    # Create SQL database to store data in
    engine = db.create_engine('sqlite:///Market_Data.db')

    # store historical data in SQL database
    hist.to_sql(querystring.replace("-", ""), con=engine,
                if_exists='replace', index=False)


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

    if print_recs:
        print('Recommended stocks given your prefrences:', end=" ")

        r = rec_dict[querystring]['finance']['result'][0]['recommendedSymbols']
        for ticker in r:
            print(Fore.CYAN + Style.BRIGHT + ticker['symbol'], end=" ")
        print()

    return rec_dict


def get_usinflation():
    tp = 'CPI'
    api_url = 'https://api.api-ninjas.com/v1/inflation?type={}'.format(tp)
    response = requests.get(
        api_url, headers={
            'X-Api-Key': 'DHYTMZd4WuLvBig6WTIL7A==VlveuMZSuKschXBi'})
    return response.json()


def info_statement():
    print(
        Fore.YELLOW +
        Style.BRIGHT +
        "You have chosen the ticker symbol " +
        querystring +
        " or " +
        ticker.info['shortName'])

    if ticker.info['quoteType'] == "CRYPTOCURRENCY":
        # User asked for info about a crypto currency
        print(Fore.YELLOW +
              Style.BRIGHT +
              ticker.info['shortName'] +
              " is a Crypto-Currency with a Market Cap of " +
              str(ticker.info['marketCap']) +
              " and has a circulating supply of " +
              str(ticker.info['circulatingSupply']))

        print("Change over the " + timeperiod + " timespan: ", end='')
        temp = hist['Close'].to_dict()
        percentchange = ((temp[len(temp) - 1] - temp[0]) / temp[0]) * 100
        if percentchange > 0:
            print(Fore.GREEN + Style.BRIGHT + "" + str(percentchange) + "%")
        else:
            print(Fore.RED + Style.BRIGHT + "" + str(percentchange) + "%")

    else:
        # User asked for info about a stock
        try:
            # Print the name of the stock and its general information
            print(Fore.YELLOW +
                  Style.BRIGHT +
                  ticker.info['shortName'] +
                  " is in the " +
                  ticker.info['sector'] +
                  " sector and the " +
                  ticker.info['industry'] +
                  " industry and has a market cap of " +
                  str(ticker.info['marketCap']) +
                  " and is based in " +
                  ticker.info['city'] +
                  ", " +
                  ticker.info['country'])
        except BaseException:
            print("", end="")

        try:
            # Print the stock's current information
            print(Fore.YELLOW +
                  Style.BRIGHT +
                  ticker.info['shortName'] +
                  " is currently trading at " +
                  str(ticker.info['currentPrice']) +
                  " and has " +
                  str(ticker.info['floatShares']) +
                  " shares outstanding")
        except BaseException:
            print("", end="")

        try:
            # Print the stock's rating
            print(
                Fore.YELLOW +
                Style.BRIGHT +
                ticker.info['shortName'] +
                " currently has a " +
                ticker.info['recommendationKey'] +
                " rating.\n")
        except BaseException:
            print("", end="")

        try:
            # Print the stock's yearly change percentage
            if ticker.info['52WeekChange'] is not None:
                print("Yearly Change: ", end='')
                if ticker.info['52WeekChange'] > 0:
                    print(Fore.GREEN + Style.BRIGHT + "" +
                          str(ticker.info['52WeekChange'] * 100) + "%")
                else:
                    print(Fore.RED + Style.BRIGHT + "" +
                          str(ticker.info['52WeekChange'] * 100) + "%")
        except BaseException:
            print("", end="")

        try:
            # Print the change on the user-provided time interval/period/span
            if timeperiod != "1y":
                print("Change over the " + timeperiod + " timespan: ", end='')
                temp = hist['Close'].to_dict()
                percentchange = (
                    (temp[len(temp) - 1] - temp[0]) / temp[0]) * 100
                if percentchange > 0:
                    print(
                        Fore.GREEN +
                        Style.BRIGHT +
                        "" +
                        str(percentchange) +
                        "%")
                else:
                    print(
                        Fore.RED +
                        Style.BRIGHT +
                        "" +
                        str(percentchange) +
                        "%")
        except BaseException:
            print("", end="")

        try:
            # Print stock's Regular Market Volume
            if ticker.info['regularMarketVolume'] is not None:
                print("Regular Market Volume: ", end='')
                if ticker.info['regularMarketVolume'] >= 1000000:
                    print(Fore.GREEN + Style.BRIGHT + "" +
                          str(ticker.info['regularMarketVolume']), end="")
                else:
                    print(Fore.RED + Style.BRIGHT + "" +
                          str(ticker.info['regularMarketVolume']), end="")
                print(
                    " (Above 1 Million is ideal,"
                    " lower means the stock lacks liquidity)\n")
        except BaseException:
            print("", end="")

        try:
            # Print stock's operating margin
            if ticker.info['operatingMargins'] is not None:
                print("Operating Margin: ", end='')
                if ticker.info['operatingMargins'] >= .15:
                    print(Fore.GREEN + Style.BRIGHT + "" +
<<<<<<< HEAD
                          str(ticker.info['operatingMargins'] * 100) + "%", end="")
                else:
                    print(Fore.RED + Style.BRIGHT + "" +
                          str(ticker.info['operatingMargins'] * 100) + "%", end="")
=======
                          str(ticker.info['operatingMargins'] * 100) + "%",
                          end="")
                else:
                    print(Fore.RED + Style.BRIGHT + "" +
                          str(ticker.info['operatingMargins'] * 100) + "%",
                          end="")
>>>>>>> 21001822b8cb142c2f5fd7c245d369f37bae0352
                print(
                    " (Above 15% is ideal for most buisnesses, positive",
                    " margins are a bare minimum)\n")
        except BaseException:
            print("", end="")

        try:
            # Print the percentage of the stock that are held by institutions
            if ticker.info['heldPercentInstitutions'] is not None:
                print("Institutional Holdership: ", end='')
                if ticker.info['heldPercentInstitutions'] >= .20:
                    print(Fore.GREEN +
                          Style.BRIGHT +
                          "" +
                          str(ticker.info['heldPercentInstitutions'] *
                              100) +
                          "%", end="")
                else:
                    print(Fore.RED +
                          Style.BRIGHT +
                          "" +
                          str(ticker.info['heldPercentInstitutions'] *
                              100) +
                          "%", end="")
                print(" (Percent of shares Institutions/Hedgefunds like"
                      " BlackRock (Smart Money) are holding, these"
                      " institutions have billions and thousands of analysts"
                      " working for them anything above 20% is good)\n")
        except BaseException:
            print("", end="")

        try:
            # Print percentage of shares that are shorted
            if ticker.info['shortPercentOfFloat'] is not None:
                print("Percentage of shares short: ", end='')
                if ticker.info['shortPercentOfFloat'] < .20:
                    print(Fore.GREEN +
                          Style.BRIGHT +
                          "" +
                          str(ticker.info['shortPercentOfFloat'] *
                              100) +
                          "%", end="")
                else:
                    print(Fore.RED +
                          Style.BRIGHT +
                          "" +
                          str(ticker.info['shortPercentOfFloat'] *
                              100) +
                          "%", end="")
                print(" (Long story short, less is good, the higher this"
                      " percentage the more the Smart Money think this stock"
                      " is overvalued under 20% good.)\n")
        except BaseException:
            print("", end="")

        try:
            # Print the stock's earning ratio
            if ticker.info['trailingPE'] is not None:
                print("Price to Earning Ratio: ", end='')
                if ticker.info['trailingPE'] <= 25:
                    print(Fore.GREEN + Style.BRIGHT + "" +
                          str(ticker.info['trailingPE']), end="")
                else:
                    print(Fore.RED + Style.BRIGHT + "" +
                          str(ticker.info['trailingPE']), end="")
                print(" (If price to earning ratio is over 25 the stock is"
                      " likely overvalued far under means its undervalued,"
                      " useful metric for value investing)\n")
        except BaseException:
            print("", end="")

        try:
            # Print the stock's dividends
            if ticker.info['dividendYield'] is not None:
                if ticker.info['trailingPE'] <= 25:
                    print(Fore.GREEN +
                          Style.BRIGHT +
                          ticker.info['shortName'] +
                          " gives a dividend of " +
                          str(ticker.info['dividendYield'] *
                              100) +
                          "% the share price " +
                          str(ticker.info['dividendRate']) +
                          " times a year", end="")
            else:
                print(
                    Fore.RED +
                    Style.BRIGHT +
                    ticker.info['shortName'] +
                    " does not give out a dividend",
                    end='')
            print(" (Dividends are like a gift companies give to their"
                  " investors for holding shares of their stock. They are"
                  " programmed a certain number of times a year and pay you a"
                  " set percentage of the current share price)\n")
        except BaseException:
            print("", end="")


info_statement()

<<<<<<< HEAD
print(
    Fore.YELLOW +
    Style.BRIGHT +
    "US Major Market Indices during the " +
    timeperiod +
    " timeframe:\n")

print("NASDAQ: ", end='')

tick1 = yf.Ticker("^IXIC")
hist1 = tick1.history(period=timeperiod)
hist1 = hist1.reset_index(level=0)
temp1 = hist1['Close'].to_dict()
percentchange = ((temp1[len(temp1) - 1] - temp1[0]) / temp1[0]) * 100
if percentchange > 0:
    print(
        Fore.GREEN +
        Style.BRIGHT +
        "" +
        str(percentchange) +
        "%")
else:
    print(
        Fore.RED +
        Style.BRIGHT +
        "" +
        str(percentchange) +
        "%")


print("S&P 500: ", end='')
tick1 = yf.Ticker("^GSPC")
hist1 = tick1.history(period=timeperiod)
hist1 = hist1.reset_index(level=0)
temp1 = hist1['Close'].to_dict()
percentchange = ((temp1[len(temp1) - 1] - temp1[0]) / temp1[0]) * 100
if percentchange > 0:
    print(
        Fore.GREEN +
        Style.BRIGHT +
        "" +
        str(percentchange) +
        "%")
else:
    print(
        Fore.RED +
        Style.BRIGHT +
        "" +
        str(percentchange) +
        "%")

print("DOW Jones: ", end='')
tick1 = yf.Ticker("^DJI")
hist1 = tick1.history(period=timeperiod)
hist1 = hist1.reset_index(level=0)
temp1 = hist1['Close'].to_dict()
percentchange = ((temp1[len(temp1) - 1] - temp1[0]) / temp1[0]) * 100
if percentchange > 0:
    print(
        Fore.GREEN +
        Style.BRIGHT +
        "" +
        str(percentchange) +
        "%")
else:
    print(
        Fore.RED +
        Style.BRIGHT +
        "" +
        str(percentchange) +
        "%")
print()
print("In general stocks follow the trend of the index they fall under (tech stocks like AAPL(Apple) fall under the NASDAQ) if the major indices are down most stocks will follow.")
print()
inflationdata = get_usinflation()

print(Fore.YELLOW + Style.BRIGHT + "Inflation Data US for the " +
      inflationdata[-1]['period'] + ":\n")
print("Yearly Rate: ", end="")
if inflationdata[-1]['yearly_rate_pct'] < 2.5:
    print(
        Fore.GREEN +
        Style.BRIGHT +
        "" +
        str(inflationdata[-1]['yearly_rate_pct']) +
        "%")
else:
    print(
        Fore.RED +
        Style.BRIGHT +
        "" +
        str(inflationdata[-1]['yearly_rate_pct']) +
        "%")

print("Monthly Rate: ", end="")
if inflationdata[-1]['monthly_rate_pct'] < 0:
    print(
        Fore.GREEN +
        Style.BRIGHT +
        "" +
        str(inflationdata[-1]['monthly_rate_pct']) +
        "%")
else:
    print(
        Fore.RED +
        Style.BRIGHT +
        "" +
        str(inflationdata[-1]['monthly_rate_pct']) +
        "%")
print()
print("High inflation rates are followed by higher intrest rates, high intrest rates devalues stock, therefore high inflation rates are bad for the stock market")
print()
get_recs(querystring)
=======
if overwrite:
    # Query info from the SQL database
    query_result = engine.execute(
                            "SELECT Date, Close FROM " +
                            querystring.replace("-", "") + ";").fetchall()

    datadict = pd.DataFrame(query_result)
    # datadict.set_index(0, inplace=True)
    print(datadict)
>>>>>>> 21001822b8cb142c2f5fd7c245d369f37bae0352

data = hist[["Date", "Open"]]

<<<<<<< HEAD
datadict = pd.DataFrame(query_result)
datadict.set_index(0, inplace=True)

datadict.plot(figsize=(16, 9))
plt.xlabel('Date')
plt.ylabel('Price')
plt.savefig(querystring + ".png")
plt.ioff()
plt.show(block=False)
=======
plt.plot(data["Date"], data["Open"])
plt.title(ticker.info['shortName'] + ' Performance '
          'over ' + timeperiod)
plt.ylabel('Price ($)')
plt.xlabel('Date')
plt.show()
>>>>>>> 21001822b8cb142c2f5fd7c245d369f37bae0352
