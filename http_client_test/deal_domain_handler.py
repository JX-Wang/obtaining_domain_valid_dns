# encoding:utf-8

import tornado.ioloop
import tornado.web
import requests
import hashlib
import time
import json
import os


class ResultFileHandler(tornado.web.RequestHandler):
    '''
	根据文件名，web服务器返回文件
	'''

    def get(self, filename):
        print('i download file handler : ', filename)
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + filename)
        with open("./verified_domain/" + filename, "r") as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                self.write(data)
        # 记得要finish
        self.finish()


class DomainFileHandler(tornado.web.RequestHandler):
    """
    根据文件名，web服务器返回文件
    """

    def get(self, file_name):
        print('i download file handler : ', file_name)
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + file_name)
        with open("./test/" + file_name, "r") as f:
            while True:
                data = f.read(1024)
                print data
                if not data:
                    break
                self.write(data)

        # 记得要finish
        self.finish()



class RecvDomainRequestHandler(tornado.web.RequestHandler):
    """
    接收来自对方服务器的域名实时/非实时验证请求
    """

    def post(self, request_type):
        code = 1
        print request_type
        # remote_ip = self.request.remote_ip  # 访问的远程地址
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        print param

        self.write({'time':'aaa','code':1})
        return

        file_url = param['file_url']
        id = param['id']
        time = param['time']
        file_md5 = param['file_md5']
        original_file_name = file_url.split('/')[-1]  # 远程文件的名称
        local_file_name = original_file_name + '_' + str(id)  # 保存到本地的文件名称
        print local_file_name
        print file_url
        print type(file_url)
        domain_data = requests.get(file_url)
        print domain_data
        domain_data = requests.get(file_url).text  # 获取内容 todo 增加异常处理功能
        print domain_data
        h = hashlib.md5(domain_data.encode("utf-8")).hexdigest()

        with open("./unverified_domain_data/" + local_file_name, "w") as f:  # 将要验证的域名数据保存到本地
            f.writelines(domain_data)

        if h != param['file_md5']:
            code = 2

        respond = {
            "time": param['time'],
            "code": code
        }
        self.write(respond)  # http请求的响应结果

        if code == 2:
            return
        # deal_with_domains_query(id, local_file_name)