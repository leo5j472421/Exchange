import time


class Ticker:
    def __init__(self):
        self.base = None
        self.quote = None
        self.price = 0.0
        self.volume = 0.0
        self.change = None
        self.lastprice = 0.0
        self.timestramp = time.time()

    def formate(self, data, base, quote):
        # self.change = float(data['percentChange']) * 100
        self.price = float(data['last_price'])
        self.base = base
        self.quote = quote
        self.volume = float(data['volume'])
        # self.change = (float(data['close'])-float(data['open']))/float(data['open'])
        if 'timestamp' in data:
            self.timestramp = float(data['timestamp'])
        else:
            self.timestramp = time.time()
