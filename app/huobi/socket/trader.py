from ..model.trader import Trader as td
from ..model.traders import Traders
import websocket, gzip
from threading import Thread
from ..function import *
import logging

'''
{                                              Huobi's OrderBook data will reset evey time when receive the new data from server
    'ch': 'market.btcusdt.depth.step0',        Channel
    'tick': {                                  
        'ts': 1516771568089,                   Timestamp
        'asks': [
            [10635.73, 0.2264],                Rate , Amount
            '
            '
            '
        ],
        'bids': [
            [10604.13, 0.224],
            '
            '
            '
        ],
        'version': 1523609243
    },
    'ts': 1516771568471
}
'''


class Trader:
    def __init__(self, currencypair=['BTC_USDT'],targe=['BTC_USDT'],notice = None):
        self.data = {}
        self.isReady = False
        self.currencypair = {}
        for a in currencypair:
            self.currencypair.update({a.replace('_', '').lower(): a})
        for cp in currencypair:
            self.resetData(cp)
        self.targe = targe
        self.notice = notice
        self.i = 0

    def resetData(self, cp):
        self.data.update({cp: Traders()})

    def on_open(self, ws):
        self.isReady = False
        for c in self.currencypair:
            subscript(ws, c, 'trader')

    def on_message(self, ws, message):
        if self.i == 10:
            return
        message = json.loads(gzip.decompress(message).decode('utf-8'))
        if 'tick' in message:
            self.isReady = False
            channel = message['ch'][message['ch'].find('.') + 1:][0:message['ch'].find('.') + 1]
            if channel in self.currencypair:
                self.resetData(self.currencypair[channel])
                data = message['tick']
                for side in data:
                    if side == 'asks':
                        for a in data['asks']:
                            trade = td(a[0], a[1])
                            self.data[self.currencypair[channel]].asks.update({str(a[0]): trade})
                            self.data[self.currencypair[channel]].total[0] += trade.amount
                    else:
                        for a in data['bids']:
                            trade = td(a[0], a[1])
                            self.data[self.currencypair[channel]].bids.update({str(a[0]): trade})
                            self.data[self.currencypair[channel]].total[1] += trade.total
                self.isReady = True
                if self.currencypair[channel] in self.targe:
                    callback(self.notice,self.currencypair[channel])
        elif 'status' in message:
            if message['status'] == 'ok':
                logging.info('subscript {} channel success'.format(message['subbed']))
            elif message['status'] == 'error':
                logging.error(message['status']['err-msg'])
                return
        elif 'ping' in message:
            self.ws.send(json.dumps({"pong": message['ping']}))

    def on_error(self, ws, message):
        logging.error(message)
        self.isReady = False
        time.sleep(1)
        logging.info('Restart The Socket')
        self.start()

    def on_close(self, ws):
        self.isReady = False
        logging.warning('Huobi Trader----------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart The Socket')
        self.start()

    def start(self):
        logging.info('huobi trader start')
        self.ws = websocket.WebSocketApp('wss://api.huobi.pro/ws', on_open=self.on_open, on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
