from ..model.trader import Trader as td
from ..model.traders import Traders
import websocket,gzip
from threading import Thread
from ..function import *
import logging

class Trader:
    def __init__(self, currencypair=['BTC_USDT']):
        self.p = True
        self.data = {}
        self.resetData(currencypair)
        self.isReady = False
        self.currencypair = {}
        for a in currencypair:
            self.currencypair.update({a.replace('_','').lower():a})

    def resetData(self,currencypair):
        self.data = {}
        for a in currencypair:
            self.data.update({a: Traders()})

    def on_open(self, ws):
        self.isReady = False
        for c in self.currencypair:
            subscript(ws, c , 'trader' )


    def on_message(self, ws, message):
        message = json.loads(gzip.decompress(message).decode('utf-8'))
        if 'tick' in message :
            channel = message['ch'][message['ch'].find('.')+1:][0:message['ch'].find('.')+1]
            if channel in self.currencypair:
                self.isReady = True
                self.resetData(self.currencypair.values())
                data = message['tick']
                for side in data :
                    if side == 'asks':
                        for a in data['asks']:
                            trade = td(a[0], a[1])
                            self.data[self.currencypair[channel]].asks.update({str(a[0]):trade})
                            self.data[self.currencypair[channel]].total[0] += trade.amount
                    else:
                        for a in data['bids']:
                            trade = td(a[0], a[1])
                            self.data[self.currencypair[channel]].bids.update({str(a[0]):trade})
                            self.data[self.currencypair[channel]].total[1] += trade.total
        elif 'status' in message:
            if message['status'] == 'ok':
                logging.info('subscript {} channel success'.format(message['subbed']))
            elif message['status'] == 'error':
                logging.error( message['status']['err-msg'] )
                return
        elif 'ping' in message:
            self.ws.send(json.dumps({"pong": message['ping']}))
    def on_close(self, ws):
        self.isReady = False
        logging.warning('----------------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart The Socket')
        self.start()

    def start(self):
        logging.info('huobi trader start')
        self.ws = websocket.WebSocketApp('wss://api.huobi.pro/ws', on_open=self.on_open, on_message=self.on_message,
                                         on_close=self.on_close)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
