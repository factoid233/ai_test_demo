# -*- coding: utf-8 -*-
from typing import List
import pandas as pd
import sqlalchemy.sql.expression
import sqlalchemy.orm
from sqlalchemy import select
from sqlalchemy_serializer import Serializer

from backstage.model import case_models, Base
from backstage.utils.db_handler import DBHandler


class FetchCaseData:
    testfunc_model_str = None
    _model = None
    _stmt = None

    def __init__(self, testfunc, session, **kwargs):
        self.testfunc = testfunc
        self.session: sqlalchemy.orm.Session = session
        self.kwargs = kwargs

    def normal_fetch_data(self) -> pd.DataFrame:
        self._check_testfunc()
        self._choose_stmt()
        res = self._execute_sql()
        return res

    def _check_testfunc(self):
        self.testfunc_model_str = 'case_' + self.testfunc
        if self.testfunc_model_str not in case_models.__dict__.keys():
            raise KeyError(f'不存在该 {self.testfunc} 测试项')
        self._model = getattr(case_models, self.testfunc_model_str)
        return

    def _choose_stmt(self):
        if self.testfunc not in CustomStmt.__dict__:
            limit = self.kwargs.get('limit')
            self.stmt = CustomStmt.common_stmt(self._model, limit=limit)
        else:
            # 走自定义方法
            stmt = getattr(CustomStmt, self.testfunc)(**self.kwargs)
            if not isinstance(stmt, sqlalchemy.sql.expression.Select):
                raise RuntimeError(f"自定义方法 CustomStmt.{self.testfunc} 返回类型有误")
            self.stmt = stmt

    @staticmethod
    def _jsonify_query_model_result(data: list, json_format_option: dict = None) -> list:
        """格式化sqlalchemy查询出的结果，将对象（datetime,date...）转换为普通字符串"""
        _format = {
            'date_format': '%Y-%m-%d',
            'datetime_format': '%Y-%m-%d %H:%M:%S',
            'time_format': '%H:%M',
            'decimal_format': '{}'
        }
        if isinstance(json_format_option, dict) and json_format_option:
            _format.update(json_format_option)
        serializer_json = Serializer(**_format)(data)
        return serializer_json

    def _execute_sql(self) -> pd.DataFrame:
        res = DBHandler.query_orm_all_field_results(self.session, stmt=self.stmt)
        df = pd.DataFrame(res)
        return df


class CustomStmt:
    @staticmethod
    def common_stmt(model, limit=None):
        stmt = select(model).limit(limit)
        return stmt

    @staticmethod
    def vehicle_license(**kwargs):
        limit = kwargs.get('limit')
        model = case_models.case_vehicle_license
        stmt = select(model).where(model.flag != -1).limit(limit)
        return stmt


if __name__ == '__main__':
    x = FetchCaseData('daben_front', 1)
    x.normal_fetch_data()
