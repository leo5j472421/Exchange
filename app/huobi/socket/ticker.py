import logging
from threading import Thread

import gzip,requests
import websocket

from function import *
from model.ticker import Ticker as t
from ..api import *

'''
{
    'ts': 1516771146653,                  Timestamp
    'ch': 'market.btcusdt.detail',        Channel
    'tick': {                             TickerData
        'low': 10000.0,
        'id': 1523472994,
        'count': 162822,
        'amount': 10988.277588332003,
        'vol': 116416741.8753981,
        'high': 11350.0,
        'version': 1523472994,
        'open': 10384.12,                 開盤價
        'close': 10532.0                  收盤價
    }
}
'''
class Ticker:

    def __init__(self, notice=None, currencypair=['BTC_USDT', 'ETH_USDT'], targe=['BTC_USDT']):
        self.data = {}
        self.isReady = False
        self.currencypair = {}
        for a in currencypair:
            self.currencypair.update({a.replace('_', '').lower(): a})
        self.notice = notice
        self.targe = targe
        self.restart = True

    def resetTick(self, cp):
        pair = self.currencypair[cp].split('_')
        #data = get_ticker(cp)
        data = json.loads(requests.get('https://api.huobi.pro/market/detail/merged?symbol={}'.format(cp)).text)
        if not data == None:
            data = data['tick']
            tickerData = {
                'price': data['close'],
                'baseVolume': data['vol'],
            }
            tick = t()
            tick.formate(tickerData, pair[0], pair[1])
            self.data.update({self.currencypair[cp]: tick})

    def on_open(self, ws):
        # self.currencypair = get_symbolArray()
        for cp in self.currencypair:
            self.resetTick(cp)
            ws.send(json.dumps({"sub": "market.{}.detail".format(cp), "id": "id10"}))
        logging.info(MSG_RESET_TICKER_DATA.format(HUOBI))
        self.isReady = True
        # self.getTickerData()
        # logging.info('init huobi\'s market Data')

    def on_message(self, ws, message):
        message = json.loads(gzip.decompress(message).decode('utf-8'))
        if 'tick' in message:
            channel = message['ch'].replace('market.', '').replace('.detail', '')
            cp = self.currencypair[channel]
            if channel in self.currencypair:
                pair = cp.split('_')
                data = message['tick']
                tickerData = {
                    'price': data['close'],
                    'baseVolume': data['vol'],
                }
                tick = t()
                tick.formate(tickerData, pair[0], pair[1])
                tick.lastprice = self.data[cp].price
                self.data.update({cp: tick})
                self.isReady = True
                if cp in self.targe:
                    if not self.data[cp].lastprice == self.data[cp].price:
                        self.data[cp].lastprice = self.data[cp].price
                        callback(self.notice, cp)
        elif 'status' in message:
            if message['status'] == 'ok':
                logging.info(MSG_SUBSCRIPT_SUCCESS.format(HUOBI, 'ticker', message['subbed']))
            elif message['status'] == 'error':
                logging.error(message['err-msg'])
                return
        elif 'ping' in message:
            self.ws.send(json.dumps({"pong": message['ping']}))

    def on_error(self, ws, message):
        logging.error(message)
        self.isReady = False
        time.sleep(1)

    def on_close(self, ws):
        self.isReady = False
        logging.warning(MSG_SOCKET_CLOSE.format(HUOBI, 'ticker', timestampToDate()))
        logging.warning('Close Time : ' + timestampToDate(time.time() - time.timezone, True))
        if self.restart:
            time.sleep(1)
            logging.info(MSG_SOCKET_RESTART.format(HUOBI, 'ticker'))
            self.start()

    def start(self):
        logging.info(MSG_SOCKET_START.format(HUOBI, 'ticker'))
        self.ws = websocket.WebSocketApp('wss://api.huobi.pro/ws', on_open=self.on_open, on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
