import time,datetime
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
        self.price = float(data['price'])
        self.base = base
        self.quote = quote
        self.volume = float(data['baseVolume'])
        self.timestramp = time.time()
        try :
            self.change = float(data['change'])
        except:
            self.change = None