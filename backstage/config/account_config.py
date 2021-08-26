# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

db_118 = {
    'db': 'test_data',
    'host': '118.190.91.189',
    'user': os.getenv('DB_118_USER'),
    'pwd': os.getenv('DB_118_PWD'),
    'port': 3306
}
# cdas 139.129.97.251
db_cdas = {
    'db': 'cdas',
    'host': 'vpc-main.mysql.rds.aliyuncs.com',
    'user': os.getenv('DB_CDAS_USER'),
    'pwd': os.getenv('DB_CDAS_PWD'),
    'port': 3306
}
db_local = {
    'db': 'test_data',
    'host': '172.16.1.167',
    'user': os.getenv('DB_172_USER'),
    'pwd': os.getenv('DB_172_PWD'),
    'port': 3306
}
oss_AccessKeyID = os.getenv('OSSUSER')
oss_AccessKeySecret = os.getenv('OSSPWD')
