# Increadibly Uncredible Financial Advisors (name in progress)

This service aims to provide every user with the information they need to make better financial choices when it comes to investing in the stock market and cryptocurrency. 

We will provide historical data, market trends, and possibly the charts themselves. We might also provide adjusted-for-inflation data and gdp estimates.


## Use

Run the `MarketData.py` file and input up to 10 companies you want information about. This will:

- create the `Market_Data.db` database and insert one table per company. This table will record the company's closing evaluation on daily intervals for the past year,

- retrieve and print out recommended stocks to pair with the each respective company in your portfolio,

- ask you for a time range for a graphical representation of the stock's price on the given time range.