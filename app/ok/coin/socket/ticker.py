from threading import Thread
import websocket
from app.ok.ex.socket.ticker import Ticker as exTicker
from app.ok.function import *

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


class Ticker(exTicker):

    def __init__(self, notice=None, currencypair=['BTC_USDT', 'ETH_USDT'], targe=['BTC_USDT']):
        self.data = {}
        self.isReady = False
        self.currencypair = currencypair
        self.notice = notice
        self.targe = targe
        self.lastTime = time.time()
        self.name = 'OKCoin'

    def on_open(self, ws):
        self.lastTime = time.time()
        self.isReady = False
        for cp in self.currencypair:
            self.resetTicker(cp)
            ws.send(json.dumps({'event':'addChannel','channel':'ok_sub_spot_{}_ticker'.format(cp.replace('USDT','USD'))}))

    def start(self):
        logging.basicConfig(level=logging.INFO)
        logging.info('OKCoin tick start')
        self.ws = websocket.WebSocketApp('wss://real.okcoin.com:10440/websocket', on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
