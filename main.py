from kernal.comparer import Comparer
from app.bittrex.bittrex import Bittrex
from app.ok.okex import Okex
from app.poloniex.poloniex import Poloniex
from app.huobi.huobi import Huobi
from app.ok.okcoin import Okcoin

#comparer = Comparer(exchange1=Okcoin(),exchange2=Okex(), currencypair=['BTC_USDT','ETH_USDT','ETH_BTC'],targe=['BTC_USDT'])
#comparer.start()


o = Bittrex()
o.trader.start()

