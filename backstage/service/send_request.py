# -*- coding: utf-8 -*-
import asyncio
import sys

import httpx
import pandas as pd
from structlog import getLogger

from backstage.config.common_config import sema_num_request, request_timeout
from backstage.dao.def_type import DefTypeHandler
from backstage.service.custom_exception import ApiConnectFail


class SendRequest:
    df = None
    _exception = []
    limit_num = 10
    _exception_normal_response = set()
    _exception_normal_response_num = 0

    def __init__(self, df, session, **kwargs):
        self.kwargs = kwargs
        self.df = df
        self.session = session
        self.logger = getLogger(self.__class__).bind(uuid=kwargs.get('uuid'))

    def normal_run(self):
        asyncio.run(self.send_reqs())
        return self

    async def send_reqs(self):
        sema_num = self.kwargs.get('sema_num_request', sema_num_request)
        self.logger.info(f'开始请求接口， 共开启 {sema_num}个并发')
        timeout = self.get_timeout()
        timeout = timeout if timeout else request_timeout
        sema = asyncio.Semaphore(sema_num)
        async with httpx.AsyncClient(timeout=timeout) as client:
            tasks = []
            for index, row in self.df.iterrows():
                task = asyncio.create_task(self.req_sema(sema, client, row, index))
                tasks.append(task)
            await asyncio.gather(*tasks)

    def get_timeout(self):
        timeout = self.kwargs.get('timeout')
        if timeout and isinstance(timeout, int):
            self.logger.info(f'开启自定义耗时 timeout={timeout}')
            return timeout
        testfunc = self.kwargs.get('testfunc')
        return DefTypeHandler(self.session).get_timeout(testfunc)

    async def req_sema(self, sema, client: httpx.AsyncClient, series: pd.Series, index):
        async with sema:
            await self.req_one(client=client, series=series, index=index)

    async def req_one(self, client: httpx.AsyncClient, series: pd.Series, index):
        """
        url,method,params,data,header,json
        @param index:
        @param client:
        @param series:
        @return:
        """
        response = None
        error = None
        try:
            response = await client.request(method=series['request_method'].lower(),
                                            url=series['env_url'],
                                            params=series['request_get_body'],
                                            data=series['request_post_form_body'],
                                            json=series['request_post_json_body'])
            response.raise_for_status()
            if self._exception_normal_response_num < self.limit_num:
                self._exception_normal_response.add(response.text)
                self._exception_normal_response_num += 1
                self._exception = []
            else:
                pass
            self.logger.info(index, latency=response.elapsed.total_seconds(), response_text=response.text, **series.to_dict())

        except httpx.TimeoutException as exc:
            error = "{}".format(client.timeout)
        except httpx.HTTPStatusError as exc:
            response = exc.response
            error = f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
        except httpx.HTTPError as exc:
            error = sys.exc_info()[0].__doc__.strip()
        finally:
            if error:
                self._exception_normal_response_num = 0
                self._exception.append(error)
                self.df.at[index, 'error'] = error
                self.logger.error(error, exc_info=False, stack_info=False, **series.to_dict())
        if len(self._exception) >= self.limit_num and set(self._exception) == 1:
            exception_msg = "\t".join(self._exception)
            msg = f"接口连接失败，可能接口({series['env_url']})未开启 Detail:\t{exception_msg}"
            raise ApiConnectFail(msg)
        if self._exception_normal_response_num >= self.limit_num and set(self._exception_normal_response) == 1:
            msg = f"接口连接失败，可能接口({series['env_url']})未开启 Detail:\t{response.text}"
            raise ApiConnectFail(msg)
        if response is not None:
            self.df.at[index, 'response_text'] = response.text
            self.df.at[index, 'response_latency'] = response.elapsed.total_seconds()
