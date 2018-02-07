import logging

from kernal.ui.ui import *

'''
logging.basicConfig(level=logging.INFO)
comparer = Comparer(currencypair=['BTC_USDT', 'LTC_USDT', 'ETH_USDT'], targe=['BTC_USDT', 'LTC_USDT', 'ETH_USDT'])
comparer.start()




p = Binance(currencypair=['ETH_USDT' ],targe=['BTC_USDT','LTC_USDT','ETH_USDT'])

def tradeTest(cp):
    askslow1 = min(list(map(float, p.trader.data[cp].asks.keys())))
    bidshigh1 = max(list(map(float, p.trader.data[cp].bids.keys())))
    print("{}: {}'s Asks low : {} {}  Bids High : {} {} ".format(
        cp, p, askslow1, p.trader.data[cp].asks[str(askslow1)].amount, bidshigh1,
        p.trader.data[cp].bids[str(bidshigh1)].amount))


def tickerTest(cp):
    print("{}'Price : {} : {}  ".format(cp, p, str(
        p.ticker.data[cp].price)))


p.setTickerCompare(tickerTest)
p.setTraderCompare(tradeTest)
#p.ticker.start()
'''

if __name__ == "__main__":
    print('App Start Time : {}'.format(timestampToDate(int(time.time() - time.timezone))))
    root = tk.Tk()
    root.title('Exchange Compare')
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("1000x1000")
    root.mainloop()
