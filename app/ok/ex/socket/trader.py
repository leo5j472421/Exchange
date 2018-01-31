from threading import Thread

import websocket

from function import *
from model.trader import Trader as td
from model.traders import Traders

'''[{
    'data': {
        'asks': [
            ['11719.5', '0.001'],
            '
            '
            '
        ],
        'timestamp': 1516770794313,
        'bids': [
            ['10591.872', '0.79236926'],
            '
            '
            '
        ]
    },
    'binary': 0,
    'channel': 'ok_sub_spot_BTC_USDT_depth'
}]'''


class Trader:
    def __init__(self, currencypair=['BTC_USDT'], targe=['BTC_USDT'], notice=None):
        self.p = True
        self.data = {}
        self.isReady = False
        self.currencypair = currencypair
        for a in self.currencypair:
            self.data.update({a: Traders()})
        self.lastTime = time.time()
        self.targe = targe
        self.notice = notice
        self.name = 'OKEx'

    def on_open(self, ws):
        self.isReady = False
        for cp in self.currencypair:
            ws.send(json.dumps({'event':'addChannel','channel':'ok_sub_spot_{}_depth'.format(cp)}))

    def on_error(self, ws, message):
        logging.error(message)
        self.isReady = False
        time.sleep(1)

    def on_message(self, ws, message):
        message = json.loads(message)
        if type(message) is dict:
            return  # {"event":"pong"}
        message = message[0]
        if time.time() - self.lastTime > 30:
            ws.send('{"event":"ping"}')
            self.lastTime = time.time()
        channel = message['channel'].replace('ok_sub_spot_', '').replace('_depth', '')
        if self.name is 'OKCoin':
            channel = channel.replace('USD', 'USDT')
        if 'result' in message['data'].keys():
            if message['data']['result']:
                logging.info('success subscript {}\'s{} channel'.format(self.name, message['data']['channel']))
            else:
                logging.error(message['data']['error_msg'])
        if channel in self.currencypair:
            trades = {'asks': [], 'bids': []}
            for side in message['data']:
                if side == 'asks' :
                    for a in message['data']['asks']:
                        trades['asks'].append(td(float(a[0]), float(a[1])))
                elif side == 'bids' :
                    for a in message['data']['bids']:
                        trades['bids'].append(td(float(a[0]), float(a[1])))
            self.data[channel].formate(trades,self.name)
            self.isReady = True
            cp = channel
            Min = min(list(map(float, self.data[cp].asks.keys())))
            Max = max(list(map(float, self.data[cp].bids.keys())))
            if cp in self.targe:
                if (not Min == self.data[cp].lastAsksLow) or (not Max == self.data[cp].lastBidsHigh):
                    self.data[cp].lastAsksLow = min(list(map(float, self.data[cp].asks.keys())))
                    self.data[cp].lastBidsHigh = max(list(map(float, self.data[cp].bids.keys())))
                    callback(self.notice, cp)

    def on_close(self, ws):
        self.isReady = False
        logging.warning('{} Trade----------------------------CLOSE WebSocket-----------------------'.format(self.name))
        logging.warning('Close Time : '.format(timestampToDate(int(time.mktime(time.localtime())), True)))
        time.sleep(1)
        logging.info('Restart {} Trade Socket'.format(self.name))
        self.start()

    def start(self):
        logging.info('OKEx trader start')
        self.ws = websocket.WebSocketApp('wss://real.okex.com:10441/websocket', on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
