import datetime
import json
import time

import matplotlib.pyplot as plt
import requests

from constant import *


def getTradeHistory(exchange, currencypair):
    history = []
    try:
        if exchange == POLONIEX:
            pair = currencypair.split('_')
            data = json.loads(requests.get(
                'https://poloniex.com/public?command=returnTradeHistory&currencyPair={}&start={}'.format(
                    '{}_{}'.format(pair[1], pair[0]), str(datetime.datetime.now().timestamp() - 1500))).text)
            history = [[d['rate'], datetime.datetime.strptime(d['date'], '%Y-%m-%d %H:%M:%S')] for d in data]
        elif exchange == HUOBI:
            cp = currencypair.replace('_', '').lower()
            data = json.loads(
                requests.get('https://api.huobi.pro/market/history/trade?symbol={}&size=2000'.format(cp)).text)
            data = data['data']
            for d in data:
                for b in d['data']:
                    history.append(
                        [b['price'], datetime.datetime.fromtimestamp((float(b['ts']) / 1000) + time.timezone)])
        elif exchange == OKCOIN:
            cp = currencypair.replace('USDT', 'USD').lower()
            data = json.loads(requests.get('https://www.okcoin.com/api/v1/trades.do?symbol={}'.format(cp)).text)
            history = [[int(d['price']), datetime.datetime.fromtimestamp(float(d['date']) + time.timezone)] for d in
                       data]
        elif exchange == OKEX:
            cp = currencypair.lower()
            data = json.loads(requests.get('https://www.okex.com/api/v1/trades.do?symbol={}'.format(cp)).text)
            history = [[int(d['price']), datetime.datetime.fromtimestamp(float(d['date']) + time.timezone)] for d in
                       data]
        elif exchange == BITTREX:
            pair = currencypair.split('_')
            data = json.loads(requests.get(
                'https://bittrex.com/api/v1.1/public/getmarkethistory?market={}'.format(
                    '{}-{}'.format(pair[1], pair[0]))).text)
            for d in data['result']:
                try:
                    b = [d['Price'], datetime.datetime.strptime(d['TimeStamp'], '%Y-%m-%dT%H:%M:%S.%f')]
                except:
                    b = [d['Price'], datetime.datetime.strptime(d['TimeStamp'], '%Y-%m-%dT%H:%M:%S')]
                history.append(b)
        elif exchange == BITFINEX:
            cp = currencypair.replace('USDT', 'USD').replace('_', '')
            data = json.loads(requests.get('https://api.bitfinex.com/v2/trades/t{}/hist'.format(cp)).text)
            history = [[d[3], datetime.datetime.fromtimestamp((float(d[1]) / 1000) + time.timezone)] for d in data]
        elif exchange == BINANCE:
            data = json.loads(requests.get(
                'https://api.binance.com/api/v1/trades?symbol={}'.format(currencypair.replace('_', ''))).text)
            history = [[d['price'], datetime.datetime.fromtimestamp(float((d['time']) / 1000) + time.timezone)] for d in
                       data]
    except :
        return None
    return sorted(history, key=lambda x: x[1])


def plot(history1, history2):
    x1 = [a[1] for a in history1]
    y1 = [float(a[0]) for a in history1]
    x2 = [a[1] for a in history2]
    y2 = [float(a[0]) for a in history2]
    # plt.plot(xa,regr.coef_ * xa + regr.intercept_)
    plt.plot(x1, y1, label=POLONIEX)
    plt.plot(x2, y2, label=HUOBI)
    plt.legend()
    # beautify the x-labels
    plt.gcf().autofmt_xdate()
    plt.show()


#plot(getTradeHistory(OKCOIN, 'ETH_BTC'), getTradeHistory(POLONIEX, 'BTC_USDT'))
