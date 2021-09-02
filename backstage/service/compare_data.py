# -*- coding: utf-8 -*-
from itertools import zip_longest

import pandas as pd

from backstage.utils.compare_value import CompareValue


class CompareData:
    kwargs = None
    df_actual = None
    df_expect = None
    _ea_mapping = None
    df = None

    def __init__(self, df_actual, df_expect, **kwargs):
        self.kwargs = kwargs
        self.df_actual: pd.DataFrame = df_actual
        self.df_expect: pd.DataFrame = df_expect
        self._ea_mapping: dict = kwargs.get('expected_actual_mapping')

    @classmethod
    def compare_value(cls, data_act, data_exp):
        """

        :param data_act:
        :param data_exp:
        :return: True False 'skip':不计入统计
        """
        if data_exp in ('未知', '', None):
            return 'skip'
        data1_type = CompareValue.is_num_str(data_act)
        data2_type = CompareValue.is_num_str(data_exp)
        if data1_type == 'num' and data2_type == 'num':
            data_act = CompareValue.str_to_num(data_act)
            data_exp = CompareValue.str_to_num(data_exp)
            return CompareValue.compare_num(data_act, data_exp)
        elif data1_type == 'str' and data2_type == 'num':
            return False
        elif data1_type == 'num' and data2_type == 'str':
            return False
        elif data1_type == 'str' and data2_type == 'str':
            return CompareValue.compare_str(data_act, data_exp)
        else:
            raise RuntimeError(f'暂不支持比较{data_act} {data_exp}')

    def normal_run(self):
        testfunc_type = self.kwargs.get('testfunc_type')
        if testfunc_type is None:
            raise RuntimeError('testfunc_type 获取异常')
        if testfunc_type in (1,):
            self.testfunc_type1()
        else:
            raise RuntimeError(f'无此该类型 testfunc_type{testfunc_type} 比较方法')

    def testfunc_type1(self):
        _list = []
        for (index_act, series_act), (index_exp, series_exp) in zip_longest(self.df_actual.iterrows(),
                                                                            self.df_expect.iterrows(),
                                                                            fillvalue=(None, None)):
            _dict = {}
            for key in self._ea_mapping.keys():
                _dict[key] = self.compare_value(data_act=series_act[key], data_exp=series_exp[key])
            _list.append(_dict)
        self.df = pd.DataFrame(_list)
        return
