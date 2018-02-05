import json
import time,logging
from constant import *

def timestampToDate(timestamp=time.time()-time.timezone, combine=True):
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







