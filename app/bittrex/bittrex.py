from .socket.ticker import *
from .socket.trader import *
class Bittrex:
    def __init__(self,currencypair=['BTC_USDT'],targe=['BTC_USDT']):
        self.ticker = Ticker(targe=targe)
        self.trader = Trader(currencypair=currencypair,targe=targe)

    def __str__(self):
        return BITTREX

    def __call__(self, currencypair, targe):
        self.ticker.targe = targe
        self.ticker.currencypair = currencypair
        self.trader.currencypair = currencypair

    def start(self):
        self.ticker.start()
        self.trader.start()

    def setTickerCompare(self,function):
        self.ticker.notice = function

    def setTraderCompare(self,function):
        self.trader.notice =function