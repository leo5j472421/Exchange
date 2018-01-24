import time,json,logging


def timestampToDate(timestamp, combine):
    timestamp = int(timestamp)
    if combine:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timestamp))
    else:
        return {'date': time.strftime("%Y-%m-%d", time.gmtime(timestamp)),
                'time': time.strftime("%H:%M:%S", time.gmtime(timestamp))}

def callback( cb, *args):
    if cb:
        try:
            cb(*args)
        except Exception as e:
            logging.error("error from callback {}: {}".format(cb, e))

def subscript(ws,cp,type='ticker'):
    if type == 'ticker':
        text = {'event':'addChannel','channel':'ok_sub_spot_{}_ticker'.format(cp)}
    elif type == 'trader':
        text = {'event':'addChannel','channel':'ok_sub_spot_{}_depth'.format(cp)}
    ws.send(json.dumps(text))
