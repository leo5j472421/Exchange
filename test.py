from app.poloniex.polonixeApi import PoloniexApi
import datetime
import matplotlib.pyplot as plt
import numpy as np
from sklearn import linear_model

a = PoloniexApi()
data = a.returnMarketTradeHistory('USDT_ETH')
print(data)
b = []
for d in data:
    b.append([d['rate'],datetime.datetime.strptime( d['date'],'%Y-%m-%d %H:%M:%S') ] )
xd = [a[1]for a in b ]
y = [float(a[0]) for a in b ]
xa = [d.timestamp() for d in xd]
x = [[d.timestamp()] for d in xd]
print(x)
regr = linear_model.LinearRegression()
regr.fit(x ,y )
print('Coefficients: \n', regr.coef_)

#plt.plot(xa,regr.coef_ * xa + regr.intercept_)
plt.plot(xd,y)
# beautify the x-labels

plt.gcf().autofmt_xdate()

plt.show()

