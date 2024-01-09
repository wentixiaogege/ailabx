import backtrader as bt


class StrategyBase(bt.Strategy):
    def log(self, txt, dt=None):
        '''构建策略打印日志的函数：可用于打印订单记录或交易记录等'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        def notify_order(self, order):
            # 未被处理的订单
            if order.status in [order.Submitted, order.Accepted]:
                return
            # 已经处理的订单
            if order.status in [order.Completed, order.Canceled, order.Margin]:
                if order.isbuy():
                    self.log(
                        'BUY EXECUTED, ref:%.0f，Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f, Stock: %s' %
                        (order.ref,  # 订单编号
                         order.executed.price,  # 成交价
                         order.executed.value,  # 成交额
                         order.executed.comm,  # 佣金
                         order.executed.size,  # 成交量
                         order.data._name))  # 股票名称
                else:  # Sell
                    self.log('SELL EXECUTED, ref:%.0f, Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f, Stock: %s' %
                             (order.ref,
                              order.executed.price,
                              order.executed.value,
                              order.executed.comm,
                              order.executed.size,
                              order.data._name))
