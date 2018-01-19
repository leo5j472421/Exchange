from .polonixeApi import PoloniexApi
from .socket.ticker import Ticker
from .socket.trader import Trader


class Poloniex:

    def __init__(self, currencypair=['BTC_USDT'], targe=['BTC_USDT']):
        self.ticker = Ticker(targe=targe)
        self.trader = Trader(currencypair=currencypair)
        self.caller = PoloniexApi()
        self.name = 'Poloniex'

    def __call__(self, currencypair, targe):
        self.ticker.targe = targe
        self.trader.currencypair = currencypair

    def start(self):
        self.ticker.start()
        self.trader.start()

    def setTickerCompare(self, function ):
        self.ticker.notice = function

    def setTraderCompare(self, function):
        self.trader.notice = function
