from threading import Thread

import websocket

from ..function import *
from ..model.trader import Trader as td
from ..model.traders import Traders

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
    def __init__(self, currencypair=['BTC_USDT'], targe=['BTC_USDT'], notice=None):
        self.data = {}
        self.isReady = False
        self.currencypair = {}
        for a in currencypair:
            self.data.update({a: Traders()})
            self.currencypair.update({a.replace('_', '').replace('USDT', 'USD'): a})
        self.targe = targe
        self.notice = notice
        self.channelId = {}

    def on_open(self, ws):
        self.isReady = False
        for c in self.currencypair:
            subscript(ws, c, 'book')

    def on_message(self, ws, message):
        message = json.loads(message)
        if type(message) is dict:
            if message['event'] == 'subscribed':
                logging.info('success subscribed Bitfinex\'s {} order channel'.format(message['pair']))
                self.channelId.update({str(message['chanId']): self.currencypair[message['pair']]})
            elif message['event'] == 'error':
                logging.error(message)
        elif self.channelId[str(message[0])] in self.currencypair.values():
            cp = self.channelId[str(message[0])]
            if message[1] == 'hb': # HeartBeat
                return
            elif type(message[1][0]) is list:  # init orderbook data
                for data in message[1]:
                    trade = td(float(data[0]), float(abs(data[2])))
                    if data[2] < 0:  # asks
                        self.data[cp].asks.update({str(trade.rate): trade})
                        self.data[cp].total[0] += trade.amount
                    else:  # bids
                        self.data[cp].bids.update({str(trade.rate): trade})
                        self.data[cp].total[1] += trade.total
                self.isReady = True
            else:  # realtime data
                trade = td(float(message[1][0]), float(abs(message[1][2])))
                if message[1][1] == 0: # remove order
                    if str(trade.rate) in self.data[cp].asks:
                        self.data[cp].total[0] -= self.data[cp].asks[str(trade.rate)].amount
                        self.data[cp].asks.pop(str(trade.rate))
                    elif str(trade.rate) in self.data[cp].bids:
                        self.data[cp].total[0] -= self.data[cp].bids[str(trade.rate)].amount
                        self.data[cp].bids.pop(str(trade.rate))
                    else:
                        logging.warning('{} is not in the Bitfinex\'s Order Book '.format(str(trade.rate)))
                elif message[1][2] < 0:  # asks
                    if str(trade.rate) in self.data[cp].asks:  # modify
                        self.data[cp].total[0] -= self.data[cp].asks[str(trade.rate)].amount
                    self.data[cp].asks.update({str(trade.rate): trade})
                    self.data[cp].total[0] += trade.amount
                elif message[1][2] > 0:  # bids
                    if str(trade.rate) in self.data[cp].asks:  # modify
                        self.data[cp].total[1] -= self.data[cp].bids[str(trade.rate)].total
                    self.data[cp].bids.update({str(trade.rate): trade})
                    self.data[cp].total[1] += trade.total
                if cp in self.targe:
                    #askslow = min(list(map(float, self.data[cp].asks.keys())))
                    #bidshigh = max(list(map(float, self.data[cp].bids.keys())))
                    #print('Asks low {} :  {} Bids high {} : {} '.format(str(askslow), self.data[cp].asks[str(askslow)].amount,
                    #                                               str(bidshigh), self.data[cp].bids[str(bidshigh)].amount))

                    callback(self.notice, cp)

    def on_error(self, ws, message):
        logging.error(message)
        self.isReady = False
        time.sleep(1)
        logging.info('Restart Bitfinex Trader Socket')
        self.start()

    def on_close(self, ws):
        self.isReady = False
        logging.warning('Bitfinex Trader----------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart Bitfinex Trader Socket')
        self.start()

    def start(self):
        logging.info('Bitfinex trader start')
        self.ws = websocket.WebSocketApp('wss://api.bitfinex.com/ws/2', on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
