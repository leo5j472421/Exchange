from threading import Thread

import websocket

from app.ok.function import *
from ..model.trader import Trader as td
from ..model.traders import Traders

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
        self.resetData(currencypair)
        self.isReady = False
        self.currencypair = currencypair
        for a in self.currencypair:
            self.data.update({a: Traders()})
        self.lastTime = time.time()
        self.targe = targe
        self.notice = notice
        self.name = 'OKEx'

    def resetData(self, currencypair):
        self.data = {}
        for a in currencypair:
            self.data.update({a: Traders()})

    def on_open(self, ws):
        self.isReady = False
        for c in self.currencypair:
            subscript(ws, c, 'trader')

    def on_error(self, ws, message):
        logging.error(message)
        self.isReady = False
        time.sleep(1)
        logging.info('Restart {} Trade Socket'.format(self.name))
        self.start()

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
            for side in message['data']:
                if side == 'asks':
                    for a in message['data']['asks']:
                        a[0] = str(float(a[0]))
                        trade = td(float(a[0]), float(a[1]))
                        if a[1] == '0':
                            if a[0] not in self.data[channel].asks:
                                print('{} in not in {}\'s bids list '.format(a[1], self.name))
                            else:
                                self.data[channel].total[0] -= self.data[channel].asks[a[0]].amount
                                self.data[channel].asks.pop(a[0])
                        elif a[0] in self.data[channel].asks:
                            self.data[channel].total[0] -= self.data[channel].asks[a[0]].amount
                            self.data[channel].total[0] += trade.amount
                            self.data[channel].asks.update({str(trade.rate): trade})
                        else:
                            self.data[channel].total[0] += trade.amount
                            self.data[channel].asks.update({str(trade.rate): trade})
                elif side == 'bids':
                    for a in message['data']['bids']:
                        a[0] = str(float(a[0]))  # 123 is 123.0 problem
                        trade = td(float(a[0]), float(a[1]))
                        if a[1] == '0':
                            if a[0] not in self.data[channel].bids:
                                print('{} in not in {}\'s bids list '.format(a[1], self.name))
                            else:
                                self.data[channel].total[1] -= self.data[channel].bids[a[0]].total
                                self.data[channel].bids.pop(a[0])
                        elif a[0] in self.data[channel].bids:
                            self.data[channel].total[1] -= self.data[channel].bids[a[0]].total
                            self.data[channel].total[1] += trade.total
                            self.data[channel].bids.update({a[0]: trade})
                        else:
                            self.data[channel].total[1] += trade.total
                            self.data[channel].bids.update({str(a[0]): trade})
            self.isReady = True
            if channel in self.targe:
                callback(self.notice, channel)

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
