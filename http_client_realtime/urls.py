#coding=utf-8
"""
系统路由设置
"""
from realtime_handler import DomainNSRealtimeHandler

urls = [
    (r"/domain_ns_realtime/", DomainNSRealtimeHandler),
    # (r"/file/(\w+)", ResultFileHandler),
    # (r'/sec/task_confirm/', sectaskconfirmhandler),
    # (r'/query/task_confirm/', querytaskconfirmhandler),

]
