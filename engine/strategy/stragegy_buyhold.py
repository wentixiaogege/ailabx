# encoding:utf8
import backtrader as bt
from .algos import *
from loguru import logger
from engine.strategy.strategy_base import StrategyBase


class StratgeyBuyHold(StrategyBase):
    def __init__(self, weights=None):
        self.algos = [
            RunOnce(),
            SelectAll(),
        ]

        if weights:
            self.algos.append(WeightFix(weights))
        else:
            self.algos.append(WeightEqually())

    def next(self):
        context = {
            'strategy': self
        }
        run_algos(context, self.algos)
