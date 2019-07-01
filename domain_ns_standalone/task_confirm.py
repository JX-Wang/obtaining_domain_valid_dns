#! /usr/bin/env pyton
# coding:utf-8
"""
    post task
=====================
Author @ Wangjunxiong
Date @ 2019/06/26
"""
import requests

IP = "localhost"
PORT = 8888
TIMEOUT = 10


class TaskConfirm:
    def __init__(self, file_path):
        self.file_path = str(file_path).strip()
        self.d = {
            "file_path": self.file_path
        }

    def sec_post(self):
        sec_url = "http://{ip}:{port}/task_confirm/sec/".format(ip=str(IP), port=str(PORT))
        try:
            requests.post(url=sec_url, json=self.d, timeout=TIMEOUT)
        except Exception as e:
            # print "SEC POST ERROR -> ", str(e)
            return str(e)
        return True

    def query_post(self):
        query_url = "http://{ip}:{port}/task_confirm/query/".format(ip=str(IP), port=str(PORT))
        try:
            requests.post(url=query_url, json=self.d, timeout=TIMEOUT)
        except Exception as e:
            # print "QUERY POST ERROR -> ", str(e)
            return str(e)
        return True


if __name__ == '__main__':
    filename = "000001_20190626173201"
    TaskConfirm(filename).sec_post()
    TaskConfirm(filename).query_post()
