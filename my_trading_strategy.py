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

    params = dict(stop_loss_point=0.15, buy_count=0, sell_count=0, unit=0)

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
        # self.order = None

    # def notify_order(self, order):
    #     if order.status in [order.Submitted, order.Accepted]:
    #         # Buy/Sell order submitted/accepted to/by broker - Nothing to do
    #         return

    #     # Check if an order has been completed
    #     # Attention: broker could reject order if not enough cash
    #     if order.status in [order.Completed]:
    #         if order.isbuy():
    #             self.log(
    #                 'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
    #                 (order.executed.price,
    #                  order.executed.value,
    #                  order.executed.comm))

    #             self.buyprice = order.executed.price
    #             self.buycomm = order.executed.comm
    #         else:  # Sell
    #             self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
    #                      (order.executed.price,
    #                       order.executed.value,
    #                       order.executed.comm))

    #         self.bar_executed = len(self)

    #     elif order.status in [order.Canceled, order.Margin, order.Rejected]:
    #         self.log('Order Canceled/Margin/Rejected')

    #     self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    # 計算買的股數
    def get_buy_size(self, price, position_size):
        if position_size == 0:
            self.params.unit = (self.broker.cash)/16
        if (self.broker.cash > self.params.unit):
            return math.floor(self.params.unit/price)
        else:
            return math.floor(self.broker.cash/price)

    def get_sell_size(self, price, position_size):
        if position_size > 0:
            if ((price * position_size) >= self.params.unit):
                return math.floor(self.params.unit/price)
            else:
                return math.floor((price * position_size)/price)
        else:
            return 0

    def custom_buy(self, price, exectype):
        self.log('BUY ' + ', Price: ' + str(price))
        buy_size = self.get_buy_size(price=price,
                                     position_size=self.broker.getposition(data).size)
        self.log('buy_size, %.2f' % buy_size)
        self.order = self.buy(size=buy_size, price=price, exectype=exectype)

    def custom_sell(self, price, exectype):
        self.log('SELL ' + ', Price: ' + str(price))
        sell_size = self.get_sell_size(price=price,
                                       position_size=self.broker.getposition(data).size)
        self.log('sell_size, %.2f' % sell_size)
        self.order = self.sell(size=sell_size, price=price, exectype=exectype)

    def next(self):
        target_buy_price = round(
            self.lowest * (1 + self.params.stop_loss_point * self.params.buy_count), 2)
        target_sell_price = round(
            self.highest * (1 - self.params.stop_loss_point * self.params.sell_count), 2)
        self.log('Current Position, %.2f' % self.broker.getposition(data).size)
        self.log('Cash, %.2f' % self.broker.cash)
        self.log('target_buy_price, %.2f' % target_buy_price)
        self.log('target_sell_price, %.2f' % target_sell_price)
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        # if self.order:
        #     return
        # 買
        if(self.datahigh[0] >= target_buy_price):
            if(target_buy_price >= self.datalow[0]):
                self.custom_buy(price=target_buy_price,
                                exectype=bt.Order.Limit)
            else:
                target_buy_price = self.dataopen[0]
                self.custom_buy(price=target_buy_price,
                                exectype=bt.Order.Limit)
            self.params.buy_count += 1
            self.params.sell_count = 1
        # 賣
        if(self.datalow[0] <= target_sell_price):
            if(target_sell_price <= self.datahigh[0]):
                self.custom_sell(price=target_buy_price,
                                 exectype=bt.Order.Limit)
            else:
                target_sell_price = self.dataopen[0]
                self.custom_sell(price=target_buy_price,
                                 exectype=bt.Order.Limit)
            self.params.sell_count += 1
            self.params.buy_count = 1
        if(self.lowest == 0 or (self.lowest > self.datalow[0])):
            self.lowest = self.datalow[0]
            self.log('New Lowest Price: ' + str(self.lowest))
        if(self.highest == 0 or (self.highest < self.datahigh[0])):
            self.highest = self.datahigh[0]
            self.log('New Highest Price: ' + str(self.highest))
        self.log('High, %.2f' % self.datahigh[0])
        self.log('Low, %.2f' % self.datalow[0])
        self.log('Open, %.2f' % self.dataopen[0])
        self.log('Close, %.2f' % self.dataclose[0])


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(
        TestStrategy, stop_loss_point=0.15)

    # Create a Data Feed
    data = bt.feeds.YahooFinanceData(dataname='TSLA',
                                     fromdate=datetime(2011, 1, 1),
                                     todate=datetime(2021, 2, 9))

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(10000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()
    cerebro.plot()
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
