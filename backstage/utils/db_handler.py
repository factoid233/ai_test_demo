# -*- coding: utf-8 -*-
import copy

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy_serializer import Serializer

import backstage.config.db_config as db_config


class DBHandler:
    @staticmethod
    def create_scoped_session(db_alias) -> sqlalchemy.orm.scoped_session:
        """
        db_config 命名中要以数据库的url要以 xxx_db_url形式命名
        :param db_alias: public_test_db_url cads_db_url
        :return:
        """
        db_alias_set = set(filter(lambda x: 'db_url' in x, db_config.__dict__.keys()))
        if db_alias not in db_alias_set:
            raise KeyError(f'传值必须为 {db_alias_set} 其一')
        db_url = getattr(db_config, db_alias)
        engine = sqlalchemy.create_engine(db_url, **db_config.engine_config)
        session = sqlalchemy.orm.sessionmaker(bind=engine)
        _scoped_session = sqlalchemy.orm.scoped_session(session)
        return _scoped_session

    @staticmethod
    def jsonify_query_model_result(data: list, json_format_option: dict = None) -> list:
        """
        格式化sqlalchemy查询出的结果，将对象（datetime,date...）转换为普通字符串
        不会格式化 json 为字符串
        :param data:
        :param json_format_option:
        :return:
        """
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

    @classmethod
    def format_query_all_field(cls, data: sqlalchemy.engine.result.ScalarResult):
        """
        变成 key value形式
        适用于stmt 为 select(model).scalars 的查询
        :param data:
        :return:
        """
        res1 = []
        for item in data:
            _dict = item.__dict__
            no_need_key = '_sa_instance_state'
            if no_need_key in _dict:
                del _dict[no_need_key]
            res1.append(_dict)
        res2 = cls.jsonify_query_model_result(res1)
        return res2

    @classmethod
    def query_orm_all_field_results(cls, session, stmt):
        res = session.execute(stmt).scalars()
        res1 = DBHandler.format_query_all_field(res)
        return res1

    @classmethod
    def query_special_fields_results(cls, session, stmt, params=None):
        """
        适用于指定字段的查询语句
        select(DefEnv.testfunc, DefEnv.request_headers,).where(DefEnv.testfunc == self.testfunc).where(DefEnv.env_en == self.env_alias)
        :param session:
        :param stmt:
        :param params:
        :return:
        """
        results = session.execute(stmt, params)
        res_keys = results.keys()
        res_values = results.fetchall()
        list_ = list()
        for one in res_values:
            temp_dict = dict()
            for key, value in zip(res_keys, one):
                temp_dict[key] = value
            list_.append(temp_dict)
        res1 = cls.jsonify_query_model_result(list_)
        return res1

    @classmethod
    def query_special_fields_result(cls, session, stmt, params=None):
        """
        查询指定单条记录
        :param session:
        :param stmt:
        :param params:
        :return:
        """
        res = cls.query_special_fields_results(session, stmt, params=None)
        if res:
            return res[0]
        else:
            return None
