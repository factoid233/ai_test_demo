# -*- coding: utf-8 -*-
from backstage.service.pre_request_handler import PreRequestHandler
from backstage.utils.db_handler import DBHandler
from backstage.service.fetch_case_data import FetchCaseData


class Control:
    case_data = None

    def run(self, **kwargs):
        session = DBHandler.create_scoped_session('local_db_url')

        # 获取用例数据
        _fetch_case_data = FetchCaseData(session=session(), **kwargs)
        self.case_data = _fetch_case_data.normal_fetch_data()

        # 请求前处理
        _pre_request_handler = PreRequestHandler(session=session(), data=self.case_data, **kwargs)
        _pre_request_handler.normal_run()


if __name__ == '__main__':
    x = Control()
    x.run(testfunc='vehicle_license', limit=1000, env_alias='dev_java')
