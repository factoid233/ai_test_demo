# -*- coding: utf-8 -*-
import re
from itertools import zip_longest
from typing import Dict, List

import pandas as pd

from backstage.utils.common import str_to_json
from backstage.utils.compare_value import CompareValue
from backstage.service.get_common_data import GetCommonData


class CompareData:
    """
    以简单类型和复杂类型区分
    仅比较输出 df 值仅为 True False skip
    {'simple': df, 'complex_field1':'df1','complex_field2':'df2',....}
    """
    kwargs = None
    df_actual = None
    df_expect = None
    _ea_mapping = None
    dfs: Dict[str, pd.DataFrame] = None

    def __init__(self, df_actual, df_expect, testfunc, **kwargs):
        self.kwargs = kwargs
        self.df_actual: pd.DataFrame = df_actual
        self.df_expect: pd.DataFrame = df_expect
        self._ea_mapping: dict = kwargs.get('expected_actual_mapping')
        self.testfunc = testfunc

    @classmethod
    def compare_value(cls, data_act, data_exp):
        """

        :param data_act:
        :param data_exp:
        :return: True False 'skip':不计入统计
        """
        if data_exp in ('未知', '', None):
            return 'skip'
        if data_act in (None,):
            return False

        # 去掉预期结果中的空格再处理
        data_exp = data_exp.replace(' ', '') if isinstance(data_exp, str) else data_exp
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
        """
        预期结果和实际结果比较只有简单类型和复杂类型的两种区分
        :return:
        """
        _list_simple = []
        _dict_complex = {}
        for (index_act, series_act), (index_exp, series_exp) in zip_longest(self.df_actual.iterrows(),
                                                                            self.df_expect.iterrows(),
                                                                            fillvalue=(None, None)):
            _dict_simple = {'index': index_exp}
            for key in self._ea_mapping.keys():
                if not GetCommonData.is_complex_field(self.testfunc, key):
                    _dict_simple[key] = self.compare_value(data_act=series_act[key], data_exp=series_exp[key])
                else:
                    # 复杂字段
                    if key not in _dict_complex.keys():
                        _dict_complex[key] = []
                    res = self.complex_field_process(act=series_act[key], exp=series_exp[key], index_main=index_exp)
                    _dict_complex[key].extend(res)
            _list_simple.append(_dict_simple)
        df_simple = pd.DataFrame(_list_simple).set_index(['index'])
        for key in _dict_complex.copy().keys():
            _dict_complex[key] = pd.DataFrame(_dict_complex[key])
        self.dfs = {'simple': df_simple, **_dict_complex}
        return self

    def complex_field_process(self, act, exp, index_main) -> List[dict]:
        results = []
        complex_first_act = act
        # 暂时只处理预期结果反序列化json，不处理接口返回结果
        complex_first_exp2 = str_to_json(exp)
        complex_first_exp = [] if complex_first_exp2 is False else complex_first_exp2
        if not (isinstance(complex_first_act, list) and isinstance(complex_first_exp, list)):
            return results
        for act1, exp1 in zip_longest(complex_first_act, complex_first_exp, fillvalue={}):
            temp = dict(index_main=index_main)
            # 以预期结果的key为准
            for key, value in exp1.items():
                if key not in act1.keys():
                    temp[key] = False
                else:
                    temp[key] = self.compare_value(data_act=act1[key], data_exp=exp1[key])
            # 如果exp1为空，act1有值仅展示， 即 识别结果比人看出的结果多，多出的识别结果仅展示不统计
            if not exp1 and act1:
                for key, value in act1.items():
                    temp[key] = 'skip'
            results.append(temp)
        return results
