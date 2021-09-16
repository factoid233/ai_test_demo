# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, JSON, SmallInteger, DateTime, text
from . import Base


class DefType(Base):
    __tablename__ = 'def_ai_test_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    testfunc = Column(String(255), comment='测试产品中文')
    testfunc_cn = Column(String(255), comment='测试产品英文')
    classify_mapping = Column(JSON, comment="图片分类一类补充映射")
    classify_field = Column(String(255), comment="分类的字段名称")
    translation_mapping = Column(JSON, comment="翻译映射")
    type = Column(Integer, comment="测试产品类别  1普通 2事故车 4图片分类 5验证码")
    timeout = Column(Integer, server_default=text("5"), comment="请求超时时间")
    enabled = Column(SmallInteger, server_default=text("1"), comment="1 激活，2 禁用")
    created_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))


class DefEnv(Base):
    __tablename__ = 'def_ai_test_env'
    id = Column(Integer, primary_key=True, autoincrement=True)
    testfunc = Column(String(255), comment='测试产品中文')
    env_en = Column(String(255), comment="环境别名")
    env_url = Column(String(255), comment="环境url")
    request_method = Column(String(20), comment="post get")
    request_headers = Column(JSON, comment="请求headers参数")
    request_get_body = Column(JSON, comment="请求get参数")
    request_post_form_body = Column(JSON, comment="请求post form参数")
    request_post_json_body = Column(JSON, comment="请求post json参数")
    expected_actual_mapping = Column(JSON, comment="预期结果与实际结果映射 {'expected':'actual jsonpath $.data.xxx'}")
    remark = Column(String(255), comment="备注")
    enabled = Column(SmallInteger, server_default=text("1"), comment="1 激活，2 禁用")
    created_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))