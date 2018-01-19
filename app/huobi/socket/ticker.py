import websocket, traceback, sys, gzip
from ..model.ticker import Ticker as t
from ..function import *
from threading import Thread
from ..HuobiServices import *
import logging

class Ticker:
    def __init__(self, notice=None,currencypair=['BTC_USDT','ETH_USDT'],targe=['BTC_USDT']):
        self.data = {}
        self.isReady = False
        self.currencypair = {}
        for a in currencypair:
            self.currencypair.update({a.replace('_','').lower():a})
        self.notice = notice
        self.targe = targe

    def _callback(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except Exception as e:
                logging.error("error from callback {}: {}".format(callback, e))

    def getAllTickerData(self):
        self.currencypair = get_symbolArray()

        """
        print(symbols)
        for symbol in symbols:
            pair = symbols[symbol].split('_')
            data = get_ticker(symbol)['tick']
            tick = t()
            tick.formate(data, pair[0], pair[1])
            self.data.update({symbols[symbol]: tick})
        print(self.data['BTC_USDT'].price)
        """
    def on_open(self, ws):
        #self.getAllTickerData()
        self.isReady = False
        for cp in self.currencypair:
            subscript(ws,cp)
        # self.getTickerData()
        logging.info('init huobi\'s market Data')

    def on_message(self, ws, message):
        message = json.loads(gzip.decompress(message).decode('utf-8'))
        if 'tick' in message :
            channel = message['ch'][message['ch'].find('.')+1:][0:message['ch'].find('.')+1]
            if channel in self.currencypair:
                self.isReady = True
                pair = self.currencypair[channel].split('_')
                data = message['tick']
                tick = t()
                tick.formate(data, pair[0], pair[1])
                self.data.update({self.currencypair[channel]:tick})
                if self.currencypair[channel] in self.targe :
                    self._callback(self.notice,self.currencypair[channel])
        elif 'status' in message:
            if message['status'] == 'ok':
                logging.info('subscript {} channel success'.format(message['subbed']))
            elif message['status'] == 'error':
                logging.error( message['status']['err-msg'] )
                return
        elif 'ping' in message:
            self.ws.send(json.dumps({"pong": message['ping']}))

    def on_error(self,ws,message):
        logging.error(message)
        self.isReady = False
        time.sleep(1)
        logging.info('Restart The Socket')
        self.start()

    def on_close(self, ws):
        self.isReady = False
        logging.warning('----------------------------CLOSE WebSocket-----------------------')
        logging.warning('Close Time : ' + timestampToDate(int(time.mktime(time.localtime())), True))
        time.sleep(1)
        logging.info('Restart The Socket')
        self.start()

    def start(self):
        logging.info('huobi tick start')
        self.ws = websocket.WebSocketApp('wss://api.huobi.pro/ws', on_open=self.on_open, on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
