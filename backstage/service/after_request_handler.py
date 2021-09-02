# -*- coding: utf-8 -*-
import time

import orjson
import pandas as pd

from backstage.config.common_config import encrypt_key, complex_field
from backstage.service.custom_handler import CustomAfterRequest
from backstage.utils.common import generate_uuid, str_to_json, get_class_functions, json_path
from backstage.utils.crypto_handler import Crypto


class AfterRequestHandler:
    df_expect: pd.DataFrame = None
    df_actual: pd.DataFrame = None
    kwargs = None
    _encrypt_key_mapping = None
    session = None
    testfunc = None

    def __init__(self, df_expect, df_actual, session, **kwargs):
        self.df_expect = df_expect
        self.df_actual = df_actual
        self.kwargs = kwargs
        self.testfunc = kwargs.get('testfunc')
        self._encrypt_key_mapping = encrypt_key
        self.session = session

    def normal_run(self):
        self.custom_process()
        self.expected_data_process()
        self.actual_data_process()

    def expected_data_process(self):
        self.decrypt_data()

    def actual_data_process(self):
        self.split_datas()

    def decrypt_data(self):
        """解密部分敏感字段"""
        df = self.df_expect
        need_keys_simple = []
        need_keys_complex = []
        for key in df.keys():
            if key in self._encrypt_key_mapping['simple']:
                need_keys_simple.append(key)
            elif key in self._encrypt_key_mapping['complex'].keys():
                need_keys_complex.append(key)
        for key in need_keys_simple:
            df[key] = self.simple_decrypt(df[key])
        for key in need_keys_complex:
            df[key] = self.complex_decrypt(key, df[key])

    def simple_decrypt(self, content: pd.Series) -> list:
        """简单字段解密"""
        content_list = content.to_list()
        # 替换None值为 '' ,None不支持解密
        content_list1 = ['' if i is None else i for i in content_list]
        content_list2 = Crypto.crypto_api_java(content_list1)
        # 再次替换回来原来的None
        content_list3 = [None if i is '' else i for i in content_list2]
        return content_list3

    def complex_decrypt(self, key, content: pd.Series):
        """复杂字段解密"""
        need_keys = self._encrypt_key_mapping['complex'][key]

        def func1(x):
            """临时提取并替换加密的字段"""
            need_to_decrypt = pd.DataFrame(columns=['encrypt'])
            try_json = str_to_json(x)
            content_list = try_json if try_json is not False else x
            if x in ('[]', '') or content_list is None:
                return x
            for row in content_list:
                for need_key in need_keys:
                    if need_key in row:
                        _uuid = generate_uuid()
                        need_to_decrypt.at[_uuid, 'encrypt'] = row[need_key]
                        row[need_key] = _uuid
            """请求接口解密参数"""
            need_to_decrypt['decrypt'] = Crypto.crypto_api_java(need_to_decrypt['encrypt'].to_list())
            """替换解密后的字符"""
            for row in content_list:
                for need_key in need_keys:
                    if need_key in row:
                        _uuid2 = row[need_key]
                        row[need_key] = need_to_decrypt.loc[_uuid2, 'decrypt']
            content_str = orjson.dumps(content_list).decode(errors='replace')
            return content_str

        content1 = content.map(func1)
        content2 = content1.to_list()
        return content2

    def custom_process(self):
        custom_funcs = get_class_functions(CustomAfterRequest)
        if self.testfunc in custom_funcs:
            self.df_actual = getattr(CustomAfterRequest(self.df_actual, **self.kwargs), self.testfunc)()

    def split_datas(self):
        df = self.df_actual
        ea_mapping = self.kwargs.get('expected_actual_mapping')
        for index, row in df.iterrows():
            self.split_data(index, row, ea_mapping, df, self.testfunc)
        return

    @classmethod
    def split_data(cls, index, series: pd.Series, mapping: dict, df, testfunc):
        """
        series 包含的key
        ['request_headers', 'request_method', 'env_url',
       'request_post_form_body', 'request_get_body', 'request_post_json_body',
       'response_text', 'response_latency']
        :param testfunc:
        :param df:
        :param index:
        :param series:
        :param mapping:
        :return:
        """
        response_text = series['response_text']
        try:
            response_json = orjson.loads(response_text)
        except orjson.JSONDecodeError:
            response_json = None
        split_dict = {}
        for key, jspath in mapping.items():
            split_dict[key] = cls.extract_value_by_jsonpath(response_json, jspath, testfunc)
        df.at[index, split_dict.keys()] = split_dict.values()
        return series

    @classmethod
    def extract_value_by_jsonpath(cls, response_json, jspath, testfunc):
        extract_values = json_path(response_json, jspath)
        if extract_values:
            # 不是False
            if testfunc not in complex_field.keys():
                # 简单字段
                extract_value = extract_values[0]
                return extract_value
            else:
                # 复杂字段
                return extract_values
        return None
