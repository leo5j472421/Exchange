from model.trader import Trader as td
from model.traders import Traders
import websocket, gzip
from threading import Thread
from function import *
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
            self.data.update({cp: Traders()})
        self.targe = targe
        self.notice = notice



    def on_open(self, ws):
        self.isReady = False
        for cp in self.currencypair:
            ws.send(json.dumps({"sub": "market.{}.depth.step0".format(cp), "id": "id10"}))

    def on_message(self, ws, message):
        message = json.loads(gzip.decompress(message).decode('utf-8'))
        if 'tick' in message:
            channel = message['ch'].replace('market.','').replace('.depth.step0','')
            if channel in self.currencypair:
                cp = self.currencypair[channel]
                tds = Traders()
                data = message['tick']
                trades = {'asks': [], 'bids': []}
                for side in data:
                    if side == 'asks':
                        for a in data['asks']:
                            trades['asks'].append(td(a[0], a[1]))
                    else:
                        for a in data['bids']:
                            trades['bids'].append(td(a[0], a[1]))
                tds.formate(trades,'Huibo')
                tds.lastAsksLow = self.data[cp].lastAsksLow
                tds.lastBidsHigh = self.data[cp].lastBidsHigh
                self.data.update({cp:tds})
                self.isReady = True
                Min = min(list(map(float, self.data[cp].asks.keys())))
                Max = max(list(map(float, self.data[cp].bids.keys())))
                if cp in self.targe:
                    if (not Min == self.data[cp].lastAsksLow) or (not Max == self.data[cp].lastBidsHigh):
                        self.data[cp].lastAsksLow = min(list(map(float, self.data[cp].asks.keys())))
                        self.data[cp].lastBidsHigh = max(list(map(float, self.data[cp].bids.keys())))
                        callback(self.notice, cp)
        elif 'status' in message:
            if message['status'] == 'ok':
                logging.info('subscript {} channel success'.format(message['subbed']))
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
        logging.warning('Huobi Trader----------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart Huobi Trader Socket')
        self.start()

    def start(self):
        logging.info('huobi trader start')
        self.ws = websocket.WebSocketApp('wss://api.huobi.pro/ws', on_open=self.on_open, on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
