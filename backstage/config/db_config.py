# -*- coding: utf-8 -*-
from backstage.config.account_config import *

engine_config = {
    'pool_recycle': 3600,
    'pool_size': 10,
    'isolation_level': "READ_UNCOMMITTED",
    'pool_pre_ping': True
}
# 数据用例数据库
mysql_url = "mysql+pymysql://%(user)s:%(pwd)s@%(host)s/%(db)s"
current_db = db_local
cads_db_url = mysql_url % db_cdas
current_db_url = mysql_url % current_db

# celery记录用数据库
mysql_url_celery = 'db+mysql+pymysql://%(user)s:%(pwd)s@%(host)s/%(db)s'
current_db_url_celery = mysql_url_celery % current_db
# redis
redis_host = "10.100.1.10"
redis_port = 10001
# redis key存活时间 取一天
redis_expire = 86400

redis_url = 'redis://%(host)s:%(port)s/0' % {'host': redis_host, 'port': redis_port}
