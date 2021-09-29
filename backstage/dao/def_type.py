# -*- coding: utf-8 -*-
from sqlalchemy import select
from backstage.model.def_models import DefType
from backstage.utils.db_handler import DBHandler


class DefTypeHandler:
    def __init__(self, session):
        self.session = session

    def get_timeout(self, testfunc):
        stmt = select(DefType.timeout).where(DefType.testfunc == testfunc)
        res: dict = DBHandler.query_special_fields_result_no_key(self.session, stmt)
        return res

    def get_type(self, testfunc):
        stmt = select(DefType.type).where(DefType.testfunc == testfunc)
        res: dict = DBHandler.query_special_fields_result_no_key(self.session, stmt)
        return res

    def get_translation_mapping(self, testfunc):
        stmt = select(DefType.translation_mapping).where(DefType.testfunc == testfunc)
        res: dict = DBHandler.query_special_fields_result_no_key(self.session, stmt)
        return res

    def get_classify_mapping(self, testfunc):
        stmt = select(DefType.classify_mapping).where(DefType.testfunc == testfunc)
        res: dict = DBHandler.query_special_fields_result_no_key(self.session, stmt)
        return res

    def get_classify_field(self, testfunc):
        stmt = select(DefType.classify_field).where(DefType.testfunc == testfunc)
        res: dict = DBHandler.query_special_fields_result_no_key(self.session, stmt)
        return res

    def get_all_zh_name(self):
        stmt = select(DefType.testfunc, DefType.testfunc_cn)
        res: dict = DBHandler.query_special_fields_results(self.session, stmt)
        return res
