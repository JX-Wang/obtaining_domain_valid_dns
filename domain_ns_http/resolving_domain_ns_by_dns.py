# encoding:utf-8
"""
利用DNS递归服务器，获取域名的NS服务器
"""
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


def obtaining_domain_ns_name(domain, recursion_server= '47.94.47.91', retry_times=3, timeout=3):
    """
    根据域名，获取其顶级域名的权威服务器地址
    root_ip 数据类型为list
    """

    main_domain = extract_main_domain(domain)
    ns = []
    ns_status = 'FALSE'
    if not main_domain:  # 主域名不存在
        return ns, ns_status

    resolver = dns.resolver.Resolver(configure=False)
    resolver.timeout, resolver.lifetime = timeout, timeout
    resolver.nameservers = recursion_server

    for _ in range(retry_times):  # 尝试3次
        try:
            dns_resp = dns.resolver.query(main_domain, 'NS')
            for r in dns_resp.response.answer:
                r = str(r.to_text())
                for i in r.split('\n'):
                    i = i.split(' ')
                    ns_domain, rc_type = i[0], i[3]
                    if ns_domain[:-1] != main_domain:
                        continue
                    if rc_type == 'NS':
                        ns.append(str(i[4][:-1]).lower())
            ns_status = 'TRUE'
            ns.sort()
            break
        except dns.resolver.NoAnswer:
            ns_status = 'NO ANSWERS'
        except dns.resolver.NXDOMAIN:
            ns_status = "NXDOMAIN"  # 尝试一次
            break
        except dns.resolver.NoNameservers:
            ns_status = 'NO NAMESERVERS'  # 尝试一次
            break
        except dns.resolver.Timeout:
            ns_status = 'TIMEOUT'
        except:
            ns_status = 'UNEXPECTED ERRORS'

    return ns, ns_status


if __name__ == '__main__':
    print obtaining_domain_ns_name('baidu.com', '47.94.47.91')