# -*- coding: utf-8 -*-
from backstage.config.db_config import redis_host, redis_port

broker_url = 'redis://%(host)s:%(port)s/0' % {'host': redis_host, 'port': redis_port}
result_backend = 'redis://%(host)s:%(port)s/1' % {'host': redis_host, 'port': redis_port}

# 给celery注入 sqlalchemy engine配置
database_engine_options = {
    'pool_recycle': 3600,
    'pool_size': 10,
    'isolation_level': "READ_UNCOMMITTED",
    'pool_pre_ping': True
}
# mq连接超时配置
# The broker connection timeout only applies to a worker attempting to connect to the broker.
# It does not apply to producer sending a task
broker_connection_timeout = 5
broker_connection_max_retries = 5
# 不使用utc时间
enable_utc = False
timezone = 'Asia/Shanghai'
# celery kwagrs args参数存储
result_extended = True

# broker配置
broker_transport_options = {
    'visibility_timeout': 432000, 'max_retries': 1, 'socket_connect_timeout': 5, 'retry_on_timeout': True
}

# ## 后台存储配置
result_backend_transport_options = {
    'visibility_timeout': 18000, 'retry_policy': {'timeout': 5.0}}
result_backend_max_retries = 1
# 默认存储一天
result_expires = 86400
