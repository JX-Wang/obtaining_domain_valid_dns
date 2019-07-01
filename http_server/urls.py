#coding=utf-8
"""
系统路由设置
"""
from manage_data_handler import RecvDomainRequestHandler,TaskConfirmHandler,RespDomainResultHandler

urls = [
    (r"/notify/(\w+)/domain_list", RecvDomainRequestHandler),  # 接收任务请求处理
    (r'/task_confirm/', TaskConfirmHandler),   # 任务完成确认
    (r'/file/(\w+)', RespDomainResultHandler),  # 任务完成响应

]
