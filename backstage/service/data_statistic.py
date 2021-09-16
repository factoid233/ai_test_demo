# -*- coding: utf-8 -*-
import importlib
from typing import Iterable, Dict

import pandas as pd

from backstage.dao.def_type import DefTypeHandler
from backstage.utils.compare_value import CompareValue


class DataStatistic:
    """
    以测试类型分类，统计精度和耗时
    """
    statistic_data: dict = {}

    def __init__(self, df_actual, df_compare, testfunc, testfunc_type, expected_actual_mapping, **kwargs):
        self.df_actual = df_actual
        self.df_compare = df_compare
        self.kwargs = kwargs
        self._testfunc = testfunc
        self._testfunc_type = testfunc_type
        self._ea_mapping = expected_actual_mapping

    def normal_run(self):
        self.common_info_show()
        test_class = f"TestType{self._testfunc_type}"
        if test_class not in importlib.import_module('backstage.service.data_statistic').__dict__.keys():
            raise RuntimeError(f'data_statistic 不存在 {test_class} 类')
        _class: TestTypeBase = getattr(importlib.import_module('backstage.service.data_statistic'), test_class)(
            df_compare=self.df_compare, df_actual=self.df_actual, testfunc=self._testfunc,
            testfunc_type=self._testfunc_type, expected_actual_mapping=self._ea_mapping, **self.kwargs)
        _class.normal_run()
        self.statistic_data.update(_class.data)
        latency_statistic = _class.latency_statistic()
        self.statistic_data.update(latency_statistic)

    def common_info_show(self):
        self.statistic_data['env_url'] = "%s[%s]" % (self.kwargs.get('env_alias'), self.kwargs.get('env_url'))
        if 'level' in self.kwargs.keys():
            self.statistic_data['困难程度'] = str(self.kwargs.get('level'))
        return


class TestTypeBase:
    data = None

    def __init__(self, df_actual, df_compare, testfunc, testfunc_type, expected_actual_mapping, **kwargs):
        self.df_actual = df_actual
        self.df_compare: Dict[str, pd.DataFrame] = df_compare
        self.df_expect = kwargs.get('df_expect')
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
        # results.update(self.latency_statistic())
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


class TestType4(TestTypeBase):
    """
    AI分类相关的，例如：图片分类、车辆视角、图片中是否有车
    混合矩阵 计算 accuracy，precision，recall
    """
    classify_mapping = None
    classify_field = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = self.kwargs.get('session')

    def normal_run(self):
        results = {}
        self.get_need_data_from_db()
        accuracy_detail = self.accuracy_detail()
        results['accuracy_detail'] = accuracy_detail
        results['accuracy_weight_mean'] = self.accuracy_weight_mean(accuracy_detail)
        self.data = results

    def get_need_data_from_db(self):
        def_type_handler = DefTypeHandler(session=self.session)
        self.classify_mapping = def_type_handler.get_classify_mapping(self._testfunc)
        self.classify_field = def_type_handler.get_classify_field(self._testfunc)

    def accuracy_detail(self):
        classify_mapping = self.classify_mapping
        _mapping = {CompareValue.str_to_num(key): value for key, value in classify_mapping.items()}
        result_count = {i: dict(TP=0, FP=0, TN=0, FN=0, accuracy=0, precision=0, recall=0, F1=0) for i in _mapping}
        series_compare = self.df_compare['simple'][self.classify_field]
        for type_one in _mapping:
            for index, cell in series_compare.items():
                act = self.df_actual.loc[index, self.classify_field]
                exp = self.df_expect.loc[index, self.classify_field]
                act = CompareValue.str_to_num(act)
                exp = CompareValue.str_to_num(exp)
                res = cell
                if res not in (True, False):
                    continue
                if exp == type_one:
                    """"正例"""
                    if res is True:
                        result_count[type_one]['TP'] += 1
                    else:
                        result_count[type_one]['FN'] += 1

                else:
                    """负例"""
                    if act == type_one:
                        result_count[type_one]['FP'] += 1
                    else:
                        result_count[type_one]['TN'] += 1
            TP = result_count[type_one]['TP']
            TN = result_count[type_one]['TN']
            FP = result_count[type_one]['FP']
            FN = result_count[type_one]['FN']
            p = round(TP / (TP + FP), 4) if TP + FP else 0
            r = round(TP / (TP + FN), 4) if TP + FN else 0
            a = round((TP + TN) / (TP + TN + FP + FN), 4) if TP + TN + FP + FN else 0
            f1 = round(2 * p * r / (r + p), 4) if r + p else 0
            result_count[type_one]['accuracy'] = a
            result_count[type_one]['precision'] = p
            result_count[type_one]['recall'] = r
            result_count[type_one]['F1'] = f1

        return result_count

    def accuracy_weight_mean(self, accuracy_detail: Dict[str, dict]):
        df = self.df_expect.copy()
        df['flag'] = True
        df1 = df.groupby(self.classify_field).count()
        total = df['flag'].sum()
        res = 0
        for _type, _dict in accuracy_detail.items():
            weight = _dict['F1'] * df1.loc[_type, 'flag'] / total
            res += weight
        res_round = round(res, 4)
        return res_round
