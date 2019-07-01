# encoding:utf-8

"""
定期更新整个数据库中所有域名的ns记录
"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../')

import threading
import datetime
import hashlib
import time
from Queue import Queue
from threading import Thread
from collections import defaultdict
from resolving_domain_ns_by_tld import get_domain_ns_hierarchical_dns # 获取域名dns
from db_manage.data_base import MySQL
from db_manage.mysql_config import SOURCE_CONFIG_LOCAL as SOURCE_CONFIG
import tldextract
from resolving_domain_ns_by_ns import query_domain_ns_by_ns  # 获取域名dns
from resolving_ip_cname_by_ns import query_ip_cname_by_ns
from Logger import Logger
from task_confirm import TaskConfirm
domain_ns_result = {}   # 存储最终的ns结果
retry_domains = []  # 存储需要进行二次探测的域名及其主域名
thread_num = 50   # 主线程数量
retry_thread_num = 30  # 次级线程数量
update_num = 1000  # 1次更新的数量
queue = Queue()  # 任务队列

lock = threading.Lock()

logger = Logger(file_path='./log/',show_terminal=True)  # 日志配置


class NSubThread(threading.Thread):
    """自定义线程类，用于返回结果"""
    def __init__(self,func,args=()):
        super(NSubThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception,e:
            logger.logger.error('获取线程的结果失败:',str(e))
            return [], 'FALSE'


def read_domains():
    """
    读取域名存储文件，获取要探测的域名，以及提取出主域名
    注意：若是不符合规范的域名，则丢弃
    """
    domains = []
    main_domains = []
    no_fetch_extract = tldextract.TLDExtract(suffix_list_urls=None)

    try:
        db = MySQL(SOURCE_CONFIG)
    except Exception,e:
        logger.logger.error(e)
        return False
    sql = 'select domain from focused_domain'
    db.query(sql)
    domain_query = db.fetch_all_rows()
    db.close()


    for domain in domain_query:
        domain = domain['domain']
        domain_tld = no_fetch_extract(domain)
        tld, reg_domain = domain_tld.suffix, domain_tld.domain  # 提取出顶级域名和主域名部分
        if tld and reg_domain:
            main_domains.append(reg_domain+'.'+tld)
            domains.append(domain)
        else:
            logger.logger.warning('域名%s不符合规范，不进行探测' % domain)

    return domains, main_domains


def insert_domains_db(domains):
    """将域名插入到数据库中"""
    try:
        db = MySQL(SOURCE_CONFIG)
    except Exception,e:
        logger.logger.error(e)
        return False
    for domain in domains:
        sql = 'insert ignore into focused_domain (domain) values ("%s")' % (domain)
        db.insert_no_commit(sql)
    db.commit()
    db.close()
    return True


def extract_domain_tld(domain):
    """
    提取域名的顶级域名
    注意：不符合规范的域名，返回为空
    """
    no_fetch_extract = tldextract.TLDExtract(suffix_list_urls=None)
    domain_tld = no_fetch_extract(domain)
    tld = domain_tld.suffix
    if '.' in tld: # 若是多级顶级域名，则返回最后1级
        return tld.split('.')[-1]
    else:
        return tld


def fetch_tld_ns():
    """
    获取顶级域名的权威服务器（ns）IP地址
    """

    tld_ns = defaultdict(set)
    try:
        db = MySQL(SOURCE_CONFIG)
        sql = 'SELECT tld,server_ipv4 from tld_ns_zone'
        db.query(sql)
        tld_ns_query = db.fetch_all_rows()  # 获取已存储的顶级域名的权威服务器信息
    except Exception, e:
        logger.logger.error("获取顶级域名异常：",e)
        return tld_ns
    db.close()
    for i in tld_ns_query:
        tld = str(i['tld'])
        if i['server_ipv4']:
            ipv4 = str(i['server_ipv4']).split(';')
            for ip in ipv4:
                for p in ip.split(','):
                    if p:
                     tld_ns[tld].add(p)
    return tld_ns


def update_domain_ns_db():
    """添加获取域名的DNS数据"""
    # 解析关键字段信息
    global domain_ns_result
    ns_result = []
    try:
        db = MySQL(SOURCE_CONFIG)
    except:
        logger.logger.error("数据库连接失败")
        return

    for domain in domain_ns_result:
        v = domain_ns_result[domain]
        domain_ns = ','.join(v[0])
        ns_md5 = hashlib.md5(domain_ns).hexdigest()
        tld_ns = ','.join(v[1])
        ns_ns = ','.join(v[2])
        invalid_ns = ','.join(v[3])
        unknown_ns = ','.join(v[4])
        verify_strategy = v[5]
        insert_time = v[6]
        ns_result.append((domain,ns_md5,domain_ns,tld_ns,ns_ns,invalid_ns,unknown_ns,verify_strategy,insert_time,id))

    ns_sql = 'INSERT INTO domain_valid_ns (domain,ns_md5,domain_ns,tld_ns,ns_ns,invalid_ns,unknown_ns,verify_strategy,insert_time,task_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) \
                ON DUPLICATE KEY UPDATE ns_md5 = VALUES (ns_md5),domain_ns=VALUES(domain_ns),tld_ns=VALUES (tld_ns),ns_ns = VALUES (ns_ns),invalid_ns=VALUES (invalid_ns), \
                unknown_ns=VALUES (unknown_ns), verify_strategy=VALUES (verify_strategy),insert_time = VALUES (insert_time),task_id = VALUES (task_id)'  # 存在则更新，不存在则插入

    try:
        db.update_many(ns_sql, ns_result)
    except Exception as e:
        logger.logger.error("更新域名的NS记录失败:" + str(e))

    db.close()


def create_queue(domains, main_domains):
    """
    创建首次探测的任务队列
    """

    for i, d in enumerate(domains):
        queue.put((d,main_domains[i]))


def create_retry_queue(retry_domains):
    """
    创建二次探测的任务队列
    """
    for domain,main_domain in retry_domains:
        queue.put((domain,main_domain))


def obtain_domain_ns_by_tld(domain, tld_ns):
    """
    向顶级域名权威服务器请求域名的NS记录，采用子线程方式，加快探测效率
    :param
    domain:  string，要解析的域名
    tld_ns: dict，顶级域名权威服务器的IP地址集合

    :return
    domain_ns: 域名的权威服务器名称集合
    is_retry: true/false, true表示该域名要再次进行探测，false则不需要

    """
    is_retry = True  # 是否重新获取, 有顶级域名返回ns，或者是域名不存在，都不重新获取
    status = []
    tld = extract_domain_tld(domain)  # 获取要查询域名tld
    if not tld:
        logger.logger.warning("不存在该域名:%s的顶级域名" % domain)
        return []

    tld_ns_set = tld_ns.get(tld)  # 顶级域名的权威服务器IP地址
    if not tld_ns_set:
        logger.logger.warning("不存在该顶级域名:%s的权威服务器" % tld)
        return []

    sub_thread = []  # 线程列表
    domain_ns = []
    for ip in tld_ns_set:
        t = NSubThread(get_domain_ns_hierarchical_dns, args=(domain, True, ip))  # 根据顶级域名权威数量，生成对应的子线程
        sub_thread.append(t)
        t.start()

    for t in sub_thread:
        t.join()
        ns, ns_status = t.get_result()
        status.append(ns_status)
        if ns_status == 'TRUE':
            domain_ns.extend(ns[1])
            is_retry = False  # 若域名存在有效的ns，则不需要再次探测
        elif ns_status == 'NOEXSIT':  # 若域名不存在，也不需要再次探测
            is_retry = False

    return list(set(domain_ns)), is_retry


def obtaining_domain_ns_by_ns(domain,main_domain, tld_domain_ns):
    """
    向域名的权威服务器请求ns，获取域名权威服务器上的的ns记录集合
    :param string domain: 要解析的原始域名
    :param string main_domain: 主域名
    :param list tld_domain_ns: tld解析的域名的ns权威服务器地址名称集合
    :return list domain_ns: 经过验证后的有效域名ns地址集合
    """
    domain_ns = []  # 验证后的有效域名ns集合
    sub_thread = []  # 子线程集合
    tld_domain_valid_ns = []   # 顶级域名权威服务器解析的域名ns结果
    tld_domain_valid_ns_dict = {}  # 记录各个响应的内容结果
    tld_domain_invalid_ns = []   # 顶级域名权威服务器解析的域名ns结果
    ns_domain_invalid_ns = []
    ns_domain_ns = []  # 域名权威服务器解析的域名ns结果
    unknown_ns = []  # 未确定的ns
    # 创建子线程
    for n in tld_domain_ns:
        t = NSubThread(query_domain_ns_by_ns, args=(main_domain, n))
        sub_thread.append(t)
        t.setDaemon(True)
        t.start()

    # 获取域名权威服务器上的ns记录
    for t in sub_thread:
        t.join()
        ns, ns_status, original_ns = t.get_result()
        if ns_status == 'TRUE':
            ns_domain_ns.extend(ns)
            tld_domain_valid_ns.append(original_ns)
            tld_domain_valid_ns_dict[original_ns] = ns
        else:
            tld_domain_invalid_ns.append(original_ns)

    ns_domain_ns = list(set(ns_domain_ns))  # 去重
    if not tld_domain_valid_ns:  # 若无ns，则返回空，停止
        verify_strategy = 1
        is_retry = True
        return domain_ns,tld_domain_ns,ns_domain_ns,list(set(ns_domain_invalid_ns+tld_domain_invalid_ns)),unknown_ns, verify_strategy, is_retry # 无有效的tld_ns,所以重新探测

    ns_domain_del_ns = list(set(ns_domain_ns)-set(tld_domain_invalid_ns))  # 去除域名权威返回的ns中不可以正常解析的地址名称
    is_same = set(tld_domain_valid_ns) == set(ns_domain_del_ns)  # 判断有效两级的有效ns是否相同

    # 相同，则直接返回正确的地址
    if is_same:
        domain_ns = tld_domain_valid_ns  # 域名有效的ns
        verify_strategy = 2
        is_retry = False
        return domain_ns, tld_domain_ns, ns_domain_ns, list(
            set(ns_domain_invalid_ns + tld_domain_invalid_ns)), unknown_ns, verify_strategy, is_retry

    # 不同，进一步分析处理
    intersection_ns = set(tld_domain_valid_ns).intersection(set(ns_domain_del_ns))  # 上下级ns的交集
    # print intersection_ns
    if intersection_ns:  # 交集不为空
        is_retry = False
        domain_ns.extend(intersection_ns)  # 首先，交集ns为部分有效ns
        verify_strategy = 3
        # 对于只存在则域名ns的记录进行判断
        only_ns = list(set(ns_domain_ns).difference(intersection_ns))
        for n in only_ns:
            ns, ns_status, _ = query_domain_ns_by_ns(main_domain, n)  # 向域名的权威ns请求域名的ns
            if ns_status == 'TRUE':  # 可正常解析
                if set(ns).intersection(set(domain_ns)):  # 若与公共ns有交集，则判断为有效ns
                    domain_ns.append(n)
                else:
                    flag = verify_ns_by_ip(domain,n,domain_ns)
                    if flag == 1:
                        domain_ns.append(n)
                    elif flag == 0:
                        ns_domain_invalid_ns.append(n)
                    else:
                        unknown_ns.append(n)

            else:  # 无法正常解析，则为无效ns
                ns_domain_invalid_ns.append(n)

        # 对于只存在在顶级域名权威的ns记录判断
        only_tld = list(set(tld_domain_valid_ns).difference(intersection_ns))
        for n in only_tld:
            ns = tld_domain_valid_ns_dict.get(n)
            if set(ns).intersection(set(domain_ns)):
                domain_ns.append(n)
            else:
                flag = verify_ns_by_ip(domain, n, domain_ns)
                if flag == 1:
                    domain_ns.append(n)
                elif flag == 0:
                    tld_domain_invalid_ns.append(n)
                else:
                    unknown_ns.append(n)

    else:  # 两级获取的ns完全不一样的情况
        verify_strategy = 4
        is_retry = True
        logger.logger.info("域名:%s 两级ns无交集" % domain)
        if ns_domain_del_ns:  # ns不为空
            tld_ip, tld_cname = [], []
            tld_ip_dict, tld_cname_dict = {}, {}
            for n in tld_domain_valid_ns:
                ipv4, cnames, ip_cname_status = query_ip_cname_by_ns(domain,n)
                if ip_cname_status == 'TRUE' and (ipv4 or cnames):
                    tld_ip.extend(ipv4)
                    tld_cname.extend(cnames)
                    tld_ip_dict[n] = ipv4
                    tld_cname_dict[n] = cnames
            ns_ip, ns_cname = [],[]
            ns_ip_dict, ns_cname_dict = {}, {}
            for n in ns_domain_del_ns:
                ipv4, cnames, ip_cname_status = query_ip_cname_by_ns(domain, n)
                if ip_cname_status == 'TRUE' and (ipv4 or cnames):
                    ns_ip.extend(ipv4)
                    ns_cname.extend(cnames)
                    ns_ip_dict[n] = ipv4
                    ns_cname_dict[n] = cnames

            if not (ns_ip or ns_cname) and (tld_ip or tld_cname):  # ns返回的ip为空，tld返回的不为空
                for n in tld_ip_dict:
                    domain_ns.append(n)
            elif (ns_ip or ns_cname) and not (tld_ip or tld_cname): # ns返回ip不为空，tld返回为空
                for n in ns_ip_dict:
                    domain_ns.append(n)
            elif (ns_ip or ns_cname) and (tld_ip or tld_cname):  # 都不为空

                for n in tld_ip_dict:

                    if set(tld_ip_dict[n]).intersection(set(ns_ip)) or set(tld_cname_dict[n]).intersection(set(ns_cname)):
                        domain_ns.append(n)
                    else:
                        unknown_ns.append(n)
                        # print "无操作，修改程序"

                for n in ns_ip_dict:
                    if set(ns_ip_dict[n]).intersection(set(tld_ip)) or set(ns_cname_dict[n]).intersection(
                            set(tld_cname)):
                        domain_ns.append(n)
                    else:
                        # print "无操作，修改程序"
                        unknown_ns.append(n)

        else:  # ns为空
            for n in tld_domain_valid_ns:  # 返回IP或cname
                ipv4, cnames, ip_cname_status = query_ip_cname_by_ns(domain, n)
                if ip_cname_status == 'TRUE' and (ipv4 or cnames):
                    domain_ns.append(n)
                else:
                    tld_domain_invalid_ns.append(n)

    domain_ns.sort()
    invalid_ns = list(set(ns_domain_invalid_ns + tld_domain_invalid_ns))
    return domain_ns, tld_domain_ns, ns_domain_ns, invalid_ns, unknown_ns, verify_strategy,is_retry


def master_control(tld_ns,file_name):
    """主线程控制"""
    global domain_ns_result
    global retry_domains
    while queue.qsize():
        logger.logger.info('存活线程: %s, 剩余任务: %s' % (threading.activeCount(),queue.qsize()))
        domain, main_domain = queue.get()
        ns_by_tld, is_retry = obtain_domain_ns_by_tld(main_domain, tld_ns)  # 通过顶级域名权威获取域名的ns

        # print ns_by_tld, is_retry
        if ns_by_tld:
            domain_ns,tld_domain_ns,ns_domain_ns,invalid_ns, unknown_ns, verify_strategy,is_retry = obtaining_domain_ns_by_ns(domain,main_domain, ns_by_tld)
            if is_retry and not domain_ns:  # 重试为true，并且无有效ns时，则重试
                retry_domains.append((domain, main_domain))
            # ns_md5 = hashlib.md5(domain_ns).hexdigest()

        else:
            if is_retry:
                retry_domains.append((domain, main_domain))
            domain_ns, tld_domain_ns, ns_domain_ns, invalid_ns, unknown_ns, verify_strategy = [], [], [], [], [], 0   # verify_strategy=0，表示没有获取tld的内容

        insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lock.acquire()
        domain_ns_result[domain] = (domain_ns, tld_domain_ns, ns_domain_ns, invalid_ns, unknown_ns, verify_strategy, insert_time)
        print len(domain_ns_result)
        if len(domain_ns_result) == update_num:
            save_to_file(file_name)
            update_domain_ns_db()
            domain_ns_result = {}
        lock.release()
        # time.sleep(1)
        queue.task_done()


def verify_ns_by_ip(domain, ns, intersection_ns):
    """
    通过ip地址验证是否为有效ns
    :param string domain:  要验证的domain
    :param string ns:  要验证的ns
    :param list intersection_ns: 已经确认的有效ns集合
    :return: int flag  : 1/0/-1, 1表示有效，0表示无效, -1表示未知
    """
    ipv4, cnames, ip_cname_status = query_ip_cname_by_ns(domain, ns)
    verify_result = []

    if ip_cname_status == 'TRUE' and (ipv4 or cnames):
        for n in intersection_ns:
            n_ipv4, n_cnames, n_ip_cname_status = query_ip_cname_by_ns(domain, n)
            if n_ip_cname_status == 'TRUE':
                if set(ipv4).intersection(set(n_ipv4)) or set(cnames).intersection(set(n_cnames)):
                    verify_result.append(1)
                    break  # 出现交集，则停止
                else:
                    verify_result.append(-1)  # 有ip地址，但是无交集
            else:
                verify_result.append(0)
    else:
        verify_result.append(0)

    if 1 in verify_result:
        return 1
    elif -1 in verify_result:
        return -1
    else:
        return 0


def save_to_file(file_name):
    """
    将有效的ns存入到本地文件中
    :param domain_ns:
    :param id:
    :return:
    """
    global domain_ns_result
    path = '../domain_data/'
    try:
        fp = open(path+file_name,'a')

        for domain in domain_ns_result:
            domain_ns = domain_ns_result[domain][0]
            domain_ns = ','.join(domain_ns)
            if domain_ns:
                fp.write(domain+'\t'+'NS'+'\t'+domain_ns+'\n')
        fp.close()
        return True
    except Exception, e:
        print e
        return False


def first_obtaining_domain_ns(domains,main_domains,tld_ns,file_name):
    """
    第一次获取域名的有效ns记录
    """
    create_queue(domains, main_domains)
    worker_list = []
    for q in range(thread_num):  # 开始任务
        worker = Thread(target=master_control,args=(tld_ns,file_name))
        worker.setDaemon(True)
        worker.start()
        worker_list.append(worker)

    queue.join()


def retry_obtaining_domain_ns(tld_ns,file_name):
    """
    再次探测第一次未成功获取ns的域名
    """
    global retry_domains
    if not retry_domains:
        return
    print '重新探测的域名数量：',len(retry_domains),retry_domains
    create_retry_queue(retry_domains)
    worker_list = []
    for q in range(retry_thread_num):  # 开始任务
        worker = Thread(target=master_control, args=(tld_ns,file_name))
        worker.setDaemon(True)
        worker.start()
        worker_list.append(worker)

    queue.join()


def obtaining_domain_ns():
    """主函数"""
    logger.logger.info('开始定期解析域名的NS记录,线程数量为:%s' % thread_num)
    file_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = 'domain_periodic_'+file_time
    tld_ns = fetch_tld_ns()
    domains, main_domains = read_domains()

    first_obtaining_domain_ns(domains, main_domains, tld_ns,file_name)

    retry_obtaining_domain_ns(tld_ns,file_name)

    if domain_ns_result:
        # 更新数据库和文件，也使用两个子线程完成
        update_domain_ns_db()
        save_to_file(file_name)

    for _ in range(3):  # 重试三次

        flag = TaskConfirm(file_name).sec_post()  # 发送探测完成消息
        if isinstance(flag, bool): # 成功则停止发送
            break
        else:
            logger.logger.error('实时探测域名有效NS，确认探测失败：%s' % flag)

    logger.logger.info('结束定期解析域名的NS记录,线程数量为:%s' % thread_num)


def main():
    # obtaining_domain_ns()
    while True:
        obtaining_domain_ns()
        time.sleep(60)


if __name__ == '__main__':
    main()