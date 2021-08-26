# -*- coding: utf-8 -*-
import json
import uuid


def str_to_json(data):
    """
    如果能加载成json 会返回一个字典，否则返回False
    判断使用 if res != False, 防止空字典报错
    :param data: 
    :return: 
    """
    if not isinstance(data, str):
        raise TypeError('传入的数据不是 str 类型')
    if isinstance(data, (list, dict)):
        return data
    if data is None:
        return False
    is_json = True if {"{", "["} & set(data) else False
    if is_json is False:
        return False
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return False


def generate_uuid():
    return uuid.uuid1().hex


def get_class_functions(_class):
    if type(_class) != type:
        raise ValueError('传入参数应该为 类对象')
    return list(filter(lambda x: not x.startswith("__"), _class.__dict__.keys()))


if __name__ == '__main__':
    str_to_json("123{")
