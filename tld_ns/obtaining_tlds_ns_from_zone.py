#encoding:utf-8
"""
将root zone文件中的根和顶级域名的权威信息提取出来，然后存入数据库中
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../')

import re
import os
import time
from db_manage.data_base import MySQL
from db_manage.mysql_config import SOURCE_CONFIG_LOCAL as SOURCE_CONFIG
from extract_tlds_from_zone import extract_all_tlds

from Logger import Logger

logger = Logger(file_path='./log',show_terminal=True)


def is_file_open(filename):
    """判断文件是否打开"""
    p = os.popen("lsof -w %s" % filename)
    # lsof找到打开的文件时有输出
    content = p.read()
    p.close()
    # 通过是否有输出，判断文件是否打开
    return bool(len(content))


def extract_tld_ns(zone_data, tld):
    """提取顶级域名的权威服务器名称"""
    tld_ns = []
    name = tld.strip() + ".\s*\d+\tIN\tNS\t(.*)."
    for x in zone_data:
        new_x = x.splitlines()  #splitlines是将传入的字符串去除'\n'之后以数组的形式传出，而不是字符串形式
        match_name = re.match(name, new_x[0], re.IGNORECASE)
        if match_name:
            tld_ns.append(match_name.group(1))
    return tld_ns


def extract_ns_ipv4(zone_data, ns):
    """提取IPv4地址"""
    ipv4=ns+".\s*\d+\tIN\tA\t(.*)"
    ns_ipv4 = []
    for y in zone_data:
        new_y = y.splitlines()
        match_ipv4 = re.match(ipv4,new_y[0], re.IGNORECASE)
        if match_ipv4:
            ns_ipv4.append(match_ipv4.group(1))
    return ','.join(ns_ipv4)


def extract_ns_ipv6(zone_data,ns):
    """提取IPv6地址"""
    ipv6 = ns+".\s*\d+\tIN\tAAAA\t(.*)"
    ns_ipv6 = []
    for z in zone_data:
        new_z=z.splitlines()
        match_ipv6 = re.match(ipv6, new_z[0], re.IGNORECASE)
        if match_ipv6:
            ns_ipv6.append(match_ipv6.group(1))
    return ','.join(ns_ipv6)


def get_tld_ns_ip(tld, zone_data):
    """
    在root zone文件中获取顶级域名的权威服务器名称、IPv4地址和IPv6地址
    """
    ns_ipv4, ns_ipv6 = [], []
    tld_ns = extract_tld_ns(zone_data, tld)
    tld_ns.sort()
    for ns in tld_ns:
        ns_ipv4.append(extract_ns_ipv4(zone_data, ns))
        ns_ipv6.append(extract_ns_ipv6(zone_data, ns))

    return tld_ns, ns_ipv4, ns_ipv6


def read_root_zone():
    """读取根区文件"""
    file_path = './root_zone_data/root.zone'

    while 1:  # 判断文件是否处于打开状态
        if is_file_open(file_path):
            # sys.stdout.write("\r文件处于编辑状态，等待文件完成编辑中...")
            logger.logger.warning('文件处于编辑状态，等待文件完成编辑中...')
            # sys.stdout.flush()
            time.sleep(10)
        else:
            break
    try:
        fp = open(file_path, 'r')
    except Exception as e:
        logger.logger.error(e)
        return []
    zone_data = fp.readlines()
    fp.close()
    return zone_data


def insert_tld_ns_db(db,tld_result):
    """更新数据到数据库中"""

    sql = 'INSERT INTO tld_ns_zone (tld,server_name,server_ipv4,server_ipv6) VALUES (%s,%s,%s,%s) \
            ON DUPLICATE KEY UPDATE server_name=values (server_name),server_ipv4 =values (server_ipv4),server_ipv6=VALUES (server_ipv6) '

    db.update_many(sql,tld_result)


def insert_root_ns_db(db,root_ns,root_a, root_aaaa):
    """将根服务器信息存入数据库中"""
    for i,n in enumerate(root_ns):
        ns_name = str(n)
        ipv4 = str(root_a[i])
        ipv6 = str(root_aaaa[i])
        sql = 'INSERT INTO root_server (server_name,server_ipv4,server_ipv6) VALUES ("%s","%s","%s") \
                    ON DUPLICATE KEY UPDATE server_ipv4 ="%s",server_ipv6="%s" '
        db.update(sql % (ns_name, ipv4, ipv6, ipv4, ipv6))


def get_tld_ns_by_zone(is_integrity=False):
    """获取指定顶级域名的权威和IP地址"""

    logger.logger.info('开始从根区文件中提取根和顶级域名的权威信息')
    zone_data = read_root_zone()
    if len(zone_data) <= 21000: # 根据完整的zone的大小，如果小于某阈值，则判断其不完整
        logger.logger.warning('Root Zone文件较小，请检查是否完整后，重新运行')
        if not is_integrity:  # 若完整，则运行
            return

    try:
        db = MySQL(SOURCE_CONFIG)
    except:
        logger.logger.error("数据库异常：获取域名失败")
        return

    # 从根区文件中获取顶级域名的权威信息
    tlds = extract_all_tlds()
    tld_result = []
    if tlds and zone_data:
        for tld in tlds:  # 对于每个tld关键字 进行文档匹配
            tld_ns, ns_ipv4, ns_ipv6 = get_tld_ns_ip(tld, zone_data)
            tld_ns = ';'.join(tld_ns)
            ns_ipv4 = ';'.join(ns_ipv4)
            ns_ipv6 = ';'.join(ns_ipv6)
            tld_result.append((tld, tld_ns, ns_ipv4, ns_ipv6))

    insert_tld_ns_db(db, tld_result)
    root = '.'  # 从根区文件中获取根域名服务器的权威信息
    root_ns, root_ipv4, root_ipv6 = get_tld_ns_ip(root, zone_data)
    insert_root_ns_db(db, root_ns, root_ipv4, root_ipv6)
    db.close()
    logger.logger.info('结束从根区文件中提取根和顶级域名的权威信息')


if __name__ == '__main__':
    get_tld_ns_by_zone()