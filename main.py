from kernal.comparer import Comparer
from app.bittrex.bittrex import Bittrex
from app.okex.okex import Okex

comparer = Comparer(exchange1=Bittrex(),currencypair=['BTC_USDT','ETH_USDT','ETH_BTC'],targe=['ETH_USDT'])
comparer.start()

#b = Bittrex()
#b.trader.start()