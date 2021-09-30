# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

db_local = {
    'db': 'test_data',
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'pwd': os.getenv('DB_PWD'),
    'port': 3306
}
oss_AccessKeyID = os.getenv('OSSUSER')
oss_AccessKeySecret = os.getenv('OSSPWD')
