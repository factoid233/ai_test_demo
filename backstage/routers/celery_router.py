# -*- coding: utf-8 -*-
import pandas as pd
from fastapi import APIRouter
from typing import Optional, Dict

from backstage.config.db_config import redis_url
from backstage.utils.redis_handler import AioRedisAsyncio
from celery_main import app
from backstage.service.db_service import scoped_session
from backstage.dao.def_env import DefEnvHandler
from backstage.dao.def_type import DefTypeHandler
from backstage.config.common_config import ai_email_receivers

router = APIRouter(
    prefix="/celery",
    tags=["celery"],
    responses={404: {"description": "Not found"}},
)


@router.get('/get_all_envs')
async def get_all_envs():
    res1 = DefEnvHandler(scoped_session()).get_all_env_url_env_name_testfunc()
    res2 = DefTypeHandler(scoped_session()).get_all_zh_name()
    df1 = pd.DataFrame(res1)
    df2 = pd.DataFrame(res2)
    if df1.empty or df2.empty:
        code = 4004
        msg = "环境信息表格为空"
        data = None
    else:
        df = pd.merge(df1, df2, how='left', on=['testfunc'])
        results = []
        for name, grouped in df.groupby(['testfunc', 'testfunc_cn']):
            first = {'label': name[1], 'value': name[0], 'children': []}
            for index1, row1 in grouped.sort_values('env_en').iterrows():
                first['children'].append(
                    {'label': row1['env_en'], 'value': row1['env_en']})
            results.append(first)
        code = 2000
        msg = "success"
        data = {'test_info': results, 'email_receivers': ai_email_receivers}
    return dict(code=code, data=data, msg=msg)


@router.get('/active_jobs')
async def get_active_jobs():
    res: dict = app.control.inspect().active()
    if res is not None:
        all_tasks = [item for v in res.values() for item in v]
    else:
        all_tasks = []
    res_final = dict(code=2000, data=all_tasks)
    return res_final


@router.get('/stop_job/{uuid}')
async def stop_celery_job(uuid):
    res = app.control.revoke(uuid, terminate=True, signal="SIGKILL")
    return {"code": 2000, "msg": f"{res}"}


@router.get('/get_process_bar/{uuid}')
async def get_process_bar(uuid):
    redis = await AioRedisAsyncio.from_url(redis_url)
    res = await redis.get(uuid)
    if res:
        code = 2000
        msg = "success"
        data = float(res)
    else:
        code = 4003
        msg = f"不存在该键{uuid}"
        data = None
    return {"code": code, 'msg': msg, 'data': data}
