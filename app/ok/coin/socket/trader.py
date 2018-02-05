from threading import Thread
import websocket
from model.traders import Traders
from function import *
from app.ok.ex.socket.trader import Trader as exTrader

'''[{
    'data': {
        'asks': [
            ['11719.5', '0.001'],
            '
            '
            '
        ],
        'timestamp': 1516770794313,
        'bids': [
            ['10591.872', '0.79236926'],
            '
            '
            '
        ]
    },
    'binary': 0,
    'channel': 'ok_sub_spot_BTC_USDT_depth'
}]'''

class Trader(exTrader):
    def __init__(self, currencypair=['BTC_USDT'], targe=['BTC_USDT'], notice=None):
        self.p = True
        self.data = {}
        self.isReady = False
        self.currencypair = currencypair
        for a in self.currencypair:
            self.data.update({a: Traders()})
        self.lastTime = time.time()
        self.targe = targe
        self.notice = notice
        self.name = OKCOIN
        self.restart = True


    def on_open(self, ws):
        self.isReady = False
        for cp in self.currencypair:
            ws.send(json.dumps( {'event':'addChannel','channel':'ok_sub_spot_{}_depth'.format(cp.replace('USDT','USD'))}))

    def start(self):
        logging.info(MSG_SOCKET_START.format(self.name,'trader'))
        self.ws = websocket.WebSocketApp('wss://real.okcoin.com:10440/websocket', on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close, on_error=self.on_error)
        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
