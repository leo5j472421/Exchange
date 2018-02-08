
from kernal.ui.page import *


from app.binance.binance import Binance
from app.bitfinex.bitfinex import Bitfinex
from app.bittrex.bittrex import Bittrex
from app.huobi.huobi import Huobi
from app.ok.okcoin import Okcoin
from app.ok.okex import Okex
from app.poloniex.poloniex import Poloniex
from kernal.ui.changer import Changer
from app.getTradeHistory import getTradeHistory


def getExchange(exchange):
    if exchange == POLONIEX:
        return Poloniex()
    elif exchange == HUOBI:
        return Huobi()
    elif exchange == OKEX:
        return Okex()
    elif exchange == OKCOIN:
        return Okcoin()
    elif exchange == BITTREX:
        return Bittrex()
    elif exchange == BITFINEX:
        return Bitfinex()
    elif exchange == BINANCE:
        return Binance()



class MainView(tk.Frame):
    def ClearPage(self):
        for a in self.pages:
            self.pages[a][0].destroy()
            self.pages[a][1].destroy()
        self.pages = {}

    def ClickStart(self, exchanges, pairs):

        self.tradeHistory = {exchanges[0]: {},
                             exchanges[1]: {}
                             }
        self.ClearPage()
        for pair in pairs:
            self.tradeHistory[exchanges[0]].update({pair: getTradeHistory(exchanges[0], pair)})
            self.tradeHistory[exchanges[1]].update({pair: getTradeHistory(exchanges[1], pair)})
            support = True
            for a in self.tradeHistory:
                if self.tradeHistory[a][pair] == None:
                    # self.ClearPage()
                    messagebox.showinfo('Alert', MSG_NOT_SUPPORT_CURRENCY_PAIR.format(a, pair))
                    support = False
            if support:
                page = PageCurrencypair(self, exchanges=exchanges, currencypair=pair, tradeHistory=self.tradeHistory)
                page.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
                button = tk.Button(self.buttonframe, text=pair, command=page.lift)
                button.pack(side="left")
                self.pages.update({pair: [page, button]})
        try:
            self.compare.close()
        except:
            pass
        self.compare = Changer(exchange1=getExchange(exchanges[0]), exchange2=getExchange(exchanges[1]),
                               currencypair=pairs, targe=pairs, page=self)
        self.compare.start()

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        p1 = PageMain(self, notice=self.ClickStart)
        self.pages = {}
        self.tradeHistory = {}
        self.buttonframe = tk.Frame(self)
        self.container = tk.Frame(self)
        self.buttonframe.pack(side="top", fill="x", expand=False)
        self.container.pack(side="top", fill="both", expand=True)
        p1.place(in_=self.container, x=0, y=0, relwidth=1, relheight=1)
        b1 = tk.Button(self.buttonframe, text="Setting", command=p1.lift)
        b1.pack(side="left")
        p1.show()


if __name__ == "__main__":
    root = tk.Tk()
    root.title('Exchange Compare')
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("800x800")
    root.mainloop()
