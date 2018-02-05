import time
from threading import Thread

from app.bittrex.function import *
from model.ticker import Ticker as t
from .signalR import SignalR
from ..bittrexApi import BittrexApi

'''
{
    'Deltas': [{
        'OpenBuyOrders': 9252,
        'Created': '2015-12-11T06:31:40.633',
        'Volume': 7552.50518641,
        'Ask': 10658.0,
        'PrevDay': 10365.0,
        'MarketName': 'USDT-BTC',
        'Low': 9918.0,
        'OpenSellOrders': 6247,
        'TimeStamp': '2018-01-24T05:38:49.523',
        'BaseVolume': 80351054.0714494,
        'Bid': 10611.02000004,
        'High': 11380.0,
        'Last': 10658.0
    },
    '
    '
    '
    ],
    'Nounce': 261988
}
'''


class Ticker:
    def __init__(self, notice=None, targe=['BTC_USDT']):
        self.data = {}
        self.isReady = False
        self.notice = notice
        self.targe = targe
        self.lastTime = time.time()
        self.api = BittrexApi()
        self.restart = True

    def on_open(self, ws):
        self.ws.subscribe('ticker')
        datas = self.api.get_market_summaries()
        if datas['success'] is True:
            for data in datas['result']:
                currencypair = reserve(data['MarketName'])
                pair = currencypair
                TickerData = {
                    'price': data['Last'],
                    'baseVolume': data['Volume'],
                    'TimeStamp': data['TimeStamp']
                }
                ticker = t()
                ticker.formate(TickerData, pair[0], pair[1])
                self.data.update({currencypair: ticker})
            self.isReady = True
            logging.info(MSG_RESET_TICKER_DATA.format(BITTREX))

    def on_error(self, ws, msg):
        self.isReady = False
        logging.error(msg)

    def on_message(self, ws, message):
        for data in message['Deltas']:
            cp = reserve(data['MarketName'])
            pair = cp
            ticker = t()
            TickerData = {
                'price': data['Last'],
                'baseVolume': data['Volume'],
                'TimeStamp': data['TimeStamp']
            }
            ticker.formate(TickerData, pair[0], pair[1])
            ticker.lastprice = self.data[cp].price
            self.data.update({cp: ticker})
            self.isReady = True
            if cp in self.targe:
                if not self.data[cp].lastprice == self.data[cp].price:
                    self.data[cp].lastprice = self.data[cp].price
                    callback(self.notice, cp)
        self.isReady = True

    def on_close(self, ws):
        self.isReady = False
        logging.warning(MSG_SOCKET_CLOSE.format(BITTREX, 'ticker', timestampToDate()))
        if self.restart:
            time.sleep(1)
            logging.info(MSG_SOCKET_RESTART.format(BITTREX, 'ticker'))
            self.start()

    def start(self):
        self.ws = SignalR(on_open=self.on_open, on_message=self.on_message,
                          on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
