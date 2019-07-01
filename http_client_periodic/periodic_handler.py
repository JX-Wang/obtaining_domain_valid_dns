# encoding:utf-8

import tornado.web
import json
import os
from Logger import Logger

logger = Logger(file_path='./query_log/',show_terminal=True)  # 日志配置


class DomainNSPeriodicHandler(tornado.web.RequestHandler):
    """
    接收来自对方服务器的域名，并获取其域名有效的NS服务器地址
    """

    def post(self):
        param = self.request.body.decode('utf-8')
        print param
        print param
        param = json.loads(param)
        domains = param['domains']
        # id = param['id']
        file_name = param['file_name']

        try:
            fp = open("./unverified_domain_data/" + file_name, "w")
            fp.writelines(domains)
            self.write('OK')  # http请求的响应结果
        except Exception, e:
            self.write('ERROR')  # http请求的响应结果
            logger.logger.error('写入失败:'+str(e))
            return

        self.deal_with_domains_periodic(file_name)


    def deal_with_domains_periodic(self, file_name):
        """
        对方请求的实时任务
        参数：
        request_id:   		请求的唯一ID
        file_name:			域名列表文件的读入路径
        例如：
            nohup python dns_detect/main.py query 34567 unverified/34567 verified/
        """
        os.system("nohup python ../domain_ns_http/insert_domain_to_db.py %s  & > query_log/task_%s.out" % (
            file_name,file_name))