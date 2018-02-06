import datetime
import matplotlib
import tkinter as tk
from threading import Thread
from tkinter import *

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from app.binance.binance import Binance
from app.bitfinex.bitfinex import Bitfinex
from app.bittrex.bittrex import Bittrex
from app.huobi.huobi import Huobi
from app.ok.okcoin import Okcoin
from app.ok.okex import Okex
from app.poloniex.poloniex import Poloniex
from function import *
from kernal.comparer import Comparer
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


pairs = ['BTC_USDT', 'ETH_USDT', 'LTC_USDT', 'ETH_BTC', 'LTC_BTC']


class Changer(Comparer):
    def __init__(self, exchange1=Poloniex(), exchange2=Huobi(), currencypair=['BTC_USDT'], targe=['BTC_USDT'],
                 page=None):
        logging.basicConfig(level=logging.INFO)
        self.exchange1 = exchange1
        self.exchange2 = exchange2
        self.exchange1.__init__(currencypair, targe)
        self.exchange2.__init__(currencypair, targe)
        self.exchange1.setTickerCompare(self.tickerCompare)
        self.exchange2.setTickerCompare(self.tickerCompare)
        self.exchange1.setTraderCompare(self.traderCompare)
        self.exchange2.setTraderCompare(self.traderCompare)
        self.t1 = Thread(target=self.exchange1.start)
        self.t2 = Thread(target=self.exchange2.start)
        self.noSupport = []
        self.page = page

    def tickerPrinter(self, currencyPair):
        nowtime = timestampToDate(time.time() - time.timezone)
        page = self.page.pages[currencyPair][0]
        page.tradeHistory[str(self.exchange1)][currencyPair].append(
            [str(self.exchange1.ticker.data[currencyPair].price),
             datetime.datetime.fromtimestamp(int(time.time()) + time.timezone)])
        page.tradeHistory[str(self.exchange2)][currencyPair].append(
            [str(self.exchange2.ticker.data[currencyPair].price),
             datetime.datetime.fromtimestamp(int(time.time()) + time.timezone)])
        if float(page.exchangeInfo[str(self.exchange1)]['price']['text']) < float(self.exchange1.ticker.data[currencyPair].price):
            page.exchangeInfo[str(self.exchange1)]['price']['fg'] = 'red'
        elif float(page.exchangeInfo[str(self.exchange1)]['price']['text']) > float(self.exchange1.ticker.data[currencyPair].price):
            page.exchangeInfo[str(self.exchange1)]['price']['fg'] = 'blue'

        if float(page.exchangeInfo[str(self.exchange2)]['price']['text']) < float(self.exchange2.ticker.data[currencyPair].price):
            page.exchangeInfo[str(self.exchange2)]['price']['fg'] = 'red'
        elif float(page.exchangeInfo[str(self.exchange2)]['price']['text']) > float(self.exchange2.ticker.data[currencyPair].price):
            page.exchangeInfo[str(self.exchange2)]['price']['fg'] = 'blue'

        page.exchangeInfo[str(self.exchange1)]['price']['text'] = str(self.exchange1.ticker.data[currencyPair].price)
        page.exchangeInfo[str(self.exchange2)]['price']['text'] = str(self.exchange2.ticker.data[currencyPair].price)

        if time.time() - page.time > 10:
            page.time = time.time()
            page.plot()

    def traderPrinter(self, currencyPair):
        askslow1 = min(list(map(float, self.exchange1.trader.data[currencyPair].asks.keys())))
        bidshigh1 = max(list(map(float, self.exchange1.trader.data[currencyPair].bids.keys())))
        askslow2 = min(list(map(float, self.exchange2.trader.data[currencyPair].asks.keys())))
        bidshigh2 = max(list(map(float, self.exchange2.trader.data[currencyPair].bids.keys())))
        nowtime = timestampToDate(time.time() - time.timezone)

        page = self.page.pages[currencyPair][0]
        page.exchangeInfo[str(self.exchange1)]['asks']['text'] = str(askslow1)
        page.exchangeInfo[str(self.exchange1)]['bids']['text'] = str(bidshigh1)
        page.exchangeInfo[str(self.exchange2)]['asks']['text'] = str(askslow2)
        page.exchangeInfo[str(self.exchange2)]['bids']['text'] = str(bidshigh2)


