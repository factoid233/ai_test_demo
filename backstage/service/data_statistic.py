# -*- coding: utf-8 -*-
from backstage.utils.compare_value import CompareValue


class StatisticBase:
    @classmethod
    def compare_value(cls, data1, data2):
        data1_type = CompareValue.is_num_str(data1)
        data2_type = CompareValue.is_num_str(data2)
        if data1_type == 'num' and data2_type == 'num':
            data1 = CompareValue.str_to_num(data1)
            data2 = CompareValue.str_to_num(data2)
            return CompareValue.compare_num(data1, data2)
        elif data1_type == 'str' and data2_type == 'num':
            return False
        elif data1_type == 'num' and data2_type == 'str':
            return False
        elif data1_type == 'str' and data2_type == 'str':
            return CompareValue.compare_str(data1, data2)
        else:
            raise RuntimeError(f'暂不支持比较{data1} {data2}')
