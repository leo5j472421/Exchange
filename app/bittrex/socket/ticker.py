import logging
from .signalR import SignalR
from ..model.ticker import Ticker as t
from ..function import *
from ..bittrexApi import BittrexApi
from threading import Thread
import time, datetime


class Ticker:
    def __init__(self, notice=None, targe=['BTC_USDT']):
        self.data = {}
        self.isReady = False
        self.notice = notice
        self.targe = targe
        self.lastTime = time.time()
        self.api = BittrexApi()

    def _callback(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except Exception as e:
                logging.error("error from callback {}: {}".format(callback, e))

    def on_open(self, ws):
        self.isReady = True
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
    def on_error(self, ws, msg):
        self.isReady = False
        logging.error(msg)

    def on_message(self, ws, message):
        for data in message['Deltas']:
            ticker = t()
            currencypair = reserve(data['MarketName'])
            pair = currencypair
            ticker.formate(data, pair[0], pair[1])
            self.data.update({currencypair: ticker})
            if currencypair in self.targe:
                self._callback(self.notice,currencypair)

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
