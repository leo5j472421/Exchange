import logging
import time

import cfscrape
from signalr import Connection

'''
Websocket like SignalR
base on WebsocketApp
'''


class SignalR(object):

    def __init__(self, header=None,
                 on_open=None, on_message=None, on_error=None,
                 on_close=None, ):

        self.header = header if header is not None else []
        self.on_open = on_open
        self.on_message = on_message
        self.on_error = on_error
        self.on_close = on_close
        self.keep_running = False
        self.conn = None
        self.corehub = None
        self.cps = []

    def r(self, **kwargs):
        msg = kwargs
        if 'R' in msg and type(msg['R']) is not bool:
            if 'MarketName' in msg['R'] and msg['R']['MarketName'] is None:
                msg['R']['MarketName'] = self.cps[0]
                self.cps.pop(0)
                del msg['R']['Fills']
                self.received(kwargs)

    def received(self, data):
        self._callback(self.on_message, data)

    def subscribe(self, channel, cp='BTC-USDT'):
        self.cps.append(cp)
        if channel == 'ticker':
            self.corehub.server.invoke('SubscribeToSummaryDeltas')
            logging.info('Subscribe Bittrex\'s updateSummaryState')
        elif channel == 'trader':
            self.corehub.server.invoke('SubscribeToExchangeDeltas', cp)
            self.corehub.server.invoke('queryExchangeState', cp)
            logging.info('Subscribe Bittrex\'s {} updateExchangeState '.format(cp))

    def close(self):
        self.keep_running = False
        if self.conn:
            self.conn.close
        self._callback(self.on_close)

    def run_forever(self,
                    ping_interval=0, ping_timeout=None, ):

        if ping_timeout and ping_interval and ping_interval <= ping_timeout:
            raise logging.warning("Ensure ping_interval > ping_timeout")
        if self.conn:
            raise logging.warning("connection is already opened")
        thread = None
        self.keep_running = True

        try:
            logging.info('Trying to establish connection to Bittrex through https://socket-stage.bittrex.com/signalr')
            with cfscrape.create_scraper() as connection:
                self.conn = Connection(None, connection)
            self.conn.received += self.r  #
            self.conn.url = 'https://socket-stage.bittrex.com/signalr'
            self.corehub = self.conn.register_hub('coreHub')
            self.conn.start()
            logging.info(
                'Connection to Bittrex established successfully through https://socket-stage.bittrex.com/signalr')
            self._callback(self.on_open)

            self.corehub.client.on('updateSummaryState', self.received)
            self.corehub.client.on('updateExchangeState', self.received)

            while self.conn.started:
                if not self.keep_running:
                    break
                self.conn.wait(1)                   #Data will receive when connection is waiting

        except (Exception, KeyboardInterrupt, SystemExit) as e:
            self._callback(self.on_error, e)
        finally:
            if thread and thread.isAlive():
                thread.join()
            self.keep_running = False
            self._callback(self.on_close)
            self.conn = None
            self.corehub = None

    def _callback(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except Exception as e:
                logging.error("error from callback {}: {}".format(callback, e))
