# -*- coding: utf-8 -*-
import datetime
import re
from typing import Dict, List

from pathlib import Path
import pandas as pd

from backstage.config.common_config import extra_keys, simple_translation_mapper
from backstage.utils.common import str_to_json, get_project_root_path


class DataStore:
    sheets = dict()

    def __init__(self, df_actual, df_expected, dict_compare_dfs, testfunc_type, data_statistic, **kwargs):
        self.df_actual: pd.DataFrame = df_actual
        self.df_expected = df_expected
        self.dict_compare_dfs = dict_compare_dfs
        self.testfunc_type = testfunc_type
        self.data_statistic = data_statistic
        self.kwargs = kwargs

    def normal_run(self):
        """
        根据测试类型进行区分
        :return:
        """

        self.sheet_data_statistic()
        if self.testfunc_type in (1,):
            self.test_type1()
        self.translation_words()
        self.sheet_error()
        self.export_excel()

    def test_type1(self):
        sheets: Dict[str, pd.DataFrame] = {}
        # 预期结果中提取出的额外key
        extra_keys_expected = set(self.df_expected.keys()) - set(self.dict_compare_dfs['simple'].keys())
        extra_keys_need = extra_keys & extra_keys_expected
        extra_keys_need = sorted(extra_keys_need)

        _dict_compare_dfs = self.dict_compare_dfs.copy()
        _simple_compare_df = _dict_compare_dfs.pop('simple')
        sheets['通用详情'] = self.test_type1_simple(extra_keys_need, _simple_compare_df)
        if _dict_compare_dfs:
            res = self.test_type1_complex(extra_keys_need, _dict_compare_dfs)
            sheets.update(res)
        self.sheets.update(sheets)
        return

    def test_type1_simple(self, extra_keys_need, _df_compare):
        # 一个字段名称 一个空格
        joint_key_blank = ",,".join(_df_compare.keys()).split(',') + ['']
        table_head = [*extra_keys_need, *joint_key_blank]
        table_content = []
        for index, series in _df_compare.iterrows():
            extra_values = [self.df_expected.loc[index, item] for item in extra_keys_need]
            row_exp = extra_values
            row_act = ['' for _ in extra_values]
            for key in series.keys():
                cell_exp = self.df_expected.loc[index, key]
                cell_compare = series[key]
                cell_act = self.df_actual.loc[index, key]
                row_exp.extend([cell_exp, cell_compare])
                row_act.extend([cell_act, ''])
            table_content.extend([row_exp, row_act])
        df = pd.DataFrame(data=table_content, columns=table_head)
        return df

    def test_type1_complex(self, extra_keys_need, dict_compare_df: Dict[str, pd.DataFrame]):
        sheets = {}
        for sheet_name, df in dict_compare_df.items():
            # 定制表头
            custom_head_keys = list(df.keys())
            custom_head_keys.remove('index_main')
            joint_key_blank = ",,".join(custom_head_keys).split(',') + ['']
            table_head = [*extra_keys_need, *joint_key_blank]
            table_content = []
            # 取出需展示的预期、实际结果列
            sheet_expected: pd.Series = self.df_expected[sheet_name]
            sheet_actual: pd.Series = self.df_actual[sheet_name]
            # 将列按照compare的原始索引分组
            grouped = df.groupby('index_main')
            for index_main, df1 in grouped:
                # 提取预期结果和实际结果的cell，提取结果为列表
                # 预期结果需要json反序列化
                sheet_expected_row_src = sheet_expected.loc[index_main]
                sheet_expected_row_is_json = str_to_json(sheet_expected_row_src)
                sheet_expected_rows: List[
                    dict] = sheet_expected_row_is_json if sheet_expected_row_is_json is not False else []
                sheet_actual_rows: List[dict] = sheet_actual.loc[index_main]
                # 重置索引 与预期结果中的数组匹配
                df1.reset_index(drop=True, inplace=True)
                # 去掉 index_main列不展示
                df1.drop(columns=['index_main'], inplace=True)
                extra_values = [self.df_expected.loc[index_main, item] for item in extra_keys_need]
                # 遍历表格中的每一行
                for index, series_compare in df1.iterrows():
                    row_expect = extra_values.copy()
                    row_actual = ['' for _ in extra_values]
                    sheet_expected_row = sheet_expected_rows[index] if index < len(sheet_expected_rows) else {}
                    sheet_actual_row = sheet_actual_rows[index] if index < len(sheet_actual_rows) else {}
                    # 遍历行中的每个key
                    for key in series_compare.keys():
                        cell_expect = sheet_expected_row.get(key)
                        cell_actual = sheet_actual_row.get(key)
                        cell_compare = series_compare[key]
                        row_expect.extend([cell_expect, cell_compare])
                        row_actual.extend([cell_actual, ''])
                    table_content.extend([row_expect, row_actual])
            _df = pd.DataFrame(table_content, columns=table_head)
            sheets[sheet_name] = _df
        return sheets

    def sheet_data_statistic(self):
        data = self.data_statistic
        data_complex: dict = dict(filter(lambda x: isinstance(x[1], dict), data.items()))
        data_simple: dict = dict(filter(lambda x: isinstance(x[1], (str, float)), data.items()))
        data_complex1: list = self.sheet_data_statistic_complex(data_complex)
        data_simple1 = self.sheet_data_statistic_simple(data_simple)
        data_final = data_simple1 + data_complex1
        df = pd.DataFrame(data_final)
        df_columns_mapper = {item: ''for item in df.keys()}
        df.rename(columns=df_columns_mapper,inplace=True)
        self.sheets['统计'] = df
        return

    def sheet_data_statistic_complex(self, data: Dict[str, dict]):
        """
        处理精度详情统计
        :param data:
        :return:
        """
        _list = []
        for key1, value1 in data.items():
            _list.extend(['', ''])
            df = pd.DataFrame(value1).T
            # 翻译成中文
            index_src = df.index
            index_mapper = self.sheet_data_statistic_complex_translate(index_src)
            df.rename(index_mapper, inplace=True)

            data1 = df.to_dict('split')
            columns = ['字段名称'] + data1['columns']
            _list.extend([[key1], columns])
            for index, value2 in zip(data1['index'], data1['data']):
                row = [index] + value2
                _list.append(row)
        return _list

    def sheet_data_statistic_complex_translate(self, data):
        index_mapper = {}
        translation_mapping = self.kwargs.get('translation_mapping')
        for item in translation_mapping.keys():
            if item in data:
                index_mapper[item] = translation_mapping[item]
            else:
                for value1 in data.copy():
                    if item in value1:
                        index_mapper[value1] = value1.replace(item, translation_mapping[item])
        return index_mapper

    @classmethod
    def sheet_data_statistic_simple(cls, data: dict):
        _list = []
        for key, value in data.items():
            if key in simple_translation_mapper.keys():
                name = simple_translation_mapper[key]
            else:
                name = key
            _list.append([name, value])
        return _list

    def sheet_error(self):
        if 'error' in self.df_actual.keys():
            df = self.df_actual.dropna(subset=['error']).dropna(how='all', axis=1)['error']
            need_extra_keys = set(extra_keys) & set(self.df_expected.keys())
            df_extra = self.df_expected.loc[df.index][need_extra_keys]
            df1 = pd.concat([df_extra, df], axis=1)
            self.sheets['异常数据'] = df1
        return None

    def generate_execl_path(self):
        testfunc = self.kwargs.get('testfunc')
        name = "%s_%s.xlsx" % (testfunc, datetime.datetime.today().strftime('%Y%m%d-%H%M%S'))
        excel_path_dir = Path(get_project_root_path()) / 'output' / testfunc
        excel_path = excel_path_dir / name
        if not excel_path_dir.exists():
            excel_path_dir.mkdir(parents=True)
        return excel_path

    def translation_words(self):
        translation_mapping = self.kwargs.get('translation_mapping')
        if translation_mapping is None:
            return
        for sheet_name in self.sheets.copy().keys():
            sheet: pd.DataFrame = self.sheets[sheet_name]
            table_src_names = sheet.keys()
            table_names = {item: translation_mapping[item] for item in table_src_names if
                           item in translation_mapping.keys()}
            sheet.rename(columns=table_names, inplace=True)

            # 翻译sheet名字
            if sheet_name in translation_mapping.keys():
                dest_sheet_name = translation_mapping[sheet_name]

                self.sheets[dest_sheet_name] = self.sheets.pop(sheet_name)

    def export_excel(self):
        excel_path = str(self.generate_execl_path())
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            for name, value in self.sheets.items():
                df = pd.DataFrame(value)
                if df.empty:
                    continue
                df.to_excel(writer, sheet_name=name, index=False)
        return excel_path
