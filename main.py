from kernal.comparer import Comparer
from app.bittrex.bittrex import Bittrex
from app.ok.okex import Okex
from app.poloniex.poloniex import Poloniex
from app.huobi.huobi import Huobi
from app.ok.okcoin import Okcoin
from app.bitfinex.bitfinex import Bitfinex
import logging
comparer = Comparer(exchange1=Bitfinex() ,currencypair=['BTC_USDT', 'ETH_USDT' , 'LTC_USDT','ETH_BTC','LTC_BTC' ],targe=['BTC_USDT','LTC_USDT','ETH_BTC'] )
comparer.start()


logging.basicConfig(level=logging.INFO)
#p = Bitfinex()

def tradeTest(cp):
    askslow1 = min(list(map(float, p.trader.data[cp].asks.keys())))
    bidshigh1 = max(list(map(float, p.trader.data[cp].bids.keys())))
    print("{}: {}'s Asks low : {}  Bids High : {} ".format(
        cp, p, askslow1, bidshigh1 ))
def tickerTest(cp):
    print("{}'Price : {} : {}  ".format(cp, p, str(
        p.ticker.data[cp].price)))

#p.setTickerCompare(tickerTest)
#p.setTraderCompare(tradeTest)
#p.start()
