# -*- coding: utf-8 -*-
import re


class CompareValue:
    """
    目前仅支持数字和字符串类型
    """
    @classmethod
    def compare_str(cls, data1, data2):
        if not (isinstance(data1, str) and isinstance(data2, str)):
            raise TypeError(f'{data1}{type(data1)} 和 {data2}{type(data2)} 不全为字符串类型')
        # 去掉空格后比较
        res = data1.strip() == data2.strip()
        return res

    @classmethod
    def compare_num(cls, data1, data2):
        num_tuple = (float, int)
        if not (isinstance(data1, num_tuple) and isinstance(data2, num_tuple)):
            raise TypeError(f'{data1}{type(data1)} 和 {data2}{type(data2)} 不全为数字类型')
        res = float(data1) == float(data2)
        return res

    @classmethod
    def str_to_num(cls, data):
        """
        判断字符串 _str 是否为数字，如果是数字转为数值格式
        :return:
        """
        if isinstance(data, (int, float)):
            return data
        if not isinstance(data, str):
            raise TypeError(f'传入数据({type(data)})非字符串类型')
        pattern1 = re.compile(r'^[-+]?[0-9]\d*$')
        pattern2 = re.compile(r'^[-+]?[0-9]\d*\.\d*$')
        data = data.strip()
        if pattern1.match(data):
            # 判断是否为整数
            return int(data)
        elif pattern2.match(data):
            return float(data)
        else:
            raise RuntimeError(f'{data}无法转换为数字')

    @classmethod
    def is_num_str(cls, data):
        if isinstance(data, (float, int)):
            return 'num'
        if isinstance(data, str):
            pattern = re.compile(r'^[-+]?[0-9]\d*(?:\.\d*)?$')
            data = data.strip()
            if pattern.match(data):
                return 'num'
            else:
                return 'str'
        raise RuntimeError(f'{data} 非数字和字符串类型')


if __name__ == '__main__':
    x = CompareValue.is_num_str('0012')
    print(x)
