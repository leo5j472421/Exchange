from threading import Thread

import requests
import websocket

from ..function import *
from ..model.ticker import Ticker as t

'''
{
    255,                    Channel ID
    {
        0.093739,           Bid
        207.68071519,       Bid Size
        0.093749,           Ask
        198.45874446,       Ask Size
        0.003298,           Daily Change
        0.0365,             Daily Change Prec
        0.093739,           Last Price
        57668.79917403,     Volume
        0.0947,             High
        0.090306            Low
    }
}
'''

class Ticker:

    def __init__(self, notice=None, currencypair=['BTC_USDT', 'ETH_USDT'], targe=['BTC_USDT']):
        self.data = {}
        self.isReady = False
        self.currencypair = {}
        for a in currencypair:
            self.currencypair.update({a.replace('_','').replace('USDT','USD'):a})
        self.notice = notice
        self.targe = targe
        self.channelId = {}

    def resetTicker(self, cp):
        pair = cp.split('_')
        data = json.loads(requests.get(
            'https://api.bitfinex.com/v1/pubticker/{}'.format(cp.replace('_', '').replace('USDT', 'USD'))).text)
        if 'message' in data:
            logging.error(data)
        else:
            tick = t()
            tick.formate(data, pair[0], pair[1])
            self.data.update({cp: tick})

    def on_open(self, ws):
        for cp in self.currencypair.values():
            self.resetTicker(cp)
            subscript(ws, cp.replace('USDT', 'USD'), 'ticker')
        self.isReady = True

    def on_message(self, ws, message):
        message = json.loads(message)
        if type(message) is dict:
            if message['event'] == 'subscribed':
                logging.info('success subscribed Bitfinex\'s {} ticker channel'.format(message['pair']))
                self.channelId.update({str(message['chanId']): self.currencypair[message['pair']]})
            elif message['event'] == 'error':
                logging.error(message)
        elif self.channelId[str(message[0])] in self.currencypair.values():
            cp = self.channelId[str(message[0])]
            pair = cp.split('_')
            if message[1] == 'hb':  # HeartBeat
                return
            else:
                d = message[1]
                data = {'bid': d[0],
                        'bidSize': d[1],
                        'ask': d[2],
                        'askSize': d[3],
                        'dailyChange': d[4],
                        'dailyChangePerc': d[5],
                        'last_price':d[6],
                        'volume': d[7],
                        'high': d[8],
                        'low': d[9]
                        }
                tick = t()
                tick.formate(data,pair[0],pair[1])
                tick.lastprice = self.data[cp].price
                self.data.update({cp:tick})
                self.isReady = True
                if cp in self.targe:
                    if not self.data[cp].lastprice == self.data[cp].price:
                        self.data[cp].lastprice = self.data[cp].price
                        callback(self.notice, cp)
    def on_error(self, ws, message):
        logging.error(message)
        self.isReady = False
        time.sleep(1)
        logging.info('Restart  Bitfinex Ticker Socket')
        self.start()

    def on_close(self, ws):
        self.isReady = False
        logging.warning(' Bitfinex Ticker----------------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart Bitfinex Ticker Socket')
        self.start()

    def start(self):
        logging.info('Bitfinex tick start')
        self.ws = websocket.WebSocketApp('wss://api.bitfinex.com/ws/2', on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
