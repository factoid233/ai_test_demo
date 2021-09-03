# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Float, text, DateTime

from . import Base


class Log(Base):
    __tablename__ = "log_ai_test"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id2 = Column(String(255), comment="周测id")
    celery_id = Column(String(255))
    testfunc = Column(String(255), comment="测试产品")
    env_en = Column(String(255), comment="测试环境别名")
    req_body = Column(String(255), comment="请求参数")
    statistics_results = Column(String(255), comment="统计结果数据")
    sum_avg = Column(Float, comment="整体平均精度值")
    latency_avg = Column(Float, comment="平均耗时")
    latency_p70 = Column(Float, comment="表示按升序处理请求时间：第70%位的平均耗时")
    latency_p90 = Column(Float, comment="表示按升序处理请求时间：第90%位的平均耗时")
    latency_p95 = Column(Float, comment="表示按升序处理请求时间：第95%位的平均耗时")
    latency_p99 = Column(Float, comment="表示按升序处理请求时间：第99%位的平均耗时")
    executor = Column(String(255), comment="执行者")
    executor_ip = Column(String(255), comment="执行者ip")
    host = Column(String(255), comment="执行主机地址")
    result_file_path = Column(String(255), comment="结果excel地址")
    created_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_time = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))