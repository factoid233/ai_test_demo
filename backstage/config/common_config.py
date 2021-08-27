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
