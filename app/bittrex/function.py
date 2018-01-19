import time, json
from datetime import datetime


def timestampToDate(timestamp, combine=True):
    timestamp = int(timestamp)
    if combine:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timestamp))
    else:
        return {'date': time.strftime("%Y-%m-%d", time.gmtime(timestamp)),
                'time': time.strftime("%H:%M:%S", time.gmtime(timestamp))}


def reserve(s):  # BTC-1ST to 1ST_BTC
    s = s.split('-')
    return s[1] + '_' + s[0]

def reserve2(s):  #  1ST_BTC to BTC-1ST
    s = s.split('_')
    return s[1] + '-' + s[0]
