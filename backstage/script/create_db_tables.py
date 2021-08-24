# -*- coding: utf-8 -*-
import sqlalchemy
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).joinpath('../../..').resolve()))
from backstage.model.def_models import Base as Base_def
from backstage.model.log_models import Base as Base_log
from backstage.config.db_config import local_db_url

engine = sqlalchemy.create_engine(local_db_url)
Base_def.metadata.create_all(engine, checkfirst=True)
print('create def tables done')
Base_log.metadata.create_all(engine, checkfirst=True)
print('create log tables done')