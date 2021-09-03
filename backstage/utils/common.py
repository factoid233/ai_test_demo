# -*- coding: utf-8 -*-
import copy
import hashlib
import orjson
import re
import uuid

import jsonpath


def str_to_json(data):
    """
    如果能加载成json 会返回一个字典，否则返回False
    判断使用 if res != False, 防止空字典报错
    :param data: 
    :return: 
    """
    if isinstance(data, (list, dict)):
        return data
    if not isinstance(data, str):
        raise TypeError('传入的数据不是 str 类型')
    if data is None:
        return False
    is_json = True if {"{", "["} & set(data) else False
    if is_json is False:
        return False
    try:
        return orjson.loads(data)
    except (orjson.JSONDecodeError, TypeError):
        return False


def generate_uuid():
    return uuid.uuid1().hex


def get_class_functions(_class):
    if type(_class) != type:
        raise ValueError('传入参数应该为 类对象')
    return list(filter(lambda x: not x.startswith("__"), _class.__dict__.keys()))


def md5(src):
    m2 = hashlib.md5()
    src = src.encode(encoding='utf-8')
    m2.update(src)
    return m2.hexdigest()


def json_key_replace(json_obj, old, new):
    """
    递归替换json中的key
    @param json_obj: json对象
    @param old: 需要被替换的key
    @param new: 需要替换成的目标key
    @return: 替换后的json对象
    """
    if isinstance(json_obj, list):
        for item in json_obj:
            json_key_replace(item, old, new)
    elif isinstance(json_obj, dict):
        for key, value in json_obj.copy().items():
            if key == old:
                json_obj[new] = json_obj.pop(key)
            if isinstance(value, (dict, list)):
                json_key_replace(value, old, new)
    else:
        pass
    return json_obj


def is_contains_chinese(strs):
    """检验是否含有中文字符"""
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def json_path(json_obj, expr):
    """
    对jsonpath表达式中[?(@.车辆品牌 == '1')]的中文key替换成英文key以便支持查找
    @param json_obj: json对象
    @param expr: jsonpath表达式
    @return: 替换后的json对象
    """
    if '$' not in expr:
        expr = '$..%s' % expr
    if not is_contains_chinese(expr):
        return jsonpath.jsonpath(json_obj, expr)
    json_obj = copy.deepcopy(json_obj)
    # 查找 符合 [?(@.车辆品牌 == '1')] 的关键词
    pattern = re.findall(r"@\.(.+?)[<>=]", expr)
    if pattern:
        zh_str = pattern[0]
        # 替换成40位哈希
        en_str = md5(zh_str)  # 存放32位哈希
        json_obj = json_key_replace(json_obj, zh_str, en_str)
        # 替换回中文
        en_expr = expr.replace(zh_str, en_str)
        en_res = jsonpath.jsonpath(json_obj, en_expr)
        zh_res = json_key_replace(en_res, en_str, zh_str)
    else:
        zh_res = jsonpath.jsonpath(json_obj, expr)
    return zh_res


if __name__ == '__main__':
    str_to_json("123{")
