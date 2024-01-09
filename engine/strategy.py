import backtrader as bt


class StrategyBase(bt.Strategy):
    def log(self, txt, dt=None):
        '''�������Դ�ӡ��־�ĺ����������ڴ�ӡ������¼���׼�¼��'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        def notify_order(self, order):
            # δ������Ķ���
            if order.status in [order.Submitted, order.Accepted]:
                return
            # �Ѿ�����Ķ���
            if order.status in [order.Completed, order.Canceled, order.Margin]:
                if order.isbuy():
                    self.log(
                        'BUY EXECUTED, ref:%.0f��Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f, Stock: %s' %
                        (order.ref,  # �������
                         order.executed.price,  # �ɽ���
                         order.executed.value,  # �ɽ���
                         order.executed.comm,  # Ӷ��
                         order.executed.size,  # �ɽ���
                         order.data._name))  # ��Ʊ����
                else:  # Sell
                    self.log('SELL EXECUTED, ref:%.0f, Price: %.2f, Cost: %.2f, Comm %.2f, Size: %.2f, Stock: %s' %
                             (order.ref,
                              order.executed.price,
                              order.executed.value,
                              order.executed.comm,
                              order.executed.size,
                              order.data._name))
