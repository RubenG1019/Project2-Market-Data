import requests
import json
import sqlalchemy as db
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


inputs = input("Input ticker symbols you would like to know more about\
                (up to 10, seperated by spaces):\n")
querystrings = inputs.split()


def to_string(qlist):
    string = ""
    # TODO you can check if they are already preasent in the data base, as a
    # default all tickers will have a 1 month data range in the interval of 5m
    # any time under that can be filtered in a search and any time overthat
    # becomes uncertain in the data provided
    for query in qlist:
        if qlist.index(query) == (len(qlist) - 1):
            string += query.upper()
        else:
            string += query.upper() + ","
    return string


url = "https://yfapi.net/v8/finance/spark"

querystring = {"range": "1mo", "symbols": to_string(querystrings)}

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
        dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"],
                                                unit='s')
        dataframe.to_sql(ticker, con=engine, if_exists='append', index=False)


# Recs
def get_recs(symbol_lst=[], print_recs=True):
    base_rec_url = "https://yfapi.net/v6/finance/recommendationsbysymbol/"
    if symbol_lst == [] or type(symbol_lst) != list:
        return

    rec_dict = {}
    for s in symbol_lst:
        rec_url = base_rec_url + s.upper()
        recs = requests.request("GET", rec_url,
                                headers=headers)
        recs.raise_for_status()
        rec_dict[s] = recs.json()

    if print_recs:
        for company in rec_dict:
            print(company)
            print(json.dumps(rec_dict[company], indent=4))
            print()

    return rec_dict


q_string_recs = get_recs(symbol_lst=querystrings)
