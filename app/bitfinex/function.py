import json
import logging
import time


def timestampToDate(timestamp, combine=True):
    timestamp = int(timestamp)
    if combine:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timestamp))
    else:
        return {'date': time.strftime("%Y-%m-%d", time.gmtime(timestamp)),
                'time': time.strftime("%H:%M:%S", time.gmtime(timestamp))}


def callback(cb, *args):
    if cb:
        try:
            cb(*args)
        except Exception as e:
            logging.error("error from callback {}: {}".format(cb, e))


def subscript(ws, cp, type='ticker'):

    text = {'event': 'subscribe', 'channel': type , 'symbol': cp.replace('_','' ) }
    ws.send(json.dumps(text))
    # print(json.dumps(text))  # TickerEvent
