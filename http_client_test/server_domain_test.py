#!/usr/bin/python
# coding=utf-8
"""
系统服务器启动
"""
import tornado.ioloop
import tornado.httpserver
from tornado.options import define, options
from urls import urls
import tornado.web

define("port", default=9000, help="run on the given port", type=int)

SETTINGS = dict(
    debug = True, # 调试模式，部署时为false
)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = urls
        settings = SETTINGS
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer( Application() )
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
