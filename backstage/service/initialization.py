# -*- coding: utf-8 -*-
import orjson
import structlog


class Initialization:

    @classmethod
    def log_init(cls):
        structlog.configure(
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(serializer=cls._log_serializer),
            ])

    @classmethod
    def _log_serializer(cls, _obj, **kwargs):
        try:
            res = orjson.dumps(_obj, **kwargs)
            res1 = res.decode(errors='replace')
        except UnicodeDecodeError:
            res1 = ''
        return res1

