# -*- coding: utf-8 -*-
import orjson
import pandas as pd

from backstage.config.common_config import encrypt_key
from backstage.service.custom_handler import CustomAfterRequest
from backstage.utils.common import generate_uuid, str_to_json, get_class_functions
from backstage.utils.crypto_handler import Crypto


class AfterRequestHandler:
    df: pd.DataFrame = None
    kwargs = None
    _encrypt_key_mapping = None

    def __init__(self, df, **kwargs):
        self.df = df
        self.kwargs = kwargs
        self._encrypt_key_mapping = encrypt_key

    def normal_run(self):
        self.decrypt_data()
        self.custom_process()

    def decrypt_data(self):
        """解密部分敏感字段"""
        df = self.df
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
        testfunc = self.kwargs.get('testfunc')
        if testfunc in custom_funcs:
            self.df = getattr(CustomAfterRequest(self.df, **self.kwargs), testfunc)()

