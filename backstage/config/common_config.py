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
