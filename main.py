from kernal.comparer import Comparer
from app.okex.okex import Okex

comparer = Comparer(exchange1=Okex(),currencypair=['BTC_USDT','ETH_USDT','ETC_BTC'],targe=['BTC_USDT'])
comparer.start()