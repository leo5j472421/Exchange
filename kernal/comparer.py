from threading import Thread
from function import  *
from app.huobi.huobi import Huobi
from app.poloniex.poloniex import Poloniex

class Comparer:
    def __init__(self, exchange1=Poloniex(), exchange2=Huobi(), currencypair=['BTC_USDT'], targe=['BTC_USDT']):
        logging.basicConfig(level=logging.INFO)
        self.exchange1 = exchange1
        self.exchange2 = exchange2
        self.exchange1.__init__(currencypair, targe)
        self.exchange2.__init__(currencypair, targe)
        self.exchange1.setTickerCompare(self.tickerCompare)
        self.exchange2.setTickerCompare(self.tickerCompare)
        self.exchange1.setTraderCompare(self.tradercompare)
        self.exchange2.setTraderCompare(self.tradercompare)
        self.t1 = Thread(target=self.exchange1.start)
        self.t2 = Thread(target=self.exchange2.start)
        self.noSupport = []

    def setTarge(self, array):
        self.exchange1.ticker.targe = array
        self.exchange2.ticker.targe = array

    def tickerCompare(self, currencyPair):
        if currencyPair in self.noSupport:
            return
        elif not self.exchange1.ticker.isReady:
            logging.warning('{}\'s ticker is not Ready '.format(self.exchange1))
        elif not self.exchange2.ticker.isReady:
            logging.warning('{}\'s ticker is not Ready '.format(self.exchange2))
        else:
            nowtime = timestampToDate(time.time() - time.timezone)
            try:
                print("{}'s Price : {} : {} , {} : {} time : {} ".format(currencyPair, self.exchange1, str(
                    self.exchange1.ticker.data[currencyPair].price), self.exchange2,
                                                                       str(self.exchange2.ticker.data[
                                                                               currencyPair].price),
                                                                       nowtime))
            except KeyError:
                if currencyPair not in self.exchange1.ticker.data:
                    logging.warning('{} ticker is not support {} currency pair '.format(self.exchange1, currencyPair))
                else:
                    logging.warning('{} ticker is not support {} currency pair '.format(self.exchange2, currencyPair))
                #self.noSupport.append(currencyPair)

    def tradercompare(self, currencyPair):
        if currencyPair in self.noSupport:
            return
        try:
            if not self.exchange1.trader.isReady:
                logging.warning('{}\'s trader is not Ready '.format(self.exchange1))
            elif not self.exchange2.trader.isReady:
                logging.warning('{}\'s trader is not Ready '.format(self.exchange2))
            else:
                askslow1 = min(list(map(float, self.exchange1.trader.data[currencyPair].asks.keys())))
                bidshigh1 = max(list(map(float, self.exchange1.trader.data[currencyPair].bids.keys())))
                askslow2 = min(list(map(float, self.exchange2.trader.data[currencyPair].asks.keys())))
                bidshigh2 = max(list(map(float, self.exchange2.trader.data[currencyPair].bids.keys())))
                nowtime = timestampToDate(time.time() - time.timezone)
                print("{}: {}'s Asks low : {}  Bids High : {} , {}'s Asks low : {}  Bids High : {} time : {} ".format(
                    currencyPair, self.exchange1, askslow1, bidshigh1, self.exchange2, askslow2, bidshigh2, nowtime))
        except ValueError:
            if len(self.exchange1.trader.data[currencyPair].asks) == 0:
                logging.warning('{} trader is not support {} currency pair '.format(self.exchange1, currencyPair))
            else:
                logging.warning('{} trader is not support {} currency pair '.format(self.exchange2, currencyPair))
            #self.noSupport.append(currencyPair)

    def start(self):
        logging.info('compare start')
        self.t1.start()
        self.t2.start()
