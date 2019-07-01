#encoding:utf-8
import requests
import time
import os
import hashlib
#模拟对方服务器发来的请求，请求方式为POST，请求参数为BODY内的JSON
url = "http://10.245.146.122:8999/notify/sec/domain_list"

def get_md5_01(file_path):
  md5 = None
  if os.path.isfile(file_path):
    f = open(file_path,'rb')
    md5_obj = hashlib.md5()
    md5_obj.update(f.read())
    hash_code = md5_obj.hexdigest()
    f.close()
    md5 = str(hash_code).lower()
  return md5

md5 = get_md5_01('./test/a')
print md5
d = {
		"time": time.time(),
		"id":"11011111111",
		"file_url":"http://10.236.27.233:9000/test/domain/a",
		"file_md5":md5
	}

a = requests.post(url,json = d)
print (a.text)
