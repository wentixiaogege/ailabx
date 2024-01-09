import pandas as pd


def load_data(name):
    df = pd.read_csv('../data/csv/{}.csv'.format(name))
    df['date'] = df['date'].apply(lambda x: str(x))
    df.set_index('date', inplace=True)
    df.sort_index(ascending=True, inplace=True)
    df.dropna(inplace=True)
    return df


df = load_data('000300.SH')
df_spx = load_data('spx')


def to_backtrader_dataframe(df):
    df.index = pd.to_datetime(df.index)
    df['openinterest'] = 0
    if 'amount' not in df.columns:
        df['amount'] = 0
    df = df[['open', 'high', 'low', 'close', 'volume','amount', 'openinterest']]
    return df


df = to_backtrader_dataframe(df)
df = df[df.index > '20110708']
df_spx = to_backtrader_dataframe(df=df_spx)
#print(df[['close']])
#print(df_spx[['close']])
import backtrader as bt  # 导入 Backtrader

class PandasData_more(bt.feeds.PandasData):
    lines = ('amount', ) # 要添加的线
    # 设置 line 在数据源上的列位置
    params=(
        ('amount', -1),
           )
    # -1表示自动按列明匹配数据，也可以设置为线在数据源中列的位置索引 (('pe',6),('pb',7),)


# 实例化 cerebro
cerebro = bt.Cerebro()
from datetime import datetime

start = datetime(2011, 7, 8)
end = datetime.now().date()
data = PandasData_more(dataname=df, name='000300', fromdate=start, todate=end)
cerebro.adddata(data)  # Add the data feed
cerebro.adddata(PandasData_more(dataname=df_spx, name='spx', fromdate=start, todate=end))
# print(df)
cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='pnl')  # 返回收益率时序数据
cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='_AnnualReturn')  # 年化收益率
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='_SharpeRatio')  # 夏普比率
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='_DrawDown')  # 回撤


# 通过继承 Strategy 基类，来构建自己的交易策略子类
class MyStrategy(bt.Strategy):
    # 定义我们自己写的这个 MyStrategy 类的专有属性
    def __init__(self):
        '''必选，策略中各类指标的批量计算或是批量生成交易信号都可以写在这里'''
        print(self.datas)
        print(self.data0)
        print(self.data1)
        print(self.datas[0])
        print(self.getdatabyname('spx'))
        print('line aliases', self.data0.getlinealiases())
        # print('lines', len(self.data0.lines),self.data0.lines[0])
        # print('data0.lines.open', len(self.data0.lines), self.data0.open)
        # print('data0.lines.close', self.data0[-1], self.data0.close[-1])
        # print('data0.lines.datetime', self.data0.datetime)
        self.i = 0

    # 构建交易函数: 策略交易的主体部分
    def next(self):
        if self.i == 0:
            self.i += 1
            print('line的长度', self.data0.buflen(), self.data1.buflen())
            print('添加的列amount', self.data0.amount[0])
            print(self.datas[0]._name)
            print('datetime的使用', self.data0.datetime[0], bt.num2date(self.data0.datetime[0]).date(),
                  self.data0.datetime.date(0), self.data0.datetime.date(1))
            print(self.data1.close[1], self.data1.datetime.date(-5), self.data1.lines.datetime.date(0))
            print('next===>data0.lines.close', self.data.datetime.date(0), self.datas[0].close[0], self.data[-1],
                  self.data[-2])
            print('get====>data0.lines.close', self.data0.datetime.date(0), self.data0.get(ago=0, size=2))

        # self.buy()
        pass
        '''必选，在这里根据交易信号进行买卖下单操作'''
        # print(self.data.close[0])


cerebro.addstrategy(MyStrategy)
results = cerebro.run()

strat = results[0]
# 返回日度收益率序列
daily_return = pd.Series(strat.analyzers.pnl.get_analysis())
# 打印评价指标
print("--------------- AnnualReturn -----------------")
print(strat.analyzers._AnnualReturn.get_analysis())
print("--------------- SharpeRatio -----------------")
print(strat.analyzers._SharpeRatio.get_analysis())
print("--------------- DrawDown -----------------")
print(strat.analyzers._DrawDown.get_analysis())
