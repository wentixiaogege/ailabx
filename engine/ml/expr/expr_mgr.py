import re
from .ops import Operators, register_all_ops
from .base import Feature


class ExprMgr:
    @classmethod
    def init(cls):
        register_all_ops()

    @staticmethod
    def parse_field(field):
        # Following patterns will be matched:
        # - $close -> Feature("close")
        # - $close5 -> Feature("close5")
        # - $open+$close -> Feature("open")+Feature("close")
        if not isinstance(field, str):
            field = str(field)

        re_func = re.sub(r"(\w+\s*)\(", r"Operators.\1(", field)
        # print('re_runc',re_func)
        return re.sub(r"\$(\w+)", r'Feature("\1")', re_func)

    @staticmethod
    def get_expression(feature):
        feature = ExprMgr.parse_field(feature)
        try:
            expr = eval(feature)
        except:
            print('error', feature)
            raise
        return expr
