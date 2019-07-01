# 采集域名有效的DNS记录（获取和验证）
> 目前只支持域名的NS记录

## 目录

- [核心代码结构](#核心代码结构)
- [子系统简介](#子系统简介)
- [子系统功能说明](#子系统功能说明)
- [运行方法](#运行方法)
- [待优化内容](#待优化内容)
- [子系统截图](#子系统截图)


## 核心代码结构

```text
.
├── system.conf              # 配置文件
├── system_parameter.py      # 解析配置文件功能函数
├── Logger.py               # 系统日志功能代码
├── tld_ns             # 获取根区文件功能
├── log       # 系统日志
├── http_server            # 主节点web服务器
├── http_client_test           # 测试web服务器
├── http_client_realtime          # 实时探测节点web服务器
├── http_client_periodic          # 定时探测节点web服务器
├── domain_ns_standalone          # 获取域名ns的独立版本
├── domain_ns_http          # 获取域名ns的http版本
├── domain_data         # 存储域名和域名的dns记录，与domain_ns_standalone版本关联
└── db_manage          # 数据库文件
```


## 子系统简介
本系统采用分布式web架构，根据不同任务类型，获取域名的DNS记录，并将结果存储与返回查询客户端


## 待优化内容

```
conda env export > pyn_env.yml  # 将当前环境的配置生成为yml配置文件
```
```
conda env create -f pyn_env.yml # 即可生成一样的环境
```
