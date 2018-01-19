import websocket, traceback,sys
from ..model.ticker import Ticker as t
from ..arrary import Array
from ..function import *
from threading import Thread
from ..polonixeApi import PoloniexApi
import logging


class Ticker:
    def __init__(self, notice=None,targe=['BTC_USDT']):
        self.data = {}
        self.isReady = False
        self.caller = PoloniexApi()
        self.notice = notice
        self.targe = targe

    def _callback(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except Exception as e:
                logging.error("error from callback {}: {}".format(callback, e))

    def getTickerData(self):
        data = self.caller.returnTicker()
        for currencypair in data:
            tick = t()
            cp = currencypair.split('_')
            tick.formate(data[currencypair], cp[1], cp[0])
            rcp = reserve(currencypair)#reverse
            self.data.update({rcp: tick})

    def ticketEvent(self, args):
        pairAr = args[0].split('_')
        base = pairAr[0]
        quote = pairAr[1]
        newTickerData = {
            'last': args[1],
            'lowestAsk': args[2],
            'highestBid': args[3],
            'percentChange': args[4],
            'baseVolume': args[5],
            'quoteVolume': args[6],
            'isFrozen': args[7],
            'high24hr': args[8],
            'low24hr': args[9],
            'id': Array.markets['byCurrencyPair'][reserve(args[0])]['id']
        }

        tk = t()
        tk.formate(newTickerData, base, quote)
        self.data.update({args[0]: tk})
        if args[0] in self.targe :
            self._callback(self.notice,args[0])

    def on_open(self, ws):
        self.isReady = False
        self.getTickerData()
        logging.info('poloniex init market Data')
        subscript(self.ws, 1002)

    def on_message(self, ws, message):
        message = json.loads(message)
        if 'error' in message:
            logging.error(message)
            return
        if message[0] == 1002:
            if message[1] == 1:
                logging.info('success subscript channel ' + str(message[0]))
                return
            self.isReady = True
            message[2][0] = reserve(Array.markets['byID'][str(message[2][0])]['currencyPair'])
            data = message[2]
            self.ticketEvent(data)
        elif message[0] == 1010:
            self.isReady = False

    def on_close(self, ws):
        self.isReady = False
        logging.warning('----------------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart The Socket')
        self.start()

    def start(self):
        logging.info('poloniex tick start')
        self.ws = websocket.WebSocketApp('wss://api2.poloniex.com', on_open=self.on_open, on_message=self.on_message,
                                         on_close=self.on_close)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
