from kernal.comparer import Comparer
from app.okex.okex import Okex

comparer = Comparer(exchange2=Okex(),currencypair=['BTC_USDT','ETH_USDT','ETH_BTC'],targe=['ETH_USDT'])
comparer.start()