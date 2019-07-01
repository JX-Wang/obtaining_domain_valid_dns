# encoding: utf-8
"""
读取系统配置参数
"""

import ConfigParser


def read_server(file_name):
    """读取主节点信息"""
    cf = ConfigParser.ConfigParser()
    cf.read(file_name)
    ip = cf.get("server", "ip")
    port = cf.getint("server","port")
    return ip, port


def read_client_realtime(file_name):
    """读取实时探测主机信息"""
    cf = ConfigParser.ConfigParser()
    cf.read(file_name)
    ip = cf.get("http_client_realtime", "ip")
    port = cf.getint("http_client_realtime","port")
    return ip, port


def read_client_periodic(file_name):
    """读取定时探测主机信息"""
    cf = ConfigParser.ConfigParser()
    cf.read(file_name)
    ip = cf.get("http_client_periodic", "ip")
    port = cf.getint("http_client_periodic","port")
    return ip, port


def read_remote_ip(file_name):
    """读取远程主机信息"""
    cf = ConfigParser.ConfigParser()
    cf.read(file_name)
    ip = cf.get("remote_ip", "ip")
    port = cf.getint("remote_ip","port")
    return ip, port

if __name__ == '__main__':
    print read_server()
    print read_client_realtime()
    print read_client_periodic()
