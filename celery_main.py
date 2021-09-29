# -*- coding: utf-8 -*-
from celery import Celery
app = Celery(__name__)
# 加载配置文件
conf_path = 'backstage.config.celery_config'
app.config_from_object(conf_path)
app.autodiscover_tasks(['backstage.service.tasks'])

# if __name__ == '__main__':
#     app.worker_main(argv=['worker','--concurrency=1', '--pool=gevent', '--loglevel=info'])
