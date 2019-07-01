#coding=utf-8
"""
系统路由设置
"""
from periodic_handler import DomainNSPeriodicHandler

urls = [
    (r"/domain_ns_periodic/", DomainNSPeriodicHandler),
    # (r"/file/(\w+)", ResultFileHandler),
    # (r'/sec/task_confirm/', sectaskconfirmhandler),
    # (r'/query/task_confirm/', querytaskconfirmhandler),

]
