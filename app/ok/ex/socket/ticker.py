from threading import Thread

import websocket

import requests
from function import *
from model.ticker import Ticker as t

'''
[{
    'binary': 0,
    'channel': 'ok_sub_spot_BTC_USDT_ticker',
    'data': {
        'open': '10723.6206',
        'dayHigh': '11356.5536',
        'vol': '69175.3564',
        'close': '10599.9999',
        'timestamp': 1516770541514,
        'low': '9970',
        'dayLow': '10483.8011',
        'buy': '10600.4032',
        'high': '11356.5536',
        'sell': '10601.7996',
        'change': '213.7997',
        'last': '10601.7996'
    }
}]
'''


class Ticker:
    def __init__(self, notice=None, currencypair=['BTC_USDT', 'ETH_USDT'], targe=['BTC_USDT']):
        self.data = {}
        self.isReady = False
        self.currencypair = currencypair
        self.notice = notice
        self.targe = targe
        self.lastTime = time.time()
        self.name = 'OKEx'

    def on_open(self, ws):
        self.lastTime = time.time()
        for cp in self.currencypair:
            ws.send(json.dumps({'event':'addChannel','channel':'ok_sub_spot_{}_ticker'.format(cp)}))
            self.resetTicker(cp)
        self.isReady = True


    def resetTicker(self, cp):
        pair = cp.split('_')
        if self.name == 'OKCoin' :
            cp = cp.replace('USDT','USD' )
        data = json.loads(requests.get('https://www.{}.com/api/v1/ticker.do?symbol={}'.format(self.name,cp)).text)
        if 'error_code' in data:
             logging.error(data)
        elif 'tick' in data or 'ticker' in data :
            ts = data['date']
            if 'tick' in data:
                data = data['tick']
            else:
                data = data['ticker']
            #data.update( {'time': data['date'] } )
            tickData = {
                'price' : data['last'],
                'baseVolume' : data['vol'],
                'time' : ts
            }
            tick = t()
            tick.formate( tickData,pair[0],pair[1])
            tick.lastprice = tick.price
            if self.name == 'OKCoin':
                cp = cp.replace('USD', 'USDT')
            self.data.update({cp:tick})
            if cp in self.targe:
                callback(self.notice, cp)



    def on_error(self, ws, message):
        logging.error(message)
        self.isReady = False
        time.sleep(1)

    def on_message(self, ws, message):
        message = json.loads(message)
        if type(message) is dict:
            return  # {"event":"pong"}
        if time.time() - self.lastTime > 30:
            ws.send('{"event":"ping"}')
            self.lastTime = time.time()
        message = message[0]
        channel = message['channel'].replace('ok_sub_spot_', '').replace('_ticker', '')
        if self.name is 'OKCoin':
            channel = channel.replace('USD','USDT')
        cp = channel.upper()
        if 'result' in message['data'].keys():
            if message['data']['result']:
                logging.info('success subscript {}\' {} channel'.format(self.name,message['data']['channel']))
            else:
                logging.error(message['data']['error_msg'])
        elif channel in self.currencypair:
            pair = channel.upper().split('_')
            data = message['data']
            tickData = {
                'price' : data['last'],
                'baseVolume' : data['vol'],
            }
            tick = t()
            tick.formate( tickData,pair[0],pair[1])
            #ticker = t()
            #ticker.formate(message['data'], pair[0], pair[1])
            tick.lastprice = self.data[cp].price
            self.data.update({cp: tick})
            self.isReady = True
            if cp in self.targe:
                if not self.data[cp].lastprice == self.data[cp].price:
                    self.data[cp].lastprice = self.data[cp].price
                    callback(self.notice, cp)

    def on_close(self, ws):
        self.isReady = False
        logging.warning('{} Ticker----------------------------CLOSE WebSocket-----------------------'.format(self.name))
        logging.warning('Close Time : ' + timestampToDate(time.time() - time.timezone , True))
        time.sleep(1)
        logging.info('Restart {} Ticker Socket'.format(self.name))
        self.start()

    def start(self):
        logging.basicConfig(level=logging.INFO)
        logging.info('OKEx tick start')
        self.ws = websocket.WebSocketApp('wss://real.okex.com:10441/websocket', on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
