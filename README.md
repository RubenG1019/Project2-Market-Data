# Increadibly Uncredible Financial Advisors

This service aims to provide every user with the information they need to make better financial choices when it comes to investing in the stock market and cryptocurrency. 

We will provide historical data, market trends, and possibly the charts themselves. We might also provide adjusted-for-inflation data and gdp estimates.


## Use

Run the `MarketData.py` file. It will ask you to input

1.     up to 10 companies you want information about,
2.     the time range you want to retrieving and view data for (default is 3 months, represented as "3mo"),
3.     the intervals you want to see data for (default is 1 day, represented as "1d").

After recieving these inputs, it will:

-     retrieve each company's closing evaluation on the given interval and time range and record this information in the company's table in the `Market_Data.db` database,

-     retrieve and print out recommended stocks to pair with the each respective company in your portfolio,

-     provide a graphical representation of the stock's price at each interval on the given time range.