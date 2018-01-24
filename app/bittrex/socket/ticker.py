import logging
from .signalR import SignalR
from ..model.ticker import Ticker as t
from ..function import *
from ..bittrexApi import BittrexApi
from threading import Thread
import time

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

    def on_open(self, ws):
        logging.info('init Bittrex\'s market Data')
        self.ws.subscribe('ticker')
        datas = self.api.get_market_summaries()
        if datas['success'] is True:
            for data in datas['result']:
                ticker = t()
                currencypair = reserve(data['MarketName'])
                pair = currencypair
                ticker.formate(data, pair[0], pair[1])
                self.data.update({currencypair: ticker})
            if currencypair in self.targe:
                callback(self.notice,currencypair)

    def on_error(self, ws, msg):
        self.isReady = False
        logging.error(msg)

    def on_message(self, ws, message):   # receive Data every 5 second
        for data in message['Deltas']:
            ticker = t()
            currencypair = reserve(data['MarketName'])
            pair = currencypair
            ticker.formate(data, pair[0], pair[1])
            self.data.update({currencypair: ticker})
            if currencypair in self.targe:
                callback(self.notice,currencypair)
        self.isReady = True

    def on_close(self, ws):
        self.isReady = False
        logging.warning('----------------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart The Socket')
        self.start()

    def start(self):
        logging.basicConfig(level=logging.INFO)
        self.ws = SignalR(on_open=self.on_open, on_message=self.on_message,
                          on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
