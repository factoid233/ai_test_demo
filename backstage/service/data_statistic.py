# -*- coding: utf-8 -*-
import importlib
from typing import Iterable

import pandas as pd

from backstage.config.common_config import complex_field


class DataStatistic:
    def __init__(self, df_actual, df_compare, testfunc, testfunc_type, expected_actual_mapping, **kwargs):
        self.df_actual = df_actual
        self.df_compare = df_compare
        self.kwargs = kwargs
        self._testfunc = testfunc
        self._testfunc_type = testfunc_type
        self._ea_mapping = expected_actual_mapping

    def normal_run(self):
        test_class = f"TestType{self._testfunc_type}"
        if test_class not in importlib.import_module('backstage.service.data_statistic').__dict__.keys():
            raise RuntimeError(f'data_statistic 不存在 {test_class} 类')
        _class = getattr(importlib.import_module('backstage.service.data_statistic'), test_class)(
            df_compare=self.df_compare, df_actual=self.df_actual, testfunc=self._testfunc,
            testfunc_type=self._testfunc_type, expected_actual_mapping=self._ea_mapping, **self.kwargs)
        _class.normal_run()


class TestTypeBase:
    def __init__(self, df_actual, df_compare, testfunc, testfunc_type, expected_actual_mapping, **kwargs):
        self.df_actual = df_actual
        self.df_compare: pd.DataFrame = df_compare
        self.kwargs = kwargs
        self._testfunc = testfunc
        self._testfunc_type = testfunc_type
        self._ea_mapping: dict = expected_actual_mapping

    def normal_run(self):
        pass

    @classmethod
    def calculate_pass(cls, datas: Iterable):
        _pass = _total = 0
        for item in datas:
            if item in ('skip', None):
                continue
            _total += 1
            if item is True:
                _pass += 1
        return _pass, _total


class TestType1(TestTypeBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def normal_run(self):
        if self._testfunc not in complex_field.keys():
            # 简单字段
            simple = self.simple_field()
        else:
            # 复杂字段
            pass
        return

    def simple_field(self):
        _statistic = {}
        for label, series in self.df_compare.items():
            if label not in self._ea_mapping.keys():
                continue
            if label not in _statistic:
                _pass, _total = self.calculate_pass(series.to_list())
                _statistic[label] = {"pass": _pass, "total": _total}
        return _statistic
