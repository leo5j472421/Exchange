from kernal.comparer import Comparer
from app.bittrex.bittrex import Bittrex
from app.ok.okex import Okex
from app.poloniex.poloniex import Poloniex
from app.huobi.huobi import Huobi
from app.ok.okcoin import Okcoin
from app.bitfinex.bitfinex import Bitfinex
from app.binance.binance import Binance
import logging
comparer = Comparer(currencypair=[ 'BTC_USDT','LTC_USDT','ETH_USDT' ],targe=[ 'BTC_USDT','LTC_USDT','ETH_USDT' ] )
comparer.start()

logging.basicConfig(level=logging.INFO)
p = Binance(currencypair=['ETH_USDT' ],targe=['BTC_USDT','LTC_USDT','ETH_USDT'])

def tradeTest(cp):
    askslow1 = min(list(map(float, p.trader.data[cp].asks.keys())))
    bidshigh1 = max(list(map(float, p.trader.data[cp].bids.keys())))
    print("{}: {}'s Asks low : {} {}  Bids High : {} {} ".format(
        cp, p, askslow1,p.trader.data[cp].asks[str(askslow1)].amount, bidshigh1,p.trader.data[cp].bids[str(bidshigh1)].amount))
def tickerTest(cp):
    print("{}'Price : {} : {}  ".format(cp, p, str(
        p.ticker.data[cp].price)))

p.setTickerCompare(tickerTest)
p.setTraderCompare(tradeTest)
#p.trader.start()


