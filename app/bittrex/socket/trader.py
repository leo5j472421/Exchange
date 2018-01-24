from ..model.trader import Trader as td
from ..model.traders import Traders
from .signalR import SignalR
from ..bittrexApi import BittrexApi
from threading import Thread
from ..function import *

'''
{                                             Init OrderBook Format
    'I': '3',                                 number or receive message 
    'R': {
        'Sells': [{
            'Rate': 10677.3325,
            'Quantity': 0.12328889
        },
        '
        '
        '
        ],
        'Nounce': 928633,
        'Buys': [{
            'Rate': 10640.86232032,
            'Quantity': 0.01281495
        },
        '
        '
        '
        ],
        'MarketName': 'USDT-BTC'
    }
}


{
    'Fills': [{                                            New Trade?
        'Rate': 0.09120327,
        'Quantity': 0.043867,
        'TimeStamp': '2018-01-24T05:29:53.33',
        'OrderType': 'SELL'
    }, 
    '
    '
    '
    ],
    'Sells': [{                                             Order Book Information
        'Quantity': 0.0,
        'Rate': 0.09189,
        'Type': 1
    }, {
        'Quantity': 0.01091356,
        'Rate': 0.093667,
        'Type': 0
    }
    '
    '
    '
    ],
    'Nounce': 1202174,
    'Buys': [{
        'Quantity': 17.19390231,
        'Rate': 0.09120327,
        'Type': 2
    }
    '
    '
    '
    ],
    'MarketName': 'BTC-ETH'
}



'''

class Trader:
    def __init__(self, currencypair=['BTC_USDT', 'ETH_USDT'],targe=['BTC_USDT'],notice=None):
        self.data = {}
        self.isReady = False
        self.currencypair = currencypair
        for a in self.currencypair:
            self.data.update({a: Traders()})
        self.caller = BittrexApi()
        self.targe = targe
        self.notice = notice

    def on_open(self, ws):
        logging.info('init Bittrex\'s market Data')
        for cp in self.currencypair:
            self.ws.subscribe('trader', reserve2(cp))

    def on_error(self, ws, msg):
        self.isReady = False
        logging.error(msg)

    def on_message(self, ws, message):
        if 'R' in message:
            message = message['R']
            cp = reserve(message['MarketName'])
            logging.info('init Bittrex\'s {}  OrderBook '.format(cp))
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
            self.isReady = True
            if cp in self.targe:
                callback(self.notice,cp)
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
            self.isReady = True

            if cp in self.targe:
                callback(self.notice,cp)

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
