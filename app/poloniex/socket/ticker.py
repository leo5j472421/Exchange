from threading import Thread

import websocket
from ..function import *
from ..model.ticker import Ticker as t
from ..polonixeApi import PoloniexApi

'''
Message format
[
    1002,                             Channel
    null,                             Unknown
    [
        121,                          CurrencyPairID
        "10777.56054438",             Last
        "10800.00000000",             lowestAsk
        "10789.20000001",             highestBid
        "-0.00860373",                percentChange
        "72542984.79776118",          baseVolume
        "6792.60163706",              quoteVolume
        0,                            isForzen
        "11400.00000000",             high24hr
        "9880.00000009"               low24hr
    ]
]
'''


class Ticker:
    def __init__(self, notice=None, targe=['BTC_USDT']):
        self.data = {}
        self.isReady = False
        self.caller = PoloniexApi()
        self.notice = notice
        self.ids={}
        self.cps={}
        self.targe = targe

    def getTickerData(self):
        data = self.caller.returnTicker()  # call PoloniexApi Reset The ticker Data
        self.ids= { market: data[market]['id'] for market in data}
        self.cps= { str(data[market]['id']):market  for market in data}
        for currencypair in data:
            tick = t()
            cp = currencypair.split('_')
            tick.formate(data[currencypair], cp[1], cp[0])
            tick.lastprice = tick.price
            rcp = reserve(currencypair)  # reverse
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
            'id': self.ids[reserve(args[0])]
        }

        tk = t()
        tk.formate(newTickerData, base, quote)
        tk.lastprice = self.data[args[0]].price
        self.data.update({args[0]: tk})
        self.isReady = True
        if args[0] in self.targe:
            if not self.data[args[0]].lastprice == self.data[args[0]].price:
                self.data[args[0]].lastprice = self.data[args[0]].price
                callback(self.notice, args[0])

    def on_open(self, ws):
        self.isReady = False
        self.getTickerData()
        logging.info('poloniex init market Data')
        ws.send(json.dumps({'command': 'subscribe', 'channel': 1002}))

    def on_message(self, ws, message):
        message = json.loads(message)
        if 'error' in message:
            logging.error(message)
            return
        if message[0] == 1002:
            if message[1] == 1:
                logging.info('success subscript channel {} '.format(str(message[0])))
                return
            message[2][0] = reserve(self.cps[str(message[2][0])])
            data = message[2]
            self.ticketEvent(data)
        elif message[0] == 1010:  # Poloniex's Websocket HeartBeat
            self.isReady = False

    def on_error(self, ws, message):
        logging.error(message)
        self.isReady = False

    def on_close(self, ws):
        self.isReady = False
        logging.warning('Poloniex Ticker----------------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart Poloniex Ticker Socket')
        self.start()

    def start(self):
        logging.info('poloniex tick start')
        self.ws = websocket.WebSocketApp('wss://api2.poloniex.com/', on_open=self.on_open, on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
