# encoding:utf8
import backtrader as bt
from .algos import *
from loguru import logger
from engine.strategy.strategy_base import StrategyBase


class StratgeyAlgo(StrategyBase):
    def __init__(self, algos):
        self.algos = algos

    def next(self):
        context = {
            'strategy': self
        }
        run_algos(context, self.algos)
