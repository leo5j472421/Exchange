from threading import Thread

import requests
import ssl
import websocket

from function import *
from model.trader import Trader as td
from model.traders import Traders

'''
[        Snapshot
  CHANNEL_ID,
  [
    [
      PRICE,
      COUNT,
      AMOUNT
    ],
    ...
  ]
]

[      Update
  CHANNEL_ID,
  [
    PRICE,
    COUNT,
    AMOUNT
  ]
]


'''


class Trader:
    def __init__(self, currencypair=['BTC_USDT,ETH_USDT'], targe=['BTC_USDT'], notice=None):
        self.data = {}
        self.isReady = False
        self.currencypair = {}
        for a in currencypair:
            self.data.update({a: Traders()})
            self.currencypair.update({a.replace('_', ''): a})
        self.targe = targe
        self.notice = notice
        self.channelId = {}
        self.restart = True

    def on_open(self, ws):
        self.isReady = False
        for cp in self.currencypair:
            data = json.loads(requests.get('https://www.binance.com/api/v1/depth?symbol={}&limit=1000'.format(cp)).text)
            cp = self.currencypair[cp]
            trades = {'asks': [], 'bids': []}
            for side in data:
                if side == 'asks':
                    for order in data[side]:
                        trades['asks'].append(td(float(order[0]), float(order[1])))
                elif side == 'bids':
                    for order in data[side]:
                        trades['bids'].append(td(float(order[0]), float(order[1])))
            self.data[cp].formate(trades, BINANCE)
        logging.info(MSG_RESET_TRADER_DATA.format(BINANCE, ''))

    def on_message(self, ws, message):
        message = json.loads(message)
        data = message['data']
        cp = self.currencypair[data['s']]
        trades = {'asks': [], 'bids': []}
        for side in data:
            if side == 'a':
                for order in data[side]:
                    trades['asks'].append(td(float(order[0]), float(order[1])))
            elif side == 'b':
                for order in data[side]:
                    trades['bids'].append(td(float(order[0]), float(order[1])))
        self.data[cp].formate(trades, BINANCE)
        self.isReady = True
        Min = min(list(map(float, self.data[cp].asks.keys())))
        Max = max(list(map(float, self.data[cp].bids.keys())))
        if cp in self.targe:
            if (not Min == self.data[cp].lastAsksLow) or (not Max == self.data[cp].lastBidsHigh):
                self.data[cp].lastAsksLow = min(list(map(float, self.data[cp].asks.keys())))
                self.data[cp].lastBidsHigh = max(list(map(float, self.data[cp].bids.keys())))
                callback(self.notice, cp)

    def on_error(self, ws, message):
        logging.error(message)
        self.isReady = False
        time.sleep(1)

    def on_close(self, ws):
        self.isReady = False
        logging.warning(MSG_SOCKET_CLOSE.format(BINANCE, 'trader', timestampToDate()))
        if self.restart:
            time.sleep(1)
            logging.info(MSG_SOCKET_RESTART.format(BINANCE, 'trader'))
            self.start()

    def start(self):
        logging.info(MSG_SOCKET_START.format(BINANCE, 'trader'))
        url = 'wss://stream.binance.com:9443/stream?streams='
        for cp in self.currencypair:
            url += cp.lower() + '@depth/'
        self.ws = websocket.WebSocketApp(url, on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever, kwargs={'sslopt': {"cert_reqs": ssl.CERT_NONE}})
        self.thread.start()
