import tweepy
import keys
import yfinance as yf
from statistics import stdev
from datetime import datetime
import pytz


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
    buy = ma - stand
    sell = ma + stand
    iowaTz = pytz.timezone("US/Central")
    timeInIowa = datetime.now(iowaTz)
    currentTime = timeInIowa.strftime("%H:%M:%S")

    if price <= buy:
        return(f"Buy Signal detected for {tick} at price of {price} ({currentTime} CST)")

    if price >= sell:
        return(f"Sell Signal detected for {tick} at price of {price} ({currentTime} CST)")

    else:
        return(f"Neutral Signal detected for {tick} at price of {price} ({currentTime} CST)")


def api():
    auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
    auth.set_access_token(keys.access_token, keys.access_token_secret)
    return(tweepy.API(auth))

def tweet(api: tweepy.API, message: str, image_path=None):
    if image_path:
        api.update_status_with_media(message, image_path)
    else:
        api.update_status(message)
    print('Tweeted')

if __name__ == '__main__':
    buysell = buysell()
    api = api()
    tweet(api, buysell)

