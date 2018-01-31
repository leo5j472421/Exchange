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
        try :
          self.change = float(data['change'])
          self.timestramp = data['time']
        except KeyError :
            try:
                dt = datetime.datetime.strptime(data['TimeStamp'], '%Y-%m-%dT%H:%M:%S.%f')
                if time.daylight:
                    ts = dt.timestamp() - time.altzone  # time zone problem
                else:
                    ts = dt.timestamp() - time.timezone  # time zone problem
            except ValueError:
                dt = datetime.datetime.strptime(data['TimeStamp'], '%Y-%m-%dT%H:%M:%S')
                if time.daylight:
                    ts = dt.timestamp() - time.altzone  # time zone problem
                else:
                    ts = dt.timestamp() - time.timezone  # time zone problem
            except:
                self.timestramp = time.time()
            self.timestramp = time.time()