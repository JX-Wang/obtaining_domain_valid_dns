# encoding:utf-8
"""
主节点控制功能
"""

import tornado.web
import hashlib
import time
import json
from system_parameter import *
from Logger import Logger
from async_fetch import async_fetch,async_post
from tornado import gen

logger = Logger(file_path='./query_log/',show_terminal=True)  # 日志配置


class RespDomainResultHandler(tornado.web.RequestHandler):
    """
    根据文件名，服务器返回请求的文件内容
    """

    def get(self, file_name):
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + file_name)
        with open("./verified_domain_data/" + file_name, "r") as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                self.write(data)

        self.finish()  # 记得要finish


class TaskConfirmHandler(tornado.web.RequestHandler):
    """
    接收完成探测请求，以及告知对方服务器完成的任务id和文件的url连接
    """

    def save_file(self, domain_ns, file_name):
        """
        根据文件名称，将数据保存到本地
        """
        path = './verified_domain_data/'
        with open(path+file_name,'w') as fp:
            fp.write(domain_ns)

    @gen.coroutine
    def post(self):
        """
        接收探测任务完成的post请求，并将结果保存本地文件后，将文件链接地址告知对方服务器
        """
        param = self.request.body.decode("utf-8")
        param = json.loads(param)
        print param
        print param
        file_name = param['file_name']  # 文件名称
        task_id = param['task_id']   # 任务id
        domain_ns = param['domain_ns']  # 域名ns的数据
        task_type = param['task_type']  # 任务类型，sec/query
        self.save_file(domain_ns, file_name)   # 将域名ns数据保存到本地

        file_md5 = hashlib.md5(domain_ns.encode("utf-8")).hexdigest()  # 生成md5值
        ip, port = read_server('../system.conf')  # 读取主服务器ip地址
        remote_ip, remote_port = read_remote_ip('../system.conf')  # 远程的IP地址
        remote_url = "http://{ip}:{port}/notify/{task_type}/result_list".format(ip=remote_ip, port=str(remote_port), task_type=task_type)  # 远程访问的地址
        file_url = "http://{ip}:{port}/file/{file_name}".format(ip=ip, port=str(port), file_name=file_name)  # 文件存储url
        post_body = {
            "id": task_id,
            "time": time.time(),
            "file_url": file_url,
            "file_md5": file_md5
        }
        print remote_url
        for i in range(3):  # 最多重试3次
            respond = yield async_post(remote_url, 
                                       json_data=post_body, 
                                       data_type="json")
            if "ERROR" in respond:
                excpetion = respond[1]
                logger.logger.error('向对方发送域名ns结果文件失败:'+str(excpetion))
                return
            resp_code = respond['code']
            if resp_code == 1:
                logger.logger.info('对方接收域名ns结果文件成功')
                break                
            else:
                logger.logger.warning('对方接收域名ns结果文件失败，次数：'+str(i)+'/3')

            '''
            try:
                response = requests.post(url=remote_url, json=post_body)
            except requests.exceptions.RequestException, e:
                logger.logger.error('向对方发送域名ns结果文件失败:'+str(e))
                return
            resp_code = json.loads(response.content)['code']
            if resp_code == 1:  # 1为对方接收成功
                logger.logger.info('对方接收域名ns结果文件成功')
                break
            else:
                logger.logger.warning('对方接收域名ns结果文件失败，次数：'+str(i)+'/3')
            '''


