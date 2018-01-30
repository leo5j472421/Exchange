import ssl
from threading import Thread

import websocket,json

from function import *
from ..model.ticker import Ticker as t

'''
{
  "e": "24hrTicker",  // Event type
  "E": 123456789,     // Event time
  "s": "BNBBTC",      // Symbol
  "p": "0.0015",      // Price change
  "P": "250.00",      // Price change percent
  "w": "0.0018",      // Weighted average price
  "x": "0.0009",      // Previous day's close price
  "c": "0.0025",      // Current day's close price
  "Q": "10",          // Close trade's quantity
  "b": "0.0024",      // Best bid price
  "B": "10",          // Bid bid quantity
  "a": "0.0026",      // Best ask price
  "A": "100",         // Best ask quantity
  "o": "0.0010",      // Open price
  "h": "0.0025",      // High price
  "l": "0.0010",      // Low price
  "v": "10000",       // Total traded base asset volume
  "q": "18",          // Total traded quote asset volume
  "O": 0,             // Statistics open time
  "C": 86400000,      // Statistics close time
  "F": 0,             // First trade ID
  "L": 18150,         // Last trade Id
  "n": 18151          // Total number of trades
}
'''


class Ticker:

    def __init__(self, notice=None, currencypair=['BTC_USDT', 'ETH_USDT'], targe=['BTC_USDT']):
        self.data = {}
        self.isReady = False
        self.currencypair = {}
        for a in currencypair:
            self.currencypair.update({a.replace('_', ''): a})

        self.notice = notice
        self.targe = targe
        self.channelId = {}

    def on_open(self, ws):
        self.isReady = True

    def on_message(self, ws, message):
        message = json.loads(message)
        for data in message:
            try: ## KeyError Not in the CurrencyPair
                cp = self.currencypair[data['s']]
                pair = cp.split('_')
                tick = t()
                tick.formate(data, pair[0], pair[1])

                if cp in self.data:
                    tick.lastprice = self.data[cp].price
                self.data.update({cp: tick})
                self.isReady = True
                if cp in self.targe:
                    if not self.data[cp].lastprice == self.data[cp].price:
                        self.data[cp].lastprice = self.data[cp].price
                        callback(self.notice, cp)
            except:
                pass
    def on_error(self, ws, message):
        logging.error(message)
        self.isReady = False
        time.sleep(1)


    def on_close(self, ws):
        self.isReady = False
        logging.warning(' Binance Ticker----------------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart Binance Ticker Socket')
        self.start()

    def start(self):
        logging.info('Binance tick start')
        self.ws = websocket.WebSocketApp('wss://stream.binance.com:9443/ws/!ticker@arr', on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        # self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.thread = Thread(target=self.ws.run_forever, kwargs={'sslopt': {"cert_reqs": ssl.CERT_NONE}})
        self.thread.start()
