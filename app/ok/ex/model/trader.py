import time
class Trader:
    def __init__(self, rate=0.0, amount=0.0):
        self.rate = rate
        self.amount = amount
        self.total = rate * amount
        self.timestramp = time.time()
