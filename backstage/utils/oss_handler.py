# -*- coding: utf-8 -*-
import oss2


class OSSHandler:
    # url过期时间 单位 s
    expires_time = 1 * 60 * 60 * 24

    def __init__(self, AccessKeyID, AccessKeySecret, bucket_name, endpoint):
        self.bucket = bucket_name
        endpoint = endpoint
        auth = oss2.Auth(AccessKeyID, AccessKeySecret)
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)

    def sign_url(self, path, expires_time=None):
        """
        生成签名url
        :param path: 存放在 oss里的相对路径
        :param expires_time: 过期时间单位秒，默认一天
        :return: url
        """
        if expires_time is None:
            expires_time = self.expires_time
        url = self.bucket.sign_url(method='GET', key=path, expires=expires_time, slash_safe=True)
        return url

    def list_files(self, prefix, **kwargs) -> list:
        """
        罗列bucket下执行文件夹里的所有文件
        :param prefix: 文件夹相对路径
        :return:
        """
        _iterator = oss2.ObjectIteratorV2(bucket=self.bucket, prefix=prefix, **kwargs)
        res = [i.key for i in _iterator]
        return res

    def upload_file(self, oss_key, local_file_path):
        self.bucket.put_object_from_file(key=oss_key, filename=local_file_path)
        return True

    def bucket_cls(self):
        """
        返回bucket对象
        :return:
        """
        return self.bucket

