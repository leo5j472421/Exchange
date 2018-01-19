from ..model.trader import Trader as td
from ..model.traders import Traders
from .signalR import SignalR
import websocket, logging
from threading import Thread
from ..function import *


class Trader:
    def __init__(self, currencypair=['BTC_USDT', 'ETH_USDT']):
        self.data = {}
        self.isReady = False
        self.currencypair = currencypair
        for a in self.currencypair:
            self.data.update({a: Traders()})

    def _callback(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except Exception as e:
                logging.error("error from callback {}: {}".format(callback, e))

    def on_open(self, ws):

        logging.info('init Bittrex\'s market Data')
        for cp in self.currencypair:
            self.ws.subscribe('trader', reserve2(cp))

    def on_error(self, ws, msg):
        self.isReady = False
        logging.error(msg)

    def on_message(self, ws, message):
        # bid指買進報價
        # ask指賣出報價


        if 'R' in message:
            self.isReady = True
            logging.info('init Bittrex\'s OrderBook ')
            message = message['R']
            if message['MarketName'].replace('-', '_') in self.data:
                cp = message['MarketName'].replace('-', '_')
            else:
                cp = reserve(message['MarketName'])
            for sides in ['Sells', 'Buys']:
                side = 'asks' if sides == 'Sells' else 'bids'
                if side == 'asks':
                    for a in message[sides]:
                        trade = td(a['Rate'], a['Quantity'])
                        self.data[cp].asks.update({str(trade.rate): trade})
                        self.data[cp].total[0] += trade.amount
                else:
                    for a in message[sides]:
                        trade = td(a['Rate'], a['Quantity'])
                        self.data[cp].bids.update({str(trade.rate): trade})
                        self.data[cp].total[1] += trade.total
        else:
            if message['MarketName'].replace('-', '_') in self.data:
                cp = message['MarketName'].replace('-', '_')
            else:
                cp = reserve(message['MarketName'])
            for sides in ['Sells', 'Buys']:
                side = 'asks' if sides == 'Sells' else 'bids'
                if side == 'asks':
                    for a in message[sides]:
                        trade = td(a['Rate'], a['Quantity'])
                        if a['Type'] == 0:  # ADD to order book
                            self.data[cp].asks.update({str(trade.rate): trade})
                            self.data[cp].total[0] += trade.amount
                        elif a['Type'] == 1:  # Remove OrderBook
                            self.data[cp].total[0] -= self.data[cp].asks[str(trade.rate)].amount
                            self.data[cp].asks.pop(str(trade.rate))
                        elif a['Type'] == 2:  # EDIT the order book
                            self.data[cp].total[0] -= self.data[cp].asks[str(trade.rate)].amount
                            self.data[cp].asks.update({str(trade.rate): trade})
                            self.data[cp].total[0] += trade.amount

                else:
                    for a in message[sides]:
                        trade = td(a['Rate'], a['Quantity'])
                        if a['Type'] == 0:  # ADD to order book
                            self.data[cp].bids.update({str(trade.rate): trade})
                            self.data[cp].total[1] += trade.total
                        elif a['Type'] == 1:  # Remove OrderBook
                            self.data[cp].total[1] -= self.data[cp].bids[str(trade.rate)].total
                            self.data[cp].bids.pop(str(trade.rate))
                        elif a['Type'] == 2:  # EDIT the order book
                            self.data[cp].total[1] -= self.data[cp].bids[str(trade.rate)].total
                            self.data[cp].bids.update({str(trade.rate): trade})
                            self.data[cp].total[1] += trade.total

    def on_close(self, ws):
        self.isReady = False
        logging.warning('----------------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart The Socket')
        self.start()

    def start(self):
        logging.basicConfig(level=logging.INFO)
        self.ws = SignalR(on_open=self.on_open, on_message=self.on_message,
                          on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
