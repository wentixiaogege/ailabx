# encoding:utf8
from datetime import datetime
import backtrader as bt
import numpy as np
import pandas as pd
import pyfolio
from loguru import logger
from scipy.stats import linregress
from engine.datafeed.datafeed_csv import feed
from engine.datafeed.datafeed_arctic import ArcticDataFeed


def momentum_func(self, price_array):
    r = np.log(price_array)
    slope, _, rvalue, _, _ = linregress(np.arange(len(r)), r)
    annualized = (1 + slope) ** 252
    return (annualized * (rvalue ** 2))


# 定义动量指标
class Momentum(bt.ind.OperationN):
    lines = ('trend',)
    params = dict(period=90)
    func = momentum_func


class DummyInd(bt.Indicator):
    lines = ('dummyline',)

    params = (('value', 5),)

    def __init__(self):
        self.lines.dummyline = bt.Max(0.0, self.params.value)


# https://zhuanlan.zhihu.com/p/321149887?ivk_sa=1024320u
class BacktraderEngine:
    def __init__(self, init_cash=1000000.0, benchmark='000300.SH', start=datetime(2010, 1, 1), end=datetime.now().date()):
        self.init_cash = init_cash
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(init_cash)
        self.benchmark = benchmark
        #cerebro.broker.setcommission(0.0001)
        # 滑点：双边各 0.0001
        #cerebro.broker.set_slippage_perc(perc=0.0001)

        self.cerebro = cerebro

        self._init_analyzers()

        self.feed = feed
        self.arctic = ArcticDataFeed()

        self.start = start
        self.end = end

    def _init_analyzers(self):
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='_Returns')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='_TradeAnalyzer')
        self.cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='_AnnualReturn')
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.0, annualize=True, _name='_SharpeRatio')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='_DrawDown')
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, _name='_PyFolio')

    def add_arctic_data(self, code):
        df = self.arctic.get_df(code)
        self.add_data(code, df)

    def add_csv_data(self, code):
        self.feed.add_data(code, DATA_DIR_CSV.joinpath('{}.csv'.format(code)))
        df = self.feed.get_df(code)
        self.add_data(code, df)

    def add_data(self, code, df):
        # 加载数据
        df = to_backtrader_dataframe(df)
        data = bt.feeds.PandasData(dataname=df, name=code, fromdate=self.start, todate=self.end)

        self.cerebro.adddata(data)
        self.cerebro.addobserver(bt.observers.Benchmark,
                                 data=data)
        self.cerebro.addobserver(bt.observers.TimeReturn)

    def run(self):
        self.results = self.cerebro.run()

    def show_result(self):
        portfolio_value = self.cerebro.broker.get_value()
        accu_return = portfolio_value / self.init_cash - 1
        logger.info('累计收益率：{}'.format(accu_return))
        # logger.info('年化收益率：', accu_return)

    # 打印结果
    def _format_result(self, result):
        analyzer = {}
        # 返回参数
        # analyzer['period1'] = result.params.period1
        # analyzer['period2'] = result.params.period2
        # 提取年化收益
        analyzer['年化收益率'] = result.analyzers._Returns.get_analysis()['rnorm']
        # analyzer['年化收益率（%）'] = result.analyzers._Returns.get_analysis()['rnorm100']
        # 提取最大回撤(习惯用负的做大回撤，所以加了负号)
        analyzer['最大回撤（%）'] = round(result.analyzers._DrawDown.get_analysis()['max']['drawdown'] * (-1) / 100.0, 2)
        # 提取夏普比率
        try:
            analyzer['年化夏普比率'] = round(result.analyzers._SharpeRatio.get_analysis()['sharperatio'], 2)
        except:
            pass
        return analyzer

    def _bt_plot(self):
        self.cerebro.plot()

    def _bokeh_plot(self):
        from backtrader_plotting import Bokeh
        from backtrader_plotting.schemes import Tradimo
        plotconfig = {
            'id:ind#0': dict(
                subplot=True,
            ),
        }
        b = Bokeh(style='line', scheme=Tradimo(), plotconfig=plotconfig)
        self.cerebro.plot(b)

    def _plot_pyfolio(self, quantstats=False):
        portfolio_stats = self.results[0].analyzers.getbyname('_PyFolio')
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)

        self.show_result_empyrical(returns)
        #self.cerebro.plot(volume=False)

        df = self.feed.get_df(self.benchmark)
        df = df[['rate']]
        df.index = pd.to_datetime(df.index)
        # print(df)

        # all = pd.concat([df,returns], axis=1)
        # all.dropna(inplace=True)
        # print(all)
        #pyfolio.create_simple_tear_sheet(returns)
        #import matplotlib.pyplot as plt
        #plt.show()



        if quantstats:
            logger.info('quantstats...')
            import quantstats

            quantstats.reports.html(returns, benchmark=df, download_filename='stats.html', output='stats.html',
                                    title='AI量化平台')

    def show_result_empyrical(self, returns):
        import empyrical

        print('累计收益：', empyrical.cum_returns_final(returns))
        print('年化收益：', empyrical.annual_return(returns))
        print('最大回撤：', empyrical.max_drawdown(returns))
        print('夏普比', empyrical.sharpe_ratio(returns))
        print('卡玛比', empyrical.calmar_ratio(returns))
        print('omega', empyrical.omega_ratio(returns))

    def analysis(self):
        # 自行计算风险、收益特征

        #self.show_result_empyrical()
        #self.cerebro.plot(volume=False)

        #results = self.results
        #for result in results:
        #    ratios = self._format_result(result)
        #    print(ratios)

        self._plot_pyfolio(quantstats=True)
        # self._bt_plot()

        '''
        
       
        portvalue = self.cerebro.broker.getvalue()
        pnl = portvalue - self.init_cash
        # 打印结果
        print(f'总资金: {round(portvalue, 2)}')
        print('收益', pnl)
        accu_return = portvalue / self.init_cash - 1
        logger.info('总收益率:{}'.format(accu_return))

        annu_ret = round((accu_return + 1) ** (252 / (12 * 252 + 252 * 3 / 4)) - 1, 3)
        logger.info('年化收益:{}'.format(annu_ret))

        strats = [x for x in self.results]  # 取得两个策略的运行结果

        for ret in strats:
            print("--------------- AnnualReturn -----------------")
            print(ret.analyzers.AnnualReturn.get_analysis())
            print("--------------- SharpeRatio -----------------")
            print(ret.analyzers.SharpeRatio.get_analysis())
            print("--------------- DrawDown -----------------")
            print(ret.analyzers.DrawDown.get_analysis())

            # tdata_analyzer = ret.analyzers.getbyname('datareturns')
            # print(tdata_analyzer.get_analysis())
        
        # self.cerebro.plot(volume=False)
    '''


