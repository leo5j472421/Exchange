from app.poloniex.poloniex import Poloniex
from app.poloniex.function import *
from app.huobi.HuobiServices import *
from app.huobi.huobi import Huobi
#from .huobi.HuobiServices import *
a = Poloniex
def tickerCompare(n,c):
    if n.isReady:
        print('Price : ' + str(n.data['BTC_USDT'].price) + ' Volume : ' + str(
            n.data['BTC_USDT'].volume) + '  Change : ' + str(n.data['BTC_USDT'].change)
            + ' ' + timestampToDate(int(time.time()), True))

#poloniex = Poloniex(tickerCompare=tickerCompare)
#poloniex.start()
huobi = Huobi()
huobi.ticker.notice = tickerCompare
huobi.ticker.start()
