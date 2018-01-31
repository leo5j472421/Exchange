import logging

class Traders:
    def __init__(self):
        self.asks = {}
        self.bids = {}
        self.lastAsksLow = 0
        self.lastBidsHigh = 0
        self.total = [0.0,0.0]

    def formate(self,traders,name) :
        for side in traders:
            if side == 'asks':
                for trade in traders['asks']:
                    if trade.amount == 0.0: # remove
                        if str(trade.rate) in self.asks:
                          self.total[0] -= self.asks[str(trade.rate)].amount
                          self.asks.pop(str(trade.rate))
                        else :
                            logging.warning( '{} is not in {}\'s order book list '.format(str(trade.rate),name))
                    elif str(trade.rate) in self.asks : # modify
                        self.total[0] -= self.asks[str(trade.rate)].amount
                        self.total[0] += trade.amount
                        self.asks.update({str(trade.rate):trade})
                    else: # insert
                        self.total[0] += trade.amount
                        self.asks.update({str(trade.rate):trade})
            elif side == 'bids':
                for trade in traders['bids']:
                    if trade.amount == 0.0: # remove
                        if str(trade.rate) in self.bids:
                          self.total[1] -= self.bids[str(trade.rate)].total
                          self.bids.pop(str(trade.rate))
                        else :
                            logging.warning( '{} is not in {}\'s order book list '.format(str(trade.rate),name))
                    elif str(trade.rate) in self.bids : # modify
                        self.total[1] -= self.bids[str(trade.rate)].total
                        self.total[1] += trade.total
                        self.bids.update({str(trade.rate):trade})
                    else: # insert
                        self.total[1] += trade.total
                        self.bids.update({str(trade.rate):trade})