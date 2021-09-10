# -*- coding: utf-8 -*-
import importlib
from typing import Iterable, Dict

import pandas as pd

from backstage.config.common_config import complex_field


class DataStatistic:
    """
    以测试类型分类，统计精度和耗时
    """
    statistic_data: dict = None

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
        _class: TestTypeBase = getattr(importlib.import_module('backstage.service.data_statistic'), test_class)(
            df_compare=self.df_compare, df_actual=self.df_actual, testfunc=self._testfunc,
            testfunc_type=self._testfunc_type, expected_actual_mapping=self._ea_mapping, **self.kwargs)
        _class.normal_run()
        self.statistic_data = _class.data


class TestTypeBase:
    data = None

    def __init__(self, df_actual, df_compare, testfunc, testfunc_type, expected_actual_mapping, **kwargs):
        self.df_actual = df_actual
        self.df_compare: Dict[str, pd.DataFrame] = df_compare
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
        results = {}
        result_accuracy: Dict[str, dict] = {}
        # 简单字段
        _dict_compare_dfs_copy = self.df_compare.copy()
        _simple_df = _dict_compare_dfs_copy.pop('simple')
        result_accuracy.update(self.simple_field(_simple_df))

        # 复杂字段
        if _dict_compare_dfs_copy:
            """不是空字典"""
            result_accuracy.update(self.complex_field(_dict_compare_dfs_copy))
        results['accuracy_detail'] = result_accuracy
        results['accuracy_weight_mean'] = self.accuracy_statistic(result_accuracy)
        results.update(self.latency_statistic())
        self.data = results
        return

    def simple_field(self, _simple_df):
        _statistic = {}
        for label, series in _simple_df.items():
            if label not in self._ea_mapping.keys():
                continue
            if label not in _statistic:
                _pass, _total = self.calculate_pass(series.to_list())
                _statistic[label] = {"pass": _pass, "total": _total}
        return _statistic

    def complex_field(self, _complex_dfs: Dict[str, pd.DataFrame]) -> Dict:
        _statistic = {}
        for complex_first, df in _complex_dfs.items():
            for label, series in df.items():
                if label == 'index_main':
                    continue
                _joint_key = f'{complex_first}_{label}'
                if _joint_key not in _statistic:
                    _pass, _total = self.calculate_pass(series.to_list())
                    _statistic[_joint_key] = {"pass": _pass, "total": _total}

        return _statistic

    @classmethod
    def format_percentage_accuracy(cls, data: float):
        res = '{0:>6.2f} %'.format(round(data * 100))
        return res

    @classmethod
    def accuracy_statistic(cls, data: dict):
        """
        加权取平均值
        :param data:
        :return:
        """
        all_sum = sum(i['total'] for i in data.values())
        _average = 0
        if all_sum == 0:
            return 0
        for key, _dict1 in data.items():
            if _dict1['total'] != 0:
                _average_item = _dict1['pass'] / _dict1['total']
                res = _average_item * (_dict1['total'] / all_sum)
                _average += res
                _dict1['mean'] = cls.format_percentage_accuracy(_average_item)
            else:
                _dict1['mean'] = cls.format_percentage_accuracy(0)
        _average = cls.format_percentage_accuracy(_average)
        return _average

    def latency_statistic(self):
        """
        平均耗时 小数点默认取3位
        :return:
        """
        results = {}
        _latency_series = self.df_actual['response_latency']
        results['latency_mean'] = round(_latency_series.mean(), 3)
        for item in (0.7, 0.9, 0.95, 0.99):
            key_name = f"latency_P{round(item * 100)}"
            result_item = self.average_latency_percentage(_latency_series, item)
            results[f'{key_name}'] = round(result_item, 3)
        return results

    @classmethod
    def average_latency_percentage(cls, data_src: pd.Series, percentage: float):
        data = data_src.dropna()
        data_sort = data.sort_values(ignore_index=True)
        place = int(data_sort.index.max() * percentage)
        result = data_sort.loc[place]
        return result
