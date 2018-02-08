import tkinter as tk
import  time
from tkinter import *
from tkinter import messagebox

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from function import *

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()


class PageMain(Page):
    def ClickStart(self):
        selectIndex = list(self.lb_pair.curselection())
        if selectIndex == []:
            messagebox.showinfo('Alert', 'Please Select Currency Pair')
            return
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
        for i, cp in enumerate(PAIRS):
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
        self.fig = Figure()
        self.p = self.fig.add_subplot(1, 1, 1)
        self.plot()
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=6, column=1)
        toolbar_frame = Frame(self)
        toolbar_frame.grid(row=7, column=1)
        toolbar = NavigationToolbar2TkAgg(self.canvas, toolbar_frame)
        self.canvas.draw()

    def plot(self):
        history1 = self.tradeHistory[self.exchanges[0]][self.currencypair]
        history2 = self.tradeHistory[self.exchanges[1]][self.currencypair]
        x1 = [a[1] for a in history1]
        y1 = [float(a[0]) for a in history1]
        x2 = [a[1] for a in history2]
        y2 = [float(a[0]) for a in history2]
        self.p.clear()
        self.p.plot(x1, y1, 'b-', label=self.exchanges[0])
        self.p.plot(x2, y2, 'r-', label=self.exchanges[1])
        self.p.set_title("{} Price".format(self.currencypair), fontsize=16)
        self.p.set_ylabel("Price", fontsize=14)
        self.p.set_xlabel("UTC Time", fontsize=14)
        self.p.grid(True, linestyle='-.')
        self.fig.autofmt_xdate()
        self.p.legend()
        try:
            self.canvas.draw()
        except:
            pass
