import time


class Ticker:
    def __init__(self):
        self.base = None
        self.quote = None
        self.price = 0.0
        self.volume = 0.0
        self.change = None
        self.timestramp = time.time()

    def formate(self, data, base, quote):
        self.change = float(data['percentChange']) * 100
        self.price = float(data['last'])
        self.base = base
        self.quote = quote
        self.volume = float(data['baseVolume'])
        self.timestramp = time.time()
