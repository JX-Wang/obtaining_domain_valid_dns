#encoding:utf-8
"""
通过向各个层次的权威NS地址查询，获取域名的NS记录。
可以配置为在线和离线查询
目前只支持域名是主域名
"""

import dns
import random
import dns.name
import dns.query
import dns.resolver

import tldextract


def extract_main_domain(domain):
    """提取主域名"""
    no_fetch_extract = tldextract.TLDExtract(suffix_list_urls=None)
    domain_tld = no_fetch_extract(domain)
    main_domain = ""
    if domain_tld.suffix:
        if domain_tld.domain:
            main_domain = domain_tld.domain+'.'+domain_tld.suffix

    return main_domain


def get_authoritative_nameserver(domain, default_dns='47.94.47.91', offline=False, tld_server = None, retry_times=3):
    """
    通过向各个权威NS发送查询请求，获取域名的NS记录
    :param domain: 要查询的域名，目前只支持注册域名的权威查询
    :param offline: 是否离线查询，在线表示顶级域名的权威通过配置好的递归服务器获取；离线表示顶级域名的权威地址由输入确定
    :param tld_server: 若为离线查询，则tld_server为指定的顶级域名权威IP地址，务必为IP
    :param retry_times: 重试次数
    :return: rrset ，域名的NS记录
    """

    if offline and not tld_server.strip(): # 若使用离线数据，但顶级域名权威为空，则输出错误
        return '顶级域名权威地址IP不能为空'

    n = dns.name.from_text(domain)
    if len(n) == 1:
        return "域名的顶级域名不存在"
    depth = 2
    rrset = None
    nameserver = default_dns  # 初始化dns
    default = dns.resolver.Resolver(configure=True) # 自定义本地递归服务器
    default.nameservers = [nameserver, '1.2.4.8', '114.114.114.114']

    while True:
        s = n.split(depth)
        last = s[0].to_unicode() == u'@'
        sub = s[1]
        if len(sub) == 2:  # 若为顶级域名，且为offline，则使用指定的顶级域名权威查询域名的ns
            if offline:
                nameserver = tld_server
                depth += 1
                continue
        query = dns.message.make_query(sub, dns.rdatatype.NS, use_edns=True) # 增加使用edns
        try:
            response = dns.query.udp(query, nameserver, timeout=3)
        except:
            if retry_times:
                retry_times = retry_times - 1
                if not rrset:
                    continue
                # 重新选择一个ns地址
                rrset_cnt = len(rrset)  # rrset的大小
                random_serial = random.randint(0, rrset_cnt - 1)
                rr = rrset[random_serial]  # 随机选择一条记录
                try:
                    authority = rr.target
                except Exception,e:
                    return str(e)
                # print '%s is dddauthoritative for %s' % (authority, sub)
                try:
                    nameserver = default.query(authority).rrset[0].to_text()
                except:
                    try:
                        nameserver = default.query(authority).rrset[0].to_text()
                    except:
                        return "resovling nameserver failed"
                continue
            else:
                return 'TIMEOUT'

        retry_times = 3  # 若成功，则重新初始化超时重试次数
        rcode = response.rcode()
        if rcode != dns.rcode.NOERROR:
            if rcode == dns.rcode.NXDOMAIN:
                # print  '%s does not exist.' % sub
                return 'NOEXSIT'
            else:
                return 'Error %s' % dns.rcode.to_text(rcode)

        if len(response.authority) > 0:
            rrset = response.authority[0]
        else:
            rrset = response.answer[0]
        if last:
            return rrset

        rrset_cnt = len(rrset) # rrset的大小
        random_serial = random.randint(0, rrset_cnt-1)  # 根据长度，随机选择一个序号
        rr = rrset[random_serial]  # 随机选择一条记录
        if rr.rdtype == dns.rdatatype.SOA:
            # print 'Same server is authoritative for %s' % sub
            pass
        else:
            try:
                authority = rr.target
            except:
                return 'authority soa target error'
            # print '%s is authoritative for %s' % (authority, sub)
            try:
                nameserver = default.query(authority).rrset[0].to_text()
            except:
                try:
                    nameserver = default.query(authority).rrset[0].to_text()
                except:
                    return "resovling nameserver failed"
        depth += 1


def parse_rc_ns(rrset):
    """解析出域名的NS集合"""
    ns = []
    domain = ""
    r = str(rrset.to_text())
    for i in r.split('\n'):
        i = i.split(' ')
        rc_type, rc_ttl = i[3], i[1]
        if rc_type == 'NS':
            ns.append((i[4][:-1]).lower())
            domain = i[0][:-1]
    ns.sort()
    return domain, ns


def get_domain_ns_hierarchical_dns(domain,offline = False, tld_server = None,default_dns='47.94.47.91'):
    """按照DNS的分布层级，获取域名NS记录"""
    main_domain = extract_main_domain(domain) # 获取注册域名
    if not main_domain:
        return [domain, []], 'NOEXIST'
    rrset = get_authoritative_nameserver(main_domain,default_dns,offline,tld_server)
    if isinstance(rrset, dns.rrset.RRset):
        domain, ns = parse_rc_ns(rrset)
        if domain:
            return [domain, ns], 'TRUE'
        else:
            return [domain, []], 'FALSE'
    else:
        print '域名: %s, 异常原因：%s' % (domain, rrset)
        return [domain, []], rrset


if __name__ == '__main__':
    domain = 'zzzxhb.top'
    print get_domain_ns_hierarchical_dns(domain,offline=True, tld_server='192.55.83.30')  #offline模式
    print get_domain_ns_hierarchical_dns(domain) # online模式