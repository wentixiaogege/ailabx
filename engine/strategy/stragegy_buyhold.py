# -*- coding: utf-8 -*-

import backtrader as bt
from engine.strategy.algos import *
from loguru import logger
from engine.strategy.strategy_base import StratgeyAlgoBase


class StratgeyBuyHold(StratgeyAlgoBase):
    def __init__(self, weights=None):
        self.algos = [
            RunOnce(),
            SelectAll(),
        ]

