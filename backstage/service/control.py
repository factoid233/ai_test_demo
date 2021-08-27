# -*- coding: utf-8 -*-
from backstage.service.pre_request_handler import PreRequestHandler
from backstage.utils.db_handler import DBHandler
from backstage.service.fetch_case_data import FetchCaseData
from backstage.service.send_request import SendRequest
from backstage.service.initialization import Initialization
from backstage.service.after_request_handler import AfterRequestHandler


class Control:
    def __init__(self):
        Initialization.log_init()

    def run(self, **kwargs):
        session = DBHandler.create_scoped_session('local_db_url')

        # 获取用例数据
        _fetch_case_data = FetchCaseData(session=session(), **kwargs)
        _fetch_case_data.normal_fetch_data()

        # 请求前处理
        _pre_request_handler = PreRequestHandler(session=session(), data=_fetch_case_data.df, **kwargs)
        _pre_request_handler.normal_run()

        # 发送请求
        _send_request = SendRequest(_pre_request_handler.df, session=session(), **kwargs)
        _send_request.normal_run()

        # 请求后处理
        _after_request_handler = AfterRequestHandler(_fetch_case_data.df, **kwargs)
        _after_request_handler.normal_run()

        return


if __name__ == '__main__':
    import uuid
    x = Control()
    x.run(testfunc='vehicle_license', limit=20, env_alias='dev_java', sema_num_request=3, uuid=uuid.uuid1().hex)
