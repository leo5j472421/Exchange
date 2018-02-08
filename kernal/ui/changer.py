from kernal.comparer import *
import datetime

class Changer(Comparer):
    def __init__(self, exchange1=Poloniex(), exchange2=Huobi(), currencypair=['BTC_USDT'], targe=['BTC_USDT'],
                 page=None):
        logging.basicConfig(level=logging.INFO)
        self.exchange1 = exchange1
        self.exchange2 = exchange2
        self.exchange1.__init__(currencypair, targe)
        self.exchange2.__init__(currencypair, targe)
        self.exchange1.setTickerCompare(self.tickerCompare)
        self.exchange2.setTickerCompare(self.tickerCompare)
        self.exchange1.setTraderCompare(self.traderCompare)
        self.exchange2.setTraderCompare(self.traderCompare)
        self.t1 = Thread(target=self.exchange1.start)
        self.t2 = Thread(target=self.exchange2.start)
        self.noSupport = []
        self.page = page

    def tickerPrinter(self, currencyPair):
        page = self.page.pages[currencyPair][0]
        page.tradeHistory[str(self.exchange1)][currencyPair].append(
            [str(self.exchange1.ticker.data[currencyPair].price),
             datetime.datetime.fromtimestamp(int(time.time()) + time.timezone)])
        page.tradeHistory[str(self.exchange2)][currencyPair].append(
            [str(self.exchange2.ticker.data[currencyPair].price),
             datetime.datetime.fromtimestamp(int(time.time()) + time.timezone)])
        if float(page.exchangeInfo[str(self.exchange1)]['price']['text']) < float(
                self.exchange1.ticker.data[currencyPair].price):
            page.exchangeInfo[str(self.exchange1)]['price']['fg'] = 'red'
        elif float(page.exchangeInfo[str(self.exchange1)]['price']['text']) > float(
                self.exchange1.ticker.data[currencyPair].price):
            page.exchangeInfo[str(self.exchange1)]['price']['fg'] = 'blue'

        if float(page.exchangeInfo[str(self.exchange2)]['price']['text']) < float(
                self.exchange2.ticker.data[currencyPair].price):
            page.exchangeInfo[str(self.exchange2)]['price']['fg'] = 'red'
        elif float(page.exchangeInfo[str(self.exchange2)]['price']['text']) > float(
                self.exchange2.ticker.data[currencyPair].price):
            page.exchangeInfo[str(self.exchange2)]['price']['fg'] = 'blue'

        page.exchangeInfo[str(self.exchange1)]['price']['text'] = str(self.exchange1.ticker.data[currencyPair].price)
        page.exchangeInfo[str(self.exchange2)]['price']['text'] = str(self.exchange2.ticker.data[currencyPair].price)

        if time.time() - page.time > 10:
            page.time = time.time()
            page.plot()

    def traderPrinter(self, currencyPair):
        askslow1 = min(list(map(float, self.exchange1.trader.data[currencyPair].asks.keys())))
        bidshigh1 = max(list(map(float, self.exchange1.trader.data[currencyPair].bids.keys())))
        askslow2 = min(list(map(float, self.exchange2.trader.data[currencyPair].asks.keys())))
        bidshigh2 = max(list(map(float, self.exchange2.trader.data[currencyPair].bids.keys())))

        page = self.page.pages[currencyPair][0]
        page.exchangeInfo[str(self.exchange1)]['asks']['text'] = str(askslow1)
        page.exchangeInfo[str(self.exchange1)]['bids']['text'] = str(bidshigh1)
        page.exchangeInfo[str(self.exchange2)]['asks']['text'] = str(askslow2)
        page.exchangeInfo[str(self.exchange2)]['bids']['text'] = str(bidshigh2)

