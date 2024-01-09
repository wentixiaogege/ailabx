# encoding: utf8
from loguru import logger
import pandas as pd
import abc


class RunOnce:
    def __init__(self):
        self.done = False

    def __call__(self, context):
        done = self.done
        self.done = True
        return done


class RunPeriod:

    def __call__(self, target):
        # get last date
        now = target['strategy'].datetime.date(0)
        last_date = target['strategy'].datetime.date(-1)
        date_to_compare = last_date
        now = pd.Timestamp(now)
        date_to_compare = pd.Timestamp(date_to_compare)

        result = self.compare_dates(now, date_to_compare)

        return result

    @abc.abstractmethod
    def compare_dates(self, now, date_to_compare):
        raise (NotImplementedError("RunPeriod Algo is an abstract class!"))


# https://github.com/pmorissette/bt/blob/master/bt/algos.py
class RunQuarterly(RunPeriod):

    def compare_dates(self, now, date_to_compare):
        if now.quarter != date_to_compare.quarter:
            return False
        return True


class SelectAll:
    def __call__(self, context):
        stra = context['strategy']
        context['selected'] = list(stra.datas)
        return False



class WeightEqually:
    def __init__(self):
        pass

    def __call__(self, context):
        selected = context["selected"]
        stra = context['strategy']
        N = len(selected)
        if N > 0:
            weight = 1 / N
            for data in selected:
                stra.order_target_percent(data, weight)
        return False


class WeightFix:
    def __init__(self, weights):
        self.weights = weights

    def __call__(self, context):
        selected = context["selected"]
        stra = context['strategy']
        N = len(selected)
        if N != len(self.weights):
            logger.error('标的个数与权重个数不等')
            return True

        for data, w in zip(selected, self.weights):
            stra.order_target_percent(data, w)
        return False


def run_algos(context, algo_list):
    for algo in algo_list:
        if algo(context) is True:  # 如果algo返回True,直接不运行，本次不调仓
            return
