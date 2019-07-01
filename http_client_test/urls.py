#coding=utf-8
"""
系统路由设置
"""
from deal_domain_handler import DomainFileHandler,RecvDomainRequestHandler

urls = [
    (r'/test/domain/(\w+)', DomainFileHandler),  # 测试
    (r"/notify/(\w+)/result_list", RecvDomainRequestHandler),
    # (r"/file/(\w+)", ResultFileHandler),
    # (r'/sec/task_confirm/', sectaskconfirmhandler),
    # (r'/query/task_confirm/', querytaskconfirmhandler),

]
