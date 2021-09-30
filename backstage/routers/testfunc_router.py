# -*- coding: utf-8 -*-
from fastapi import APIRouter
from typing import Optional, Dict
from backstage.service.tasks import run_api_test
from backstage.service.initialization import Initialization
from pydantic import BaseModel
from backstage.service.db_service import scoped_session

router = APIRouter(
    prefix="/testfunc",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)


@router.get('/{testfunc}')
async def pull_testfunc(
        testfunc: str,
        env_alias: str,
        sema_num_request: Optional[int] = 1,
        limit_each: Optional[int] = None,
        limit: Optional[int] = None,
        level: Optional[int] = None,
        timeout: int = 5,
        email_receivers: Optional[str] = None
):
    _kwargs = {
        'testfunc': testfunc,
        'env_alias': env_alias,
        'sema_num_request': sema_num_request,
        'limit_each': limit_each,
        'limit': limit,
        'level': level,
        'timeout': timeout,
        'email_receivers': email_receivers.split(",")
    }
    _kwargs = {k: v for k, v in _kwargs.items() if v}
    code = 2000
    msg = "success"
    data = None
    # 检查接口是否联通
    # check_http_code, other_code, other_msg = Initialization.check_api_alive(scoped_session(), testfunc, env_alias)
    # if check_http_code is False:
    #     code = other_code
    #     msg = other_msg
    # else:
        # pass
    if 1:
        res = run_api_test.delay(**_kwargs)
        task_id = res.task_id
        data = {"task_id": task_id}
    res = {"code": code, "msg": msg, "data": data}
    scoped_session.remove()
    return res
