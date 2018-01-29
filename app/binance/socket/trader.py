from threading import Thread
import websocket,ssl,requests,json
from function import *
from app.binance.model.trader import Trader as td
from app.binance.model.traders import Traders

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

    def on_open(self, ws):
        self.isReady = False
        for c in self.currencypair:
            data = json.loads(requests.get('https://www.binance.com/api/v1/depth?symbol={}&limit=1000'.format(c)).text)
            for side in data:
                if side == 'asks':
                    for order in data[side]:
                        rate = str(float(order[0]))
                        trade = td(float(rate),float(order[1]))
                        self.data[self.currencypair[c]].total[0] += trade.amount
                        self.data[self.currencypair[c]].asks.update({rate:trade})
                elif side == 'bids':
                    for order in data[side]:
                        rate = str(float(order[0]))
                        trade = td(float(rate),float(order[1]))
                        self.data[self.currencypair[c]].total[1] += trade.total
                        self.data[self.currencypair[c]].bids.update({rate:trade})

    def on_message(self, ws, message):
        message = json.loads(message)
        data = message['data']
        cp = self.currencypair[data['s']]
        for side in data:
            if side == 'a':
                for order in data[side]:
                    rate = str(float(order[0]))
                    amount = float(order[1])
                    trade = td(float(rate), amount)
                    if not rate in self.data[cp].asks:  # Insert
                        if not amount == 0.0 :
                            self.data[cp].total[0] += trade.amount
                            self.data[cp].asks.update({rate:trade})
                    elif not amount == 0.0 : # modify
                        self.data[cp].total[0] -= self.data[cp].asks[rate].amount
                        self.data[cp].total[0] += trade.amount
                        self.data[cp].asks.update({rate:trade})
                    else: # remove
                        self.data[cp].total[0] -= self.data[cp].asks[rate].amount
                        self.data[cp].asks.pop(rate)
            elif side == 'b':
                for order in data[side]:
                    rate = str(float(order[0]))
                    amount = float(order[1])
                    trade = td(float(rate), amount)
                    if not rate in self.data[cp].bids:  # Insert
                        if not amount == 0.0 :
                           self.data[cp].total[1] += trade.total
                           self.data[cp].bids.update({rate:trade})
                    elif not amount == 0.0 : # modify
                        self.data[cp].total[1] -= self.data[cp].bids[rate].amount
                        self.data[cp].total[1] += trade.amount
                        self.data[cp].bids.update({rate:trade})
                    else : # remove
                        self.data[cp].total[1] -= self.data[cp].bids[rate].amount
                        self.data[cp].bids.pop(rate)
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
        url = 'wss://stream.binance.com:9443/stream?streams='
        for cp in self.currencypair:
            url += cp.lower() + '@depth/'
        self.ws = websocket.WebSocketApp(url, on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever, kwargs={'sslopt': {"cert_reqs": ssl.CERT_NONE}})
        self.thread.start()
