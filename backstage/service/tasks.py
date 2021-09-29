# -*- coding: utf-8 -*-
import traceback

import celery.exceptions

from celery_main import app
from structlog import getLogger
import sqlalchemy.exc
from backstage.service.control import Control
from backstage.service.custom_exception import ApiConnectFail
logger = getLogger(__file__)


@app.task(bind=True)
def run_api_test(self, **kwargs):
    error_msg = ''
    test_id = self.request.id
    logger.bind(uuid=test_id)
    try:
        kwargs['uuid'] = test_id
        _control = Control()
        _control.run(**kwargs)
    except ApiConnectFail as e:
        error_msg = str(e)
    except sqlalchemy.exc.SQLAlchemyError as e:
        error_msg = f'数据库操作异常,{e}'
    except celery.exceptions.CeleryError as e:
        error_msg = 'celery异常'
    finally:
        if error_msg:
            error_detail = traceback.format_exc()
            logger.error(error_msg, traceback=error_detail)
    return f"{test_id} done"
