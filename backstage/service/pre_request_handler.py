# -*- coding: utf-8 -*-
import pandas as pd
import sqlalchemy.orm
import re
from sqlalchemy import select
from copy import deepcopy
from backstage.model.def_models import DefEnv
from backstage.utils.db_handler import DBHandler
from backstage.utils.common import generate_uuid


class PreRequestHandler:
    request_body_template_key = {'request_headers', 'request_get_body', 'request_post_form_body',
                                 'request_post_json_body'}
    request_body_template = None

    def __init__(self, session, data, **kwargs):
        self.testfunc = kwargs.get('testfunc')
        self.env_alias = kwargs.get('env_alias')
        self.data_src: pd.DataFrame = data
        if self.testfunc is None:
            raise KeyError('缺少入参 {testfunc}')
        if self.env_alias is None:
            raise KeyError('缺少入参 {env_alias}')
        self.session: sqlalchemy.orm.Session = session

    def get_request_body(self):
        """
        :return:  {'testfunc':'', 'request_headers':'', 'request_get_body':'', 'request_post_form_body':'', 'request_post_json_body':''}
        """
        stmt = (
            select(
                DefEnv.testfunc, DefEnv.request_headers, DefEnv.request_get_body, DefEnv.request_post_form_body,
                DefEnv.request_post_json_body)
                .where(DefEnv.testfunc == self.testfunc)
                .where(DefEnv.env_en == self.env_alias)
        )
        self.request_body_template: dict = DBHandler.query_special_fields_result(self.session, stmt)

    def generate_sign(self):
        self.data_src['sign'] = [generate_uuid() for _ in self.data_src.index]

    def get_reshape_key(self) -> set:
        need_key = set()
        for key in self.request_body_template_key:
            second_dict: dict = self.request_body_template[key]
            if second_dict is None:
                continue
            for v1 in second_dict.values():
                matcher = re.match(r'\$\{(.+)\}', v1)
                if matcher:
                    need_key.add(matcher.group(1))
        return need_key

    def reshape_data(self):
        actual_keys = self.get_reshape_key()
        src_keys = set(self.data_src.keys())
        need_keys = actual_keys & src_keys
        df = self.data_src[need_keys].copy()
        for key in self.request_body_template_key:
            def func(series):
                template: dict = deepcopy(self.request_body_template[key])
                if template is None:
                    return None
                for k1, v1 in template.copy().items():
                    matcher = re.match(r'\$\{(.+)\}', v1)
                    if matcher and matcher.group(1) in need_keys:
                        template[k1] = series[matcher.group(1)]
                return template
            df[key] = df.apply(axis=1, func=func)
        return df

    def normal_run(self):
        self.get_request_body()
        self.generate_sign()
        self.reshape_data()
