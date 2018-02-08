from threading import Thread

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
            self.currencypair.update({a.replace('_', '').lower(): a})
        self.targe = targe
        self.notice = notice
        self.channelId = {}
        self.restart = True

    def on_open(self, ws):
        self.isReady = False
        for cp in self.currencypair:
            ws.send(json.dumps({'event': 'addChannel', 'channel': '{}_depth'.format(cp)}))
        logging.info(MSG_RESET_TRADER_DATA.format(ZB, ''))

    def on_message(self, ws, message):
        message = json.loads(message)
        data = message
        cp = self.currencypair[data['channel'].replace('_depth', '')]
        trades = {'asks': [], 'bids': []}
        for side in data:
            if side == 'asks':
                for order in data[side]:
                    trades['asks'].append(td(float(order[0]), float(order[1])))
            elif side == 'bids':
                for order in data[side]:
                    trades['bids'].append(td(float(order[0]), float(order[1])))
        try:
            Min, Max = self.data[cp].lastAsksLow, self.data[cp].lastBidsHigh
            self.data.update({cp: Traders()})
            self.data[cp].lastAsksLow, self.data[cp].lastBidsHigh = Min, Max
        except:
            self.data.update({cp: Traders()})
        self.data[cp].formate(trades, ZB)
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
        logging.warning(MSG_SOCKET_CLOSE.format(ZB, 'trader', timestampToDate()))
        if self.restart:
            time.sleep(1)
            logging.info(MSG_SOCKET_RESTART.format(ZB, 'trader'))
            self.start()

    def start(self):
        logging.info(MSG_SOCKET_START.format(ZB, 'trader'))
        self.ws = websocket.WebSocketApp('wss://api.zb.com:9999/websocket', on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
