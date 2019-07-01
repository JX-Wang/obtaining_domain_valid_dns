# encoding: utf-8
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
import urllib
import json
import time


@gen.coroutine
def async_fetch(url, data_type):

    try:
        start = time.time()
        res = yield AsyncHTTPClient().fetch(url, request_timeout=10)
        res_time = round((time.time() - start) * 1000, 4)  # 单位ms
        print ("{0}, {1}ms".format(url, res_time))
    except Exception, e:
        print e, url
        raise gen.Return(("ERROR",e))
    if data_type in ('json', 'JSON'):
        raise gen.Return(json.loads(res.body))
    else:
        raise gen.Return(res.body)

@gen.coroutine
def async_post(url, json_data, data_type):

    try:
        start = time.time()
        json_data = json.dumps(json_data)
        option = HTTPRequest(url, method="POST", body= json_data)
        res = yield AsyncHTTPClient().fetch(option)
        res_time = round((time.time() - start) * 1000, 4)  # 单位ms
        print ("{0}, {1}ms".format(url, res_time))
    except Exception, e:
        print e, url
        raise gen.Return(("ERROR",e))
    if data_type in ('json', 'JSON'):
        raise gen.Return(json.loads(res.body))
    else:
        raise gen.Return(res.body)


if __name__ == '__main__':
    d = {
        "time": time.time(),
        "id": "1919810",
        "file_url":"http://cty.design/verify_dns/baidu_8.txt",
        "file_md5":"1abf74b788108aaa5f3ec0aa21ad399e"
        }
    url = "http://localhost:8999/notify/query/domain_list"
    async_post(url, json=d, data_type="json")

