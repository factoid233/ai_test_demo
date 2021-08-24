# -*- coding: utf-8 -*-
from backstage.config.account_config import *

engine_config = {
    'pool_recycle': 3600,
    'pool_size': 10,
    'isolation_level': "READ_UNCOMMITTED",
    'pool_pre_ping': True
}

mysql_url = "mysql+pymysql://%(user)s:%(pwd)s@%(host)s/%(db)s"
public_test_db_url = mysql_url % db_118
cads_db_url = mysql_url % db_cdas
local_db_url = mysql_url % db_local
