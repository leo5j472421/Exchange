from .socket.ticker import Ticker
from .socket.trader import Trader
class Bittrex:
    def __init__(self,currencypair=['ETH_USDT','BTC_USDT','ETH_BTC'],targe=['ETH_USDT']):
        self.ticker = Ticker(targe=targe)
        self.trader = Trader(currencypair=currencypair)
        self.name = 'Bittrex'

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