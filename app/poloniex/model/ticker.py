import time

'''
newTickerData = {
    'last': args[1],
    'lowestAsk': args[2],
    'highestBid': args[3],
    'percentChange': args[4],
    'baseVolume': args[5],
    'quoteVolume': args[6],
    'isFrozen': args[7],
    'high24hr': args[8],
    'low24hr': args[9],
    'id': Array.markets['byCurrencyPair'][reserve(args[0])]['id']
}
'''

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
        self.change = float(data['percentChange']) * 100
        self.price = float(data['last'])
        self.base = base
        self.quote = quote
        self.volume = float(data['baseVolume'])
        self.timestramp = time.time()
