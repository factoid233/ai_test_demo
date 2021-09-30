# -*- coding: utf-8 -*-
import pandas as pd
import sqlalchemy.orm
import re
from copy import deepcopy

from structlog import getLogger

from backstage.utils.common import generate_uuid, get_class_functions
from backstage.utils.oss_handler import OSSHandler
from backstage.config.account_config import oss_AccessKeyID, oss_AccessKeySecret
from backstage.config.common_config import oss_endpoint_mapping, oss_bucket_name, oss_pic_url_expires_time
from backstage.service.custom_handler import CustomPreRequest
from backstage.dao.def_env import DefEnvHandler


class PreRequestHandler:
    _request_body_template_key = {'request_headers', 'request_get_body', 'request_post_form_body',
                                  'request_post_json_body', 'request_method', 'env_url'}
    _request_body_template = None
    df: pd.DataFrame = None

    def __init__(self, session, data, **kwargs):
        self.testfunc = kwargs.get('testfunc')
        self.env_alias = kwargs.get('env_alias')
        self.data_src: pd.DataFrame = data
        self.kwargs = kwargs
        if self.testfunc is None:
            raise KeyError('缺少入参 {testfunc}')
        if self.env_alias is None:
            raise KeyError('缺少入参 {env_alias}')
        self.session: sqlalchemy.orm.Session = session
        self.logger = getLogger(self.__class__).bind(uuid=kwargs.get('uuid'))

    def get_request_body(self):
        """
        :return:  ['testfunc', 'request_headers', 'request_get_body', 'request_post_form_body', 'request_post_json_body',
         'request_method', 'env_url']
        """

        self._request_body_template: dict = DefEnvHandler(self.session).get_request_content(self.testfunc, self.env_alias)

    def generate_sign(self):
        self.data_src['sign'] = [generate_uuid() for _ in self.data_src.index]

    def sign_pic_url(self):
        need_keys = {'url', 'pic_url'}
        key_set = set(self.data_src.keys()) & need_keys
        if key_set:
            key = key_set.pop()
        else:
            return
        oss = OSSHandler(oss_AccessKeyID, oss_AccessKeySecret, oss_bucket_name, oss_endpoint_mapping['beijing'])
        self.data_src[key] = self.data_src[key].map(lambda x: oss.sign_url(x, oss_pic_url_expires_time))

    def get_reshape_key(self) -> set:
        need_key = set()
        for key in self._request_body_template_key:
            second_dict: dict = self._request_body_template[key]
            if second_dict is None or isinstance(second_dict, str):
                continue
            for v1 in second_dict.values():
                matcher = re.match(r'\$\{(.+)\}', v1)
                if matcher:
                    need_key.add(matcher.group(1))
        return need_key

    def reshape_data(self):
        """
        替换请求数据中的 ${pic_url} ${sign}的值
        :return:
        """
        actual_keys = self.get_reshape_key()
        src_keys = set(self.data_src.keys())
        need_keys = actual_keys & src_keys
        df = self.data_src[need_keys].copy()
        for key in self._request_body_template_key:
            def func(series):
                template: dict = deepcopy(self._request_body_template[key])
                if template is None:
                    return None
                if isinstance(template, str):
                    return template
                for k1, v1 in template.copy().items():
                    matcher = re.match(r'\$\{(.+)\}', v1)
                    if matcher and matcher.group(1) in need_keys:
                        template[k1] = series[matcher.group(1)]
                return template

            df[key] = df.apply(axis=1, func=func)
        df.drop(columns=need_keys, inplace=True)
        self.df = df

    def custom_process(self):
        custom_funcs = get_class_functions(CustomPreRequest)
        if self.testfunc in custom_funcs:
            self.df = getattr(CustomPreRequest(self.df, **self.kwargs), self.testfunc)()

    def normal_run(self):
        self.get_request_body()
        self.generate_sign()
        # self.sign_pic_url()
        self.reshape_data()
        self.custom_process()
        self.logger.info('请求前置处理 done')
        return self
