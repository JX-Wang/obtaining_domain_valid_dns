# encoding:utf-8

import tornado.web
import json
import os
from Logger import Logger

logger = Logger(file_path='./query_log/',show_terminal=True)  # 日志配置


class DomainNSRealtimeHandler(tornado.web.RequestHandler):
    """
    接收来自对方服务器的域名，并获取其域名有效的NS服务器地址
    """

    def post(self):
        param = self.request.body.decode('utf-8')
        print param
        param = json.loads(param)
        domains = param['domains']  # 内部信息可以相信
        id = param['id']
        file_name = param['file_name']
        try:
            fp = open("./unverified_domain_data/" + file_name, "w")
            fp.writelines(domains)
            self.write('OK')  # http请求的响应结果
        except Exception, e:
            self.write('ERROR')  # http请求的响应结果
            logger.logger.error('写入失败:'+str(e))
            return

        self.deal_with_domains_query(file_name, id)

    def deal_with_domains_query(self,file_name, request_id):
        """
        对方请求的实时任务
        参数：
        request_id:   		请求的唯一ID
        file_name:			域名列表文件的读入路径
        例如：
            nohup python dns_detect/main.py query 34567 unverified/34567 verified/
        """
        print file_name, request_id
        os.system("nohup python ../domain_ns_http/obtaining_domain_ns_realtime.py %s %s & > query_log/task_%s.out" % (
            file_name, request_id, request_id))