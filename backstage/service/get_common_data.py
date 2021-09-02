# -*- coding: utf-8 -*-
from backstage.dao.def_env import DefEnvHandler
from backstage.dao.def_type import DefTypeHandler


class GetCommonData:
    _session = None
    _kwargs = None
    _testfunc = None
    _env_en = None
    common_data: dict = {}

    def __init__(self, session, **kwargs):
        self._session = session
        self._kwargs = kwargs
        self._testfunc = kwargs.get('testfunc')
        self._env_en = kwargs.get('env_alias')

    def normal_run(self):
        self.query_testfunc_type()
        self.query_expected_actual_mapping()

    def query_testfunc_type(self):
        testfunc_type = DefTypeHandler(self._session).get_type(self._testfunc)
        self.common_data['testfunc_type'] = testfunc_type

    def query_expected_actual_mapping(self):
        res = DefEnvHandler(self._session).get_expected_actual_mapping(testfunc=self._testfunc, env_en=self._env_en)
        self.common_data['expected_actual_mapping'] = res
