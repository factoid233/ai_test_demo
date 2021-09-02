# -*- coding: utf-8 -*-
import pandas as pd
from sqlalchemy import select

from backstage.model import case_models


class CustomStmt:
    """
    自定义取数据方法
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def vehicle_license(self):
        limit = self.kwargs.get('limit')
        model = case_models.case_vehicle_license
        stmt = select(model).where(model.flag != -1).limit(limit)
        return stmt


class CustomPreRequest:
    """
    自定义前置处理
    传入的 df 中包含的 key
    ['env_url', 'request_post_json_body', 'request_post_form_body',
       'request_headers', 'request_method', 'request_get_body']

    返回的df中也必须包含这些key

    kwargs 包含最初传入的所有参数
    """
    df: pd.DataFrame

    def __init__(self, df, **kwargs):
        self.df = df
        self.kwargs = kwargs

    def vehicle_license(self):
        return self.df


class CustomAfterRequest:
    """
    传入 df 的key 为
    ['env_url', 'request_headers', 'request_get_body', 'request_method',
       'request_post_form_body', 'request_post_json_body', 'response_text',
       'response_latency']
    """
    def __init__(self, df, **kwargs):
        self.df = df
        self.kwargs = kwargs

    def vehicle_license(self):
        return self.df