class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()


class PageMain(Page):
    def ClickStart(self):
        selectIndex = list(self.lb_pair.curselection())
        pairs = []
        for index in selectIndex:
            pairs.append(self.lb_pair.get(index))
        callback(self.notice, [self.v1.get(), self.v2.get()], pairs)

    def __init__(self, *args, **kwargs):
        self.notice = kwargs['notice']
        kwargs.pop('notice')
        Page.__init__(self, *args, **kwargs)
        self.v1 = StringVar(value=POLONIEX)
        self.v2 = StringVar(value=HUOBI)
        self.select1 = OptionMenu(self, self.v1, *EXCHANGES)
        self.select2 = OptionMenu(self, self.v2, *EXCHANGES)
        self.button1 = Button(self, text='Start', command=self.ClickStart)
        self.labprice = Label(self, text='price')
        self.lab1price = Label(self, text='0.0')
        self.lab2price = Label(self, text='0.0')
        self.lb_pair = Listbox(self, selectmode='multiple', exportselection=0)
        for i, cp in enumerate(pairs):
            self.lb_pair.insert(END, cp)

        Label(self, text='Exchange1').grid(row=0, column=0)
        self.select1.grid(row=0, column=1)
        Label(self, text='Exchange2').grid(row=1, column=0)
        self.select2.grid(row=1, column=1)
        self.button1.grid(row=4, column=0, columnspan=2)
        Label(self, text='Currency Pairs').grid(row=2, column=0)
        self.lb_pair.grid(row=2, column=1)


class PageCurrencypair(Page):
    def __init__(self, *args, **kwargs):
        self.exchanges = kwargs['exchanges']
        self.currencypair = kwargs['currencypair']
        self.tradeHistory = kwargs['tradeHistory']
        self.exchangeInfo = {}
        self.time = time.time()
        kwargs.pop('exchanges')
        kwargs.pop('currencypair')
        kwargs.pop('tradeHistory')
        Page.__init__(self, *args, **kwargs)
        for index, exchange in enumerate(self.exchanges):
            lab = Label(self, text=exchange)
            labPrice = Label(self, text=0.0)
            labAsksHigh = Label(self, text=0.0)
            labBidsLow = Label(self, text=0.0)

            lab.grid(row=index * 3, column=0)
            Label(self, text='price').grid(row=index * 3 + 1, column=0)
            labPrice.grid(row=index * 3 + 1, column=1)
            Label(self, text='Asks High :').grid(row=index * 3 + 2, column=0)
            labAsksHigh.grid(row=index * 3 + 2, column=1)
            Label(self, text='Bids High :').grid(row=index * 3 + 2, column=2)
            labBidsLow.grid(row=index * 3 + 2, column=3)
            self.exchangeInfo.update({exchange: {'price': labPrice, 'asks': labAsksHigh, 'bids': labBidsLow}})
        self.plot()

    def plot(self):
        history1 = self.tradeHistory[self.exchanges[0]][self.currencypair]
        history2 = self.tradeHistory[self.exchanges[1]][self.currencypair]
        x1 = [a[1] for a in history1]
        y1 = [float(a[0]) for a in history1]
        x2 = [a[1] for a in history2]
        y2 = [float(a[0]) for a in history2]
        fig = Figure(figsize=(6, 6))
        a = fig.add_subplot(111)
        a.plot(x1, y1)
        a.plot(x2, y2, color='red')
        a.set_title("{} Price".format(self.currencypair), fontsize=16)
        a.set_ylabel("Price", fontsize=14)
        a.set_xlabel("UTC Time", fontsize=14)
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().grid(row=6, column=1)
        canvas.draw()


class MainView(tk.Frame):
    def ClickStart(self, exchanges, pairs):
        self.tradeHistory = {exchanges[0]: {},
                             exchanges[1]: {}
                             }
        for a in self.pages:
            self.pages[a][0].destroy()
            self.pages[a][1].destroy()
        self.pages = {}
        for pair in pairs:
            self.tradeHistory[exchanges[0]].update({pair: getTradeHistory(exchanges[0], pair)})
            self.tradeHistory[exchanges[1]].update({pair: getTradeHistory(exchanges[1], pair)})
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
