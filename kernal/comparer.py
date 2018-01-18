from app.poloniex.poloniex import Poloniex
from app.huobi.huobi import Huobi
from threading import Thread
from app.huobi.function import *
import logging, time


class Comparer:
    def __init__(self, exchange1=Poloniex(), exchange2=Huobi(), currencypair=['BTC_USDT'], targe=['BTC_USDT']):
        logging.basicConfig(level=logging.INFO)
        self.exchange1 = exchange1
        self.exchange2 = exchange2
        self.exchange1.setTickerCompare(self.tickerCompare)
        self.exchange2.setTickerCompare(self.tickerCompare)

    def setTarge(self, array):
        self.exchange1.ticker.targe = array
        self.exchange2.ticker.targe = array

    def tickerCompare(self, ticker, currencyPair):
        if not self.exchange1.ticker.isReady:
            logging.warning(self.exchange1.name + '\'s ticker is not Ready ')
        elif not self.exchange2.ticker.isReady:
            logging.warning(self.exchange2.name + '\'s ticker is not Ready ')
        else:
            print(currencyPair + ': ' + self.exchange1.name + ' : ' + str(
                self.exchange1.ticker.data[currencyPair].price) + ' ' +
                self.exchange2.name + ' : ' + str(
                self.exchange2.ticker.data[currencyPair].price) + ' time : ' + timestampToDate(time.time(), True))

    def start(self):
        logging.info('compare start')
        t1 = Thread(target=self.exchange1.start)
        t2 = Thread(target=self.exchange2.start)
        t1.start()
        t2.start()
