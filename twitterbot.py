import tweepy
import keys
import yfinance as yf
from statistics import stdev
from datetime import datetime
import pytz
from sklearn.linear_model import LinearRegression
import numpy as np


def buysell():
    tick = input("What stock do you want a signal for? ")
    tick = tick.upper()
    stock = yf.Ticker(tick)
    price = stock.info['currentPrice']
    ma = stock.info['fiftyDayAverage']
    low = stock.info['regularMarketDayLow']
    high = stock.info['regularMarketDayHigh']
    low52 = stock.info['fiftyTwoWeekLow']
    high52 = stock.info['fiftyTwoWeekHigh']
    pricerange = [low52 * 0.1 + low * 0.9, low, high, high52 * 0.1 + high * 0.9]
    stand = stdev(pricerange)
    iowaTz = pytz.timezone("US/Central")
    timeInIowa = datetime.now(iowaTz)
    currentTime = timeInIowa.strftime("%H:%M:%S")

    #rsi
    closesr = stock.history(period='2wk', interval='1d')
    closer = []
    dayr = []
    neg = 0
    pos = 0
    for i in range(0, len(closesr["Close"])):
        closer.append(closesr["Close"][i])
        dayr.append(i)
    closer = np.array(closer)
    dayr = np.array(dayr)
    for x in range(1, len(closer)):
        change = (closer[x] - closer[x - 1]) / closer[x]
        if change < 0:
            neg += change
        elif change > 0:
            pos += change
    pos = (pos / 14)
    neg = (neg / 14) * -1
    rsi = 100 - (100 / (1 + (pos / neg)))
    if rsi < 40:
        rsi = (f"RSI indicates that {tick} is oversold.")
    elif rsi > 60:
        rsi = (f"RSI indicates that {tick} is overbought.")
    else:
        rsi = (f"RSI gives neutral signal for {tick}.")

    ##Wk lin
    closeswk = stock.history(period='1wk', interval='1d')
    closewk = []
    daywk = []
    for i in range(0, len(closeswk["Close"])):
        closewk.append(closeswk["Close"][i])
        daywk.append(i)
    closewk = np.array(closewk)
    daywk = np.array(daywk).reshape((-1, 1))
    modelwk = LinearRegression().fit(daywk, closewk)
    intcwk = modelwk.intercept_
    coefwk = modelwk.coef_

    ##mo lin
    closesmo = stock.history(period='1mo', interval='1d')
    closemo = []
    daymo = []
    for i in range(0, len(closesmo["Close"])):
        closemo.append(closesmo["Close"][i])
        daymo.append(i)
    closemo = np.array(closemo)
    daymo = np.array(daymo).reshape((-1, 1))
    modelmo = LinearRegression().fit(daymo, closemo)
    intcmo = modelmo.intercept_
    coefmo = modelmo.coef_
    ##3m
    closes3mo = stock.history(period='3mo', interval='1d')
    close3mo = []
    day3mo = []
    for i in range(0, len(closes3mo["Close"])):
        close3mo.append(closes3mo["Close"][i])
        day3mo.append(i)
    close3mo = np.array(close3mo)
    day3mo = np.array(day3mo).reshape((-1, 1))
    model3mo = LinearRegression().fit(day3mo, close3mo)
    intc3mo = model3mo.intercept_
    coef3mo = model3mo.coef_

    ##Situations
    if coef3mo < 0 and coefmo > 0 and coefwk > coefmo:
        return((f"Linear reggression model predicts BUY signal for {tick} at price of {price}. {rsi} ({currentTime} CST)"))
    if coef3mo > 0 and coefmo > 0 and coefwk > coefmo:
        return((f"Linear reggression model predicts BUY signal for {tick} at price of {price}. {rsi} ({currentTime} CST)"))
    if coef3mo < 0 and coefmo < 0 and coefmo > coef3mo and coefwk > coefmo and coefwk > 0:
        return((f"Linear reggression model predicts BUY signal for {tick} at price of {price}. {rsi} ({currentTime} CST)"))
    if coef3mo > 0 and coefmo < 0 and coefwk > 0:
        return((f"Linear reggression model predicts BUY signal for {tick} at price of {price}. {rsi} ({currentTime} CST)"))
    if coef3mo > 0 and coefmo > coef3mo and coefwk > coefmo:
        return((f"Linear reggression model predicts BUY signal for {tick} at price of {price}. {rsi} ({currentTime} CST)"))
    if coef3mo < 0 and coefmo < coef3mo and coefwk < coefmo:
        return((f"Linear reggression model predicts SELL signal for {tick} at price of {price}. {rsi} ({currentTime} CST)"))
    if coef3mo < 0 and coefmo > 0 and coefwk < 0:
        return((f"Linear reggression model predicts SELL signal for {tick} at price of {price}. {rsi} ({currentTime} CST)"))
    if coef3mo > 0 and coef3mo > coefmo and coefwk < 0:
        return((f"Linear reggression model predicts SELL signal for {tick} at price of {price}. {rsi} ({currentTime} CST)"))
    if coef3mo > 0 and coefmo < 0 and coefwk < coefmo:
        return((f"Linear reggression model predicts SELL signal for {tick} at price of {price}. {rsi} ({currentTime} CST)"))
    if coef3mo < 0 and coefmo < 0 and coefwk < coefmo:
        return((f"Linear reggression model predicts SELL signal for {tick} at price of {price}. {rsi} ({currentTime} CST)"))
    else:
        return((f"Neutral signal detected for {tick} at price of {price}. {rsi} ({currentTime} CST)"))


def api():
    auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
    auth.set_access_token(keys.access_token, keys.access_token_secret)
    return(tweepy.API(auth))

def tweet(api: tweepy.API, message: str):
    api.update_status(message)
    print('Tweeted')

if __name__ == '__main__':
    buysell = buysell()
    api = api()
    tweet(api, buysell)

