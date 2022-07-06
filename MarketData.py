import requests 
import sqlalchemy as db
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


inputs = input("Input ticker symbols you would like to know more about (up to 10, seperated by spaces):\n")
querystrings = inputs.split()

def to_string(qlist):
    string = ""
    #TODO you can check if they are already preasent in the data base, as a default all tickers will have a 1 month data range in the interval of 5 mins
    #any time under that can be filtered in a search and any time overthat becomes uncertain in the data provided
    for query in qlist:
        if qlist.index(query) == (len(qlist) - 1):
            string += query.upper()
        else:
            string += query.upper() + ","
    return string

url = "https://yfapi.net/v8/finance/spark"

querystring = {"range":"1mo", "symbols":to_string(querystrings)}

headers = {
    'x-api-key': "UULSxaV3C11PcBPvYr2co1z9Vc9UESaZ4KFGUNFJ"
    }

response = requests.request("GET", url, headers=headers, params=querystring)
response = response.json()

engine = db.create_engine('sqlite:///Market_Data.db')
for ticker in response:
    for i in range(0, len(response[ticker]["timestamp"])):
        usabledata = {}
        usabledata["timestamp"] = response[ticker]["timestamp"][i]
        usabledata["close"] = response[ticker]["close"][i]
        dataframe = pd.DataFrame.from_dict([usabledata])
        dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"], unit='s')
        dataframe.to_sql(ticker, con=engine, if_exists='append', index=False)
