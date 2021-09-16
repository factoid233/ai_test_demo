# -*- coding: utf-8 -*-
import sqlalchemy

from backstage.model import case_models
from backstage.utils.db_handler import DBHandler


class CaseHandler:
    def __init__(self, session):
        self.session = session

    @classmethod
    def _check_testfunc(cls, testfunc):
        _testfunc_model_str = 'case_' + testfunc
        if _testfunc_model_str not in case_models.__dict__.keys():
            raise KeyError(f'不存在该 {testfunc} 测试项')
        _model = getattr(case_models, _testfunc_model_str)
        return _model

    def get_all_field_data(self, testfunc, limit):
        _model = self._check_testfunc(testfunc)
        stmt = sqlalchemy.select(_model).limit(limit)
        res = DBHandler.query_orm_all_field_results(self.session, stmt=stmt)
        return res
