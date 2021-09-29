# -*- coding: utf-8 -*-
import orjson
import structlog
import httpx
from backstage.dao.def_env import DefEnvHandler


class Initialization:

    @classmethod
    def log_init(cls):
        structlog.configure(
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso", utc=False),
                structlog.processors.format_exc_info,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.JSONRenderer(serializer=cls._log_serializer),
            ],
        )

    @classmethod
    def _log_serializer(cls, _obj, **kwargs):
        try:
            res = orjson.dumps(_obj, **kwargs)
            res1 = res.decode(errors='replace')
        except UnicodeDecodeError:
            res1 = ''
        return res1

    @classmethod
    def check_api_alive(cls, session, testfunc, env_alias):
        db = DefEnvHandler(session)
        test_url = db.get_env_url(testfunc, env_alias)
        if test_url is None:
            return False, 4001, f"the api url of {testfunc} {env_alias} dose not exist"
        res = httpx.post(test_url)
        if res.status_code != 200:
            return False, 4002, f"{test_url} connect fail! may be api service did not start"
        return True, None, None
