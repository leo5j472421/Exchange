from threading import Thread

import websocket

from ..function import *
from model.trader import Trader as td
from model.traders import Traders
from ..polonixeApi import PoloniexApi

'''
[
    121,                                                                    CurrencyPairID
    191049657,                                                              Sequence
    [ 
        ["o", 0, "10800.00000000", "0.06347929"],                          o: OrderModify, Sides(asks,bids) , Rate , Amount
        ["t", "18448534", 1, "10800.00000000", "0.00082497", 1516766511]   t: NewTrade , TradeID? side(sell,buy) , Rate , Amount , Timestramp
    ]
]
'''


class Trader:
    def __init__(self, currencypair=['BTC_USDT', 'ETH_USDT', 'ETH_BTC', 'ZEC_BTC'], targe=['BTC_USDT'], notice=None):
        self.p = True
        self.data = {}
        self.isReady = False
        self.currencypair = currencypair
        for a in currencypair:
            self.data.update({a: Traders()})
        self.marketChannel = []
        self.targe = targe
        self.notice = notice
        self.caller = PoloniexApi()
        self.ids = {}
        self.cps = {}

    def on_open(self, ws):
        self.isReady = False
        data = self.caller.returnTicker()  # call PoloniexApi Reset The ticker Data
        self.ids = {market: data[market]['id'] for market in data}
        self.cps = {str(data[market]['id']): market for market in data}
        for c in self.currencypair:
            ws.send(json.dumps({'command': 'subscribe', 'channel': reserve(c)}))

    def on_message(self, ws, message):
        message = json.loads(message)
        if 'error' in message:
            logging.error(message)
            return
        if message[0] in self.marketChannel:
            self.isReady = True
            if message[1] == 2:
                return
            trades = {'asks': [], 'bids': []}
            cp = reserve(self.cps[str(message[0])])
            for i in message[2]:
                if i[0] == 'o':
                    if i[1] == 0 : #asks
                        trades['asks'].append(td(float(i[2]),float(i[3])))
                    else: #bids
                        trades['bids'].append(td(float(i[2]),float(i[3])))
            self.data[cp].formate(trades,'Poloniex')
            Min = min(list(map(float, self.data[cp].asks.keys())))
            Max = max(list(map(float, self.data[cp].bids.keys())))
            if cp in self.targe:
                if (not Min == self.data[cp].lastAsksLow) or (not Max == self.data[cp].lastBidsHigh):
                    self.data[cp].lastAsksLow = min(list(map(float, self.data[cp].asks.keys())))
                    self.data[cp].lastBidsHigh = max(list(map(float, self.data[cp].bids.keys())))
                    callback(self.notice, cp)
        elif message[0] < 1000:  # First msg ( all order book data )
            cp = reserve(self.cps[str(message[0])])
            if message[2][0][0] == 'i':
                logging.info('success subscript channel {} '.format(reserve(cp)))
                self.marketChannel.append(message[0])
                data = message[2][0][1]['orderBook']
                logging.info('Init {}\'s Order Book Data: {}'.format(cp, str(len(data[0]) + len(data[1]))))
                trades = {'asks': [], 'bids': []}
                for a in [0, 1]:
                    side = 'asks' if a == 0 else 'bids'
                    for rate in data[a]:
                        if side == 'asks' :
                            trades['asks'].append(td(float(rate),float(data[a][rate])))
                        else:
                            trades['bids'].append(td(float(rate),float(data[a][rate])))
                self.data[cp].formate(trades,'Poloniex')
                self.data[cp].lastAsksLow = min(list(map(float, self.data[cp].asks.keys())))
                self.data[cp].lastBidsHigh = max(list(map(float, self.data[cp].bids.keys())))
                self.isReady = True
                if cp in self.targe:
                    callback(self.notice, cp)

    def on_error(self, ws, message):
        logging.error(message)
        self.isReady = False

    def on_close(self, ws):
        self.isReady = False
        logging.warning('Poloniex Trader----------------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart Poloniex Trader Socket')
        # self.start()

    def start(self):
        logging.info('poloniex trader start')
        self.ws = websocket.WebSocketApp('wss://api2.poloniex.com/', on_open=self.on_open, on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