class RecvDomainRequestHandler(tornado.web.RequestHandler):
    """
    接收来自对方服务器的域名实时/非实时验证请求
    """
    @gen.coroutine
    def post(self, task_type):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        try:
            file_url = param['file_url']
            task_id = param['id']
            request_time = param['time']
            file_md5 = param['file_md5']
        except Exception, e:  # 解析失败
            logger.logger.error('请求内容不符合要求：'+str(e))
            self.write({'time': time.time(), 'code': 2})  # 请求内容不符合要求
            self.finish()
            return

        domain_data = yield async_fetch(file_url, "text")
        if "ERROR" in domain_data:
            exception = str(domain_data[1])
            logger.logger.error('获取要探测的域名失败：' + exception)
            self.write({'time': request_time, 'code': 2})  # 获取失败
            self.finish()
            return

        '''
        try:
            domain_data = requests.get(file_url).content  # 获取要探测的域名数据
        except Exception, e:  # 获取域名的数据失败，
            logger.logger.error('获取要探测的域名失败：'+str(e))
            self.write({'time': request_time, 'code': 2})  # 获取失败
            self.finish()
            return
        '''

        domain_md5 = hashlib.md5(domain_data.encode("utf-8")).hexdigest()  # 数据自身的md5值

        # 校验数据是否一致
        if domain_md5 == file_md5:
            if task_type in ('sec', 'query'):
                self.write({'time': request_time, 'code': 1})  # 校验一致
                self.finish()
            else:
                logger.logger.error('错误的查询类型：' + str(task_type))
                self.write({'time': request_time, 'code': 2})
                self.finish()
                return
        else:
            logger.logger.error('域名数据校验不一致')
            self.write({'time': request_time, 'code': 2})  # 校验不一致
            self.finish()
            return

        original_file_name = file_url.split('/')[-1]  # 远程文件的名称
        local_file_name = original_file_name + '_' + task_type + '_' + str(task_id)  # 保存到本地的文件名称
        with open("./unverified_domain_data/" + local_file_name, "w") as f:  # 将要验证的域名数据保存到本地
            f.writelines(domain_data)

        if task_type == 'sec':
            periodic_domain_request(domain_data, task_id, local_file_name)  # 执行定时查询节点
        elif task_type == 'query':
            query_domain_request(domain_data, task_id, local_file_name)  # 执行实时查询节点


@gen.coroutine
def query_domain_request(domains, task_id, file_name):
    """
    将需要实时查询的域名传递给实时查询http_client_realtime
    """
    query_ip, port = read_client_realtime('../system.conf')  # 获取实时探测点的ip和端口
    url = 'http://' + query_ip + ':' + str(port)+'/domain_ns_realtime/'
    request_data = {
        'domains': domains,
        'id': task_id,
        'file_name': file_name
    }

    for i in range(3):
        respond = yield async_post(url, json_data=request_data, data_type="str")
        if respond == 'OK':
            break
        elif "ERROR" in respond:
            excpetion = respond[1]
            logger.logger.error('向实时查询节点发送域名数据失败%s/3' % str(i))

        '''
        try:

            respond = requests.post(url, json=request_data, timeout=5)
            if respond.text == 'OK':
                break
            logger.logger.error('向实时查询节点发送域名数据失败%s/3' % str(i))
        except requests.exceptions.RequestException, e:
            logger.logger.error('实时节点连接失败:' + str(e))
        '''

@gen.coroutine
def periodic_domain_request(domains, task_id, file_name):
    """
    将需要实时查询的域名传递给定时查询http_client_sec
    """
    periodic_ip, port = read_client_periodic('../system.conf')  # 获取ip地址和端口号
    url = 'http://' + periodic_ip + ':' + str(port) +'/domain_ns_periodic/'
    request_data = {
        'domains': domains,
        'id': task_id,
        'file_name': file_name
    }

    for i in range(3):
        respond = yield async_post(url, json_data=request_data, data_type="str")
        if respond == 'OK':
            break
        elif "ERROR" in respond:
            excpetion = respond[1]
            logger.logger.error('向定时查询节点发送域名数据失败%s/3' % str(i))

        '''
        try:
            respond = requests.post(url, json=request_data, timeout=5)
            if respond.text == 'OK':
                break
            logger.logger.error('向定时查询节点发送域名数据失败%s/3' % str(i))
        except requests.exceptions.RequestException, e:
            logger.logger.error('定时节点连接失败:' + str(e))
        '''