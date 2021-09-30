# -*- coding: utf-8 -*-
import sys
from pathlib import Path

from sqlalchemy.orm import sessionmaker

sys.path.append(str(Path('.').resolve()))
from sqlalchemy import create_engine
from backstage.model import Base
from backstage.config.db_config import current_db_url
from backstage.model.def_models import *
from backstage.model.case_models import *
engine = create_engine(current_db_url, encoding="utf-8")
Base.metadata.create_all(engine)

_Session = sessionmaker(bind=engine)
session = _Session()
# def_type
sql1 = """INSERT INTO `def_ai_test_type` VALUES (1, 'classify_pic', '图片分类', '{\"0\": \"车\", \"1\": \"登记证正面\", \"2\": \"登记证反面\", \"3\": \"行驶证\", \"4\": \"铭牌\", \"5\": \"挡风玻璃\", \"6\": \"其他不相关图片\", \"7\": \"合格证\"}', 'classify', '{\"0\": \"车\", \"1\": \"登记证正面\", \"2\": \"登记证反面\", \"3\": \"行驶证\", \"4\": \"铭牌\", \"5\": \"挡风玻璃\", \"6\": \"其他不相关图片\", \"7\": \"合格证\"}', 4, 5, NULL, '2021-09-15 14:23:23', '2021-09-15 18:25:47');"""
session.execute(sql1)

# def_env
sql2 = """INSERT INTO `def_ai_test_env` VALUES (1, 'classify_pic', 'dev_java', 'http://ai_test_nginx:7000/api/demo', 'post', NULL, '{\"sign\": \"${sign}\"}', NULL, '{\"url\": \"${pic_url}\"}', '{\"classify\": \"$.data.class_index\"}', NULL, NULL, '2021-09-15 14:26:02', '2021-09-15 14:27:41');"""
session.execute(sql2)

# case_classify
for i in range(100):
    sql3 = f"insert into `case_classify_pic` (pic_url,classify) VALUES({i},1)"
    session.execute(sql3)
session.commit()
session.close()