# -*- coding: utf-8 -*-
import httpx
import orjson
from structlog import getLogger

logger = getLogger()


class Crypto:
    def __init__(self):
        pass

    @classmethod
    def crypto_api_java(cls, content, operation='decrypt'):
        """
        加解密接口
        :param content: list or str
        :param operation: encrypt、decrypt(default)
        :return:
        """
        url = 'http://118.190.235.150:5014/es/contact/crypto/name'
        payload = {}
        if isinstance(content, list):
            payload['name_array'] = orjson.dumps(content).decode(errors='replace')
            res_ret_msg = [None for _ in content]
        elif isinstance(content, str):
            payload['name'] = content
            res_ret_msg = ''
        else:
            raise RuntimeError(f'content{content}入参有误')

        try:
            payload['oper'] = operation
            res = httpx.post(url, data=payload)
            res_text = res.text
            res_json = orjson.loads(res_text)
            if int(res_json['ret_code']) == 0:
                res_ret_msg = res_json['ret_msg']
        except httpx.HTTPError:
            logger.error('加解密接口异常', exc_info=True, stack_info=True)
        return res_ret_msg
