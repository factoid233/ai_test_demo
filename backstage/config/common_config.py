# -*- coding: utf-8 -*-
oss_endpoint_mapping = {
    'shanghai': 'https://oss-cn-shanghai.aliyuncs.com',
    'beijing': 'https://oss-cn-beijing.aliyuncs.com'
}

# 隐私图片生效时间 单位 s
# 3天
oss_pic_url_expires_time = 259200
oss_bucket_name = 'ai-test-images'

# 默认并发数
sema_num_request = 3
# 默认请求超时时间
request_timeout = 10

# 数据库中加密的部分字段
encrypt_key = {
    'simple': ['owner_card_type_number', 'name', 'identity_number',
               'gou_mai_fang_ming_cheng', 'sfzhmhzzjgdm', 'owner'],
    'complex': {
        'transfer_reg_summary': ['机动车所有人/身份证明名称/号码'],
        'transfer_register': ['姓名/名称', '身份证明名称/号码'],
        'change_record': ['姓名/名称', '身份证明名称/号码'],
        'mortgage_register': ['抵押权人姓名/名称', '身份证明名称/号码']
    }
}

# 复杂字段
complex_field = {
    'daben_back': [
        'remark', 'reissue', 'exchange',
        'correction', 'change_record', 'pledge_record', 'serial_number',
        'endorse_delete', 'guo_hu_deng_ji', 'cancel_mortgage',
        'change_register', 'mortgage_register', 'transfer_register',
        'discharge_mortgage', 'discharge_pledge_record'],
    'daben_front': [
        'transfer_reg_summary'
    ]
}

# 结果表格展示额外字段
extra_keys = {'id', 'sign', 'pic_url', 'url', 'created_time'}

# 统计字段翻译
simple_translation_mapper = {
    'accuracy_weight_mean': '加权平均精度',
    'latency_mean': '平均耗时',
    'latency_P70': '耗时P70',
    'latency_P90': '耗时P90',
    'latency_P95': '耗时P95',
    'latency_P99': '耗时P99'
}
