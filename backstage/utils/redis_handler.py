# -*- coding: utf-8 -*-
import aioredis


class AioRedisAsyncio(aioredis.client.Redis):
    def __init__(self,*args,**kwargs):
        super(AioRedisAsyncio, self).__init__(*args,**kwargs)




if __name__ == '__main__':
    import asyncio
    from backstage.config.db_config import redis_host,redis_port
    x = AioRedisAsyncio(redis_host, redis_port)
    asyncio.run(x.set('test', '1234'))
