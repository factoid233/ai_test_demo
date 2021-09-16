# -*- coding: utf-8 -*-
import pandas as pd
import sqlalchemy.orm
from sqlalchemy import select

from backstage.model import case_models
from backstage.utils.db_handler import DBHandler

class CustomStmt:
    """
    自定义取数据方法
    返回必须为pd.Dataframe
    """

    def __init__(self, session: sqlalchemy.orm.Session, **kwargs):
        self.session = session
        self.kwargs = kwargs

    def vehicle_license(self):
        limit = self.kwargs.get('limit')
        model = case_models.case_vehicle_license
        stmt = select(model).where(model.flag != -1).limit(limit)
        res = DBHandler.query_orm_all_field_results(self.session, stmt=stmt)
        df = pd.DataFrame(res)
        return df

    def classify_pic(self):
        model = case_models.case_classify_pic
        stmt = select(model)
        res = DBHandler.query_orm_all_field_results(self.session, stmt=stmt)
        df = pd.DataFrame(res)

        # 限制分类数量
        limit_each = self.kwargs.get('limit_each')
        if limit_each is None:
            return df
        limit_each = self.kwargs.get('limit_each')
        df1 = df.groupby('classify').head(limit_each)
        return df1


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
