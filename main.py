from kernal.comparer import Comparer
from app.bittrex.bittrex import Bittrex
from app.ok.okex import Okex
from app.poloniex.poloniex import Poloniex
from app.huobi.huobi import Huobi
from app.ok.okcoin import Okcoin
from app.bitfinex.bitfinex import Bitfinex
import logging
comparer = Comparer(exchange1=Bitfinex(),exchange2=Okcoin(), currencypair=['BTC_USDT','ETH_USDT','ETH_BTC'],targe=['BTC_USDT','ETH_USDT'])
comparer.start()

#logging.basicConfig(level=logging.INFO)

#o = Bitfinex()
#o.trader.start()

