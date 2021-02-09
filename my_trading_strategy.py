# from __future__ import (absolute_import, division, print_function,
#                         unicode_literals)

from datetime import datetime  # For datetime objects
# import os.path  # To manage paths
# import sys  # To find out the script name (in argv[0])
import math
# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):

    params = dict(stop_loss_point=None, buy_count=0)

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.highest = 0
        self.lowest = 0
        self.setsizer(sizer())

    def next(self):
        # self.log('Stop Loss Point, %.3f' % self.params.stop_loss_point)
        target_buy_price = round(
            self.lowest * (1 + self.params.stop_loss_point * self.params.buy_count), 2)
        self.log('target_buy_price, %.2f' % target_buy_price)
        self.log('High, %.2f' % self.datahigh[0])
        self.log('Low, %.2f' % self.datalow[0])
        if(self.datahigh[0] >= target_buy_price):
            if(target_buy_price >= self.datalow[0]):
                self.log('BUY ' + ', Price: ' + str(target_buy_price))
                self.buy(price=target_buy_price)
            else:
                target_buy_price = self.dataopen[0]
                self.log('BUY ' + ', Price: ' + str(target_buy_price))
                self.buy(price=target_buy_price)
            self.params.buy_count += 1
        if(self.lowest == 0 or self.lowest > self.datalow[0]):
            self.lowest = self.datalow[0]
            self.params.buy_count = 1
            self.log('New Lowest Price: ' + str(self.lowest))
        self.log('Close, %.2f' % self.dataclose[0])


# 計算交易部位
class sizer(bt.Sizer):
    params = dict(unit=None)

    def _getsizing(self, comminfo, cash, data, isbuy):
        print(f'position: {self.broker.getposition(data).size}')
        print(f'cash: {cash}')
        print(f'comminfo: {comminfo.price}')
        if self.broker.getposition(data).size == 0:
            self.params.unit = cash/4
        if isbuy:
            if (cash > self.params.unit):
                return math.floor(self.params.unit/data[1])
            else:
                return math.floor(cash/data[1])
        else:
            return self.broker.getposition(data)


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(
        TestStrategy, stop_loss_point=0.15)

    # Create a Data Feed
    data = bt.feeds.YahooFinanceData(dataname='TSLA',
                                     fromdate=datetime(2021, 1, 1),
                                     todate=datetime(2021, 1, 7))

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()
    cerebro.plot()
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
