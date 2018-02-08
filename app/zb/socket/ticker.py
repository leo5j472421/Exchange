from threading import Thread

import websocket

from function import *
from model.ticker import Ticker as t


class Ticker:

    def __init__(self, notice=None, currencypair=['BTC_USDT', 'ETH_USDT'], targe=['BTC_USDT']):
        self.data = {}
        self.isReady = False
        self.currencypair = {}
        for a in currencypair:
            self.currencypair.update({a.replace('_', '').lower(): a})
        self.notice = notice
        self.targe = targe
        self.channelId = {}
        self.restart = True

    def resetTick(self):
        pass

    def on_open(self, ws):
        for cp in self.currencypair:
            self.ws.send(json.dumps({'event': 'addChannel', 'channel': '{}_ticker'.format(cp)}))
        self.resetTick()
        logging.info(MSG_RESET_TICKER_DATA.format(ZB))
        self.isReady = True

    def on_message(self, ws, message):
        message = json.loads(message)
        if 'success' in message:
            if message['success'] == False:
                logging.error(message)
        channel = message['channel'].replace('_ticker', '')
        if channel in self.currencypair:
            data = message['ticker']
            cp = self.currencypair[channel]
            pair = cp.split('_')
            tickData = {
                'price': data['last'],
                'baseVolume': data['vol']
            }
            tick = t()
            tick.formate(tickData, pair[0], pair[1])
            try:
                tick.lastprice = self.data[cp].price
            except:
                pass
            self.data.update({cp: tick})
            self.isReady = True
            if cp in self.targe:
                if not self.data[cp].lastprice == self.data[cp].price:
                    self.data[cp].lastprice = self.data[cp].price
                    callback(self.notice, cp)

    def on_error(self, ws, message):
        logging.error(message)
        self.isReady = False
        time.sleep(1)

    def on_close(self, ws):
        self.isReady = False
        logging.warning(MSG_SOCKET_CLOSE.format(ZB, 'ticker', timestampToDate()))
        if self.restart:
            time.sleep(1)
            logging.info(MSG_SOCKET_RESTART.format(ZB, 'ticker'))
            self.start()

    def start(self):
        logging.info(MSG_SOCKET_START.format(ZB, 'ticker'))
        self.ws = websocket.WebSocketApp('wss://api.zb.com:9999/websocket', on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
