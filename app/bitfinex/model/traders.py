class Traders:
    def __init__(self):
        self.asks = {}
        self.bids = {}
        self.lastAsksLow = 0
        self.lastBidsHigh = 0
        self.total = [0.0,0.0]