# -*- coding: utf-8 -*-
from sqlalchemy import select

from backstage.model.def_models import DefEnv
from backstage.utils.db_handler import DBHandler


class DefEnvHandler:
    def __init__(self, session):
        self.session = session

    def get_request_content(self, testfunc, env_alias):
        """
        :return:  ['testfunc', 'request_headers', 'request_get_body', 'request_post_form_body', 'request_post_json_body',
         'request_method', 'env_url']
        """
        stmt = (
            select(
                DefEnv.testfunc, DefEnv.request_headers, DefEnv.request_get_body, DefEnv.request_post_form_body,
                DefEnv.request_post_json_body, DefEnv.request_method, DefEnv.env_url)
                .where(DefEnv.testfunc == testfunc)
                .where(DefEnv.env_en == env_alias)
        )
        res: dict = DBHandler.query_special_fields_result(self.session, stmt)
        return res

    def get_expected_actual_mapping(self, testfunc, env_en):
        stmt = select(DefEnv.expected_actual_mapping).where(DefEnv.testfunc == testfunc).where(DefEnv.env_en == env_en)
        res: dict = DBHandler.query_special_fields_result_no_key(self.session, stmt)
        return res

    def get_env_url(self, testfunc, env_en):
        stmt = select(DefEnv.env_url).where(DefEnv.testfunc == testfunc).where(DefEnv.env_en == env_en)
        res: dict = DBHandler.query_special_fields_result_no_key(self.session, stmt)
        return res
