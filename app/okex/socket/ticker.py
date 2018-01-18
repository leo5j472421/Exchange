import websocket
from ..model.ticker import Ticker as t
from ..function import *
from threading import Thread
import logging

class Ticker:
    def __init__(self, notice=None,currencypair=['BTC_USDT','ETH_USDT'],targe=['BTC_USDT']):
        self.data = {}
        self.isReady = False
        self.currencypair = currencypair
        self.notice = notice
        self.targe = targe

    def _callback(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except Exception as e:
                logging.error("error from callback {}: {}".format(callback, e))

    def on_open(self, ws):
        self.isReady = False
        for cp in self.currencypair:
            subscript(ws,cp)
        logging.info('init OKEx\'s market Data')

    def on_message(self, ws, message):
        message = json.loads(message)[0]
        channel = message['channel'].replace('ok_sub_spot_','').replace('_ticker','')
        if 'result' in message['data'].keys():
            if message['data']['result']:
                logging.info('success subscript {} channel'.format(message['data']['channel']))
            else:
                logging.error(message['data']['error_msg'] )
        elif channel in self.currencypair:
            self.isReady = True
            pair = channel.upper().split('_')
            ticker = t()
            ticker.formate(message['data'],pair[0],pair[1])
            self.data.update({channel.upper():ticker})
            if channel in self.targe:
                self._callback(self.notice,channel)


    def on_close(self, ws):
        self.isReady = False
        logging.warning('----------------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart The Socket')
        self.start()

    def start(self):
        logging.basicConfig(level=logging.INFO)
        logging.info('OKEx tick start')
        self.ws = websocket.WebSocketApp('wss://real.okex.com:10441/websocket', on_open=self.on_open, on_message=self.on_message,
                                         on_close=self.on_close)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