from engine.config import DATA_DIR_CSV
from engine.data_utils import to_backtrader_dataframe

from engine.strategy.strategy_rotation import StrategyRotation
from engine.strategy.stragegy_buyhold import StratgeyBuyHold
from engine.strategy.strategy_picktime import StrategyPickTime


# 策略选择类
class StFetcher(object):
    _STRATS = [StratgeyBuyHold, StrategyRotation]  # 注册策略

    def __new__(cls, *args, **kwargs):
        idx = kwargs.pop('idx')  # 策略索引

        obj = cls._STRATS[idx](*args, **kwargs)
        return obj


if __name__ == '__main__':
    from engine.datafeed.datafeed_csv import CSVDatafeed

    e = BacktraderEngine()

    # e.add_data('SPX')
    e.add_data('000300.SH')
    # e.add_data('399006.SZ')
    # e.add_data('SPX')
    # e.add_data('N225')

    # e.cerebro.optstrategy(StFetcher, idx=[0, 1])

    from engine.indicator.signal_double_sma import SignalDoubleSMA
    from engine.indicator.signal_triple_sma import SignalTripleSMA
    from engine.strategy.strategy_turtle import TurtleTradingStrategy
    from engine.strategy.stragegy_buyhold import StratgeyBuyHold

    # 每次固定交易100股
    # e.cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    # e.cerebro.add_signal(bt.SIGNAL_LONG, SignalTripleSMA)

    e.cerebro.addstrategy(StratgeyBuyHold)
    e.run()
    e.analysis()
