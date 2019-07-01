# encoding:utf-8

import schedule
import time

# 获取根服务器和顶级域名的权威服务器信息
from download_root_zone import root_zone_download
from obtaining_tlds_ns_from_zone import get_tld_ns_by_zone


if __name__ == '__main__':

    # 获取顶级域名权威信息
    schedule.every(12).hours.do(root_zone_download) # 下载zone文件
    schedule.every(12).day.do(get_tld_ns_by_zone) # 提取zone文件内容

    while True:
        schedule.run_pending()
        time.sleep(5)