# -*- coding: utf-8 -*-
from backstage.service.pre_request_handler import PreRequestHandler
from backstage.utils.db_handler import DBHandler
from backstage.service.fetch_case_data import FetchCaseData
from backstage.service.send_request import SendRequest
from backstage.service.initialization import Initialization
from backstage.service.after_request_handler import AfterRequestHandler
from backstage.service.compare_data import CompareData
from backstage.service.get_common_data import GetCommonData
from backstage.service.data_statistic import DataStatistic


class Control:
    def __init__(self):
        Initialization.log_init()

    def run(self, **kwargs):
        session = DBHandler.create_scoped_session('local_db_url')

        # 获取公共参数字段
        _get_common_data = GetCommonData(session=session(), **kwargs)
        _get_common_data.normal_run()
        kwargs.update(_get_common_data.common_data)

        # 获取用例数据
        _fetch_case_data = FetchCaseData(session=session(), **kwargs)
        _fetch_case_data.normal_fetch_data()

        # 请求前处理
        _pre_request_handler = PreRequestHandler(session=session(), data=_fetch_case_data.df, **kwargs)
        _pre_request_handler.normal_run()

        # 发送请求
        _send_request = SendRequest(_pre_request_handler.df, session=session(), **kwargs)
        _send_request.normal_run()

        # 请求后处理 处理预期结果
        _after_request_handler = AfterRequestHandler(df_expect=_fetch_case_data.df,
                                                     df_actual=_send_request.df,
                                                     session=session(),
                                                     **kwargs)
        _after_request_handler.normal_run()

        # 比较预期结果与实际结果
        _compare_data = CompareData(df_actual=_after_request_handler.df_actual,
                                    df_expect=_after_request_handler.df_expect,
                                    **kwargs)
        _compare_data.normal_run()

        # 统计数据
        _data_statistic = DataStatistic(df_actual=_after_request_handler.df_actual,
                                        df_expect=_after_request_handler.df_expect,
                                        df_compare=_compare_data.dfs,
                                        **kwargs)
        _data_statistic.normal_run()

        return


if __name__ == '__main__':
    import uuid

    x = Control()
    # x.run(testfunc='vehicle_license', limit=30, env_alias='dev_java', sema_num_request=5, uuid=uuid.uuid1().hex)
    # x.run(testfunc='daben_front', limit=100, env_alias='dev_java', sema_num_request=5, uuid=uuid.uuid1().hex)
    x.run(testfunc='daben_back', limit=100, env_alias='dev_java', sema_num_request=5, uuid=uuid.uuid1().hex)
