import time,json


def timestampToDate(timestamp, combine):
    timestamp = int(timestamp)
    if combine:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(timestamp))
    else:
        return {'date': time.strftime("%Y-%m-%d", time.gmtime(timestamp)),
                'time': time.strftime("%H:%M:%S", time.gmtime(timestamp))}

def subscript(ws, channal):
    text = {'command': 'subscribe', 'channel': channal}
    ws.send(json.dumps(text))
    #print(json.dumps(text))  # TickerEvent

def reserve(s):
    pair = s.split('_')
    return '{}_{}'.format(pair[1],pair[0])
