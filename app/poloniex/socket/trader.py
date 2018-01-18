from ..model.trader import Trader as td
from ..model.traders import Traders
import websocket
from threading import Thread
from ..function import *
from ..arrary import Array
import logging


class Trader:
    def __init__(self, currencypair=['BTC_USDT', 'ETH_USDT', 'ETH_BTC', 'ZEC_BTC'], notice=None):
        self.p = True
        self.data = {}
        self.isReady = False
        self.currencypair = currencypair
        for a in currencypair:
            self.data.update({a: Traders()})
        self.marketChannel = []
        self.notice = notice

    def updateTotal(self, side, rate, total, amount, cp):
        if side == 'bids':  # update total
            if rate in self.data[cp].bids:
                self.data[cp].total[1] -= self.data[cp].bids[rate].total
            self.data[cp].total[1] += total
        else:
            if rate in self.data[cp].asks:
                self.data[cp].total[0] -= self.data[cp].asks[rate].amount
            self.data[cp].total[0] += amount

    def initOrder(self, rate, amount, side, cp):
        trade = td(float(rate), float(amount))
        self.updateTotal(side, rate, trade.total, trade.amount, cp)
        if side == 'asks':
            self.data[cp].asks.update({rate: trade})
        else:
            self.data[cp].bids.update({rate: trade})

    def modifyTrade(self, order, side, cp):
        rate = order['rate']
        amount = float(order['amount'])
        total = float(rate) * amount
        trade = td(float(rate), amount)
        self.updateTotal(side, rate, total, amount, cp)
        if side == 'asks':
            self.data[cp].asks.update({rate: trade})
        else:
            self.data[cp].bids.update({rate: trade})

    def removeTrade(self, rate, side, cp):
        if side == 'asks':
            if rate in self.data[cp].asks:
                self.data[cp].total[0] -= self.data[cp].asks[rate].amount
                self.data[cp].asks.pop(rate)
            else:
                logging.warning(rate + ' is not found in asks\'s ' + side + ' order')
        else:
            if rate in self.data[cp].bids:
                self.data[cp].total[1] -= self.data[cp].bids[rate].total
                self.data[cp].bids.pop(rate)
            else:
                logging.warning(rate + ' is not found in bids\'s ' + side + ' order')

    def traderEvent(self, args, cp):
        for data in args:
            type = data['type']
            if type == 'newTrade':
                pass
            elif type == 'orderBookModify' or type == 'orderBookRemove':
                order = data['data']
                side = order['type'] + 's'
                if type == 'orderBookModify':
                    self.modifyTrade(order, side, cp)
                else:
                    self.removeTrade(order['rate'], side, cp)

    def on_open(self, ws):
        self.isReady = False
        for c in self.currencypair:
            subscript(self.ws, reserve(c))

    def on_message(self, ws, message):
        message = json.loads(message)
        if 'error' in message:
            logging.error(message)
            return
        if message[0] in self.marketChannel:
            if message[1] == 2:
                return
            args = []
            cp = reserve(Array.markets['byID'][str(message[0])]['currencyPair'])
            for i in message[2]:
                if i[0] == 'o':
                    args.append({
                        'type': 'orderBookRemove' if i[3] == '0.00000000' else "orderBookModify",
                        'data': {
                            'type': "bid" if i[1] == 1 else 'ask',
                            'rate': i[2],
                            'amount': i[3]
                        }
                    })
                elif i[0] == 't':
                    args.append({
                        'type': 'newTrade',
                        'data': {'tradeID': i[1],
                                 'type': 'buy' if i[2] == 1 else 'sell',
                                 'rate': i[3],
                                 'amount': i[4],
                                 'total': float(i[3]) * float(i[4]),
                                 'date': timestampToDate(i[5], True)
                                 }
                    })
            self.traderEvent(args, cp)
        elif message[0] < 1000:
            cp = reserve(Array.markets['byID'][str(message[0])]['currencyPair'])
            if message[2][0][0] == 'i':
                logging.info('success subscript channel ' + reserve(cp) )
                self.marketChannel.append(message[0])
                data = message[2][0][1]['orderBook']
                logging.info('Init ' + cp + '\'s Order Book Data: ' + str(len(data[0]) + len(data[1])))
                for a in [0, 1]:
                    side = 'asks' if a == 0 else 'bids'
                    for i in data[a]:
                        self.initOrder(i, data[a][i], side, cp)

    def on_close(self, ws ):
        self.isReady = False
        logging.warning('----------------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart The Socket')
        self.start()

    def start(self):
        logging.info('poloniex trader start')
        self.ws = websocket.WebSocketApp('wss://api2.poloniex.com', on_open=self.on_open, on_message=self.on_message,
                                         on_close=self.on_close)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
