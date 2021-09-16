# -*- coding: utf-8 -*-
import pandas as pd
import sqlalchemy.sql.expression
import sqlalchemy.orm
from structlog import getLogger

from backstage.service.custom_handler import CustomStmt
from backstage.utils.common import get_class_functions
from backstage.dao.case_model import CaseHandler


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
        self._choose_custom_handler()
        self.logger.info(f'测试用例读取 done. 共{self.df.shape[0]}条用例')
        return self

    def _choose_custom_handler(self):
        custom_funcs = get_class_functions(CustomStmt)
        if self.testfunc not in custom_funcs:
            limit = self.kwargs.get('limit')
            res = CaseHandler(session=self.session).get_all_field_data(self.testfunc, limit)
            self.df = pd.DataFrame(res)
        else:
            # 走自定义方法
            self.df = getattr(CustomStmt(session=self.session, **self.kwargs), self.testfunc)()
        if self.df.empty:
            raise RuntimeError('获取用例失败，用例为空')


if __name__ == '__main__':
    x = FetchCaseData('daben_front', 1)
    x.normal_fetch_data()
