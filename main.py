from kernal.comparer import Comparer
from app.bittrex.bittrex import Bittrex
from app.okex.okex import Okex
from app.poloniex.poloniex import Poloniex
from app.huobi.huobi import Huobi

comparer = Comparer(exchange2=Bittrex(), currencypair=['BTC_USDT','ETH_USDT','ETH_BTC'],targe=['BTC_USDT'])
comparer.start()

