# -*- coding: utf-8 -*-
from typing import List
import pandas as pd
import sqlalchemy.sql.expression
import sqlalchemy.orm
from sqlalchemy_serializer import Serializer
from structlog import getLogger

from backstage.model import case_models
from backstage.service.custom_handler import CustomStmt
from backstage.utils.common import get_class_functions
from backstage.utils.db_handler import DBHandler
from backstage.dao.def_type import DefTypeHandler


class FetchCaseData:
    _testfunc_model_str = None
    _model = None
    _stmt = None
    df: pd.DataFrame = None
    testfunc_type = None

    def __init__(self, testfunc, session, **kwargs):
        self.testfunc = testfunc
        self.session: sqlalchemy.orm.Session = session
        self.kwargs = kwargs
        self.logger = getLogger(self.__class__).bind(uuid=kwargs.get('uuid'))

    def normal_fetch_data(self):
        self._check_testfunc()
        self._choose_stmt()
        self._execute_sql()
        self.logger.info(f'测试用例读取 done. 共{self.df.shape[0]}条用例')
        return self

    def _check_testfunc(self):
        self._testfunc_model_str = 'case_' + self.testfunc
        if self._testfunc_model_str not in case_models.__dict__.keys():
            raise KeyError(f'不存在该 {self.testfunc} 测试项')
        self._model = getattr(case_models, self._testfunc_model_str)
        return

    @classmethod
    def _common_stmt(cls, model, limit=None):
        stmt = sqlalchemy.select(model).limit(limit)
        return stmt

    def _choose_stmt(self):
        custom_funcs = get_class_functions(CustomStmt)
        if self.testfunc not in custom_funcs:
            limit = self.kwargs.get('limit')
            self.stmt = self._common_stmt(self._model, limit=limit)
        else:
            # 走自定义方法
            stmt = getattr(CustomStmt(**self.kwargs), self.testfunc)()
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

    def _execute_sql(self):
        res = DBHandler.query_orm_all_field_results(self.session, stmt=self.stmt)
        self.df = pd.DataFrame(res)


if __name__ == '__main__':
    x = FetchCaseData('daben_front', 1)
    x.normal_fetch_data()
