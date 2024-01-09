import backtrader as bt
from .algos import *
from loguru import logger


class StrategyPickTime(bt.Strategy):
    params = (
        ('ema_period', 200),
        ('rsi_period', 8),
        ('atr_period', 14),
        ('adx_period', 14),
    )

    def __init__(self):
        #bt.ind.EMA(self.data, period=self.p.ema_period)
        self.ema = bt.ind.EMA(period=self.p.ema_period)
        self.rsi = bt.ind.RSI(period=self.p.rsi_period)
        self.atr = bt.ind.ATR(period=self.p.atr_period)
        self.adx = bt.talib.ADX(self.data.high, self.data.low, self.data.close, timeperiod=self.p.adx_period)

    def next(self):
        if self.getposition().size == 0: #Î´³Ö²Ö
            if self.data[0] > self.ema[0] and self.adx[0] > 50 and self.rsi[0] < 20:
                pass
