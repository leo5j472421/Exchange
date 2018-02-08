from threading import Thread

from model.trader import Trader as td
from model.traders import Traders
from .signalR import SignalR
from ..bittrexApi import BittrexApi
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
    def __init__(self, currencypair=['BTC_USDT', 'ETH_USDT'], targe=['BTC_USDT'], notice=None):
        self.data = {}
        self.isReady = False
        self.currencypair = currencypair
        for a in self.currencypair:
            self.data.update({a: Traders()})
        self.caller = BittrexApi()
        self.targe = targe
        self.notice = notice
        self.restart = True

    def on_open(self, ws):
        for cp in self.currencypair:
            self.ws.subscribe('trader', reserve2(cp))

    def on_error(self, ws, msg):
        self.isReady = False
        logging.error(msg)

    def on_message(self, ws, message):
        if 'R' in message:
            message = message['R']
            cp = reserve(message['MarketName'])
            trades = {'asks': [], 'bids': []}
            for sides in ['Sells', 'Buys']:
                side = 'asks' if sides == 'Sells' else 'bids'
                if side == 'asks':
                    for a in message[sides]:
                        trades['asks'].append(td(a['Rate'], a['Quantity']))
                else:
                    for a in message[sides]:
                        trades['bids'].append(td(a['Rate'], a['Quantity']))
            self.data[cp].formate(trades, BITTREX)
            logging.info(MSG_RESET_TRADER_DATA.format(BITTREX, cp))
            self.isReady = True
            if cp in self.targe:
                callback(self.notice, cp)
        else:
            trades = {'asks': [], 'bids': []}
            cp = reserve(message['MarketName'])
            for sides in ['Sells', 'Buys']:
                side = 'asks' if sides == 'Sells' else 'bids'
                if side == 'asks':
                    for a in message[sides]:
                        trades['asks'].append(td(a['Rate'], a['Quantity']))
                else:
                    for a in message[sides]:
                        trades['bids'].append(td(a['Rate'], a['Quantity']))
            self.data[cp].formate(trades, 'Bittrex')
            self.isReady = True
            Min = min(list(map(float, self.data[cp].asks.keys())))
            Max = max(list(map(float, self.data[cp].bids.keys())))
            if cp in self.targe:
                if (not Min == self.data[cp].lastAsksLow) or (not Max == self.data[cp].lastBidsHigh):
                    self.data[cp].lastAsksLow = min(list(map(float, self.data[cp].asks.keys())))
                    self.data[cp].lastBidsHigh = max(list(map(float, self.data[cp].bids.keys())))
                    callback(self.notice, cp)

    def on_close(self, ws):
        self.isReady = False
        logging.warning(MSG_SOCKET_CLOSE.format(BITTREX, 'trader', timestampToDate()))
        if self.restart:
            time.sleep(1)
            logging.info(MSG_SOCKET_RESTART.format(BITTREX, 'trader'))
            self.start()

    def start(self):
        self.ws = SignalR(on_open=self.on_open, on_message=self.on_message,
                          on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
