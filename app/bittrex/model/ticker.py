import time,datetime
'''
{
    'BaseVolume': 100.15802301,
    'Volume': 1293917.88121596,
    'OpenBuyOrders': 411,
    'Bid': 7.46e-05,
    'PrevDay': 7.78e-05,
    'Ask': 7.461e-05,
    'TimeStamp': '2018-01-23T03:33:48.247',
    'OpenSellOrders': 5812,
    'Low': 7.298e-05,
    'High': 8.28e-05,
    'MarketName': 'BTC-1ST',
    'Last': 7.461e-05,
    'Created': '2017-06-06T01:22:35.727'
}
'''
class Ticker:
    def __init__(self):
        self.base = None
        self.quote = None
        self.price = 0.0
        self.volume = 0.0
        self.change = None
        self.timestramp = time.time()

    def formate(self, data, base, quote):
        self.price = float(data['Last'])
        self.base = base
        self.quote = quote
        self.volume = float(data['Volume'])
        try:
            dt = datetime.datetime.strptime(data['TimeStamp'], '%Y-%m-%dT%H:%M:%S.%f')
        except:
            dt = datetime.datetime.strptime(data['TimeStamp'], '%Y-%m-%dT%H:%M:%S')
        ts = dt.timestamp() + 8 * 3600  # time zone problem
        self.timestramp = ts
