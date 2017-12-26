#coding=gb18030

import sys
sys.path.append('/tools/python_common')
import os
import re
from pymongo import MongoClient
import pymongo
import redis
import datetime
from tqdm import tqdm

reload(sys)
sys.setdefaultencoding('gb18030')

print datetime.datetime.now()

redis_hosts = ['10.10.10.27', '172.16.252.22', '172.16.248.22']

def connect_redis():
    for host in redis_hosts:
        redis_pool = redis.ConnectionPool(host=host, port=6379, socket_timeout=2)
        r = redis.Redis(connection_pool = redis_pool)
        try:
            last_len = r.llen('ALI_COMPANY_KEYWORD_LIST')
            break
        except redis.exceptions.ConnectionError:
            continue
    redis_handle = redis.Redis(connection_pool = redis_pool)
    return redis_handle

redis_db = connect_redis()

mongo_db = MongoClient('192.168.60.64', 10010).company_info
print '%s COMPANY_NAME_QUEUE %d' % (datetime.datetime.now(), redis_db.llen('COMPANY_NAME_QUEUE'))
if redis_db.llen('COMPANY_NAME_QUEUE') == 0:
    mongo_handle = mongo_db.fill_info.find({'tianyancha_status': 0}, {'company_name': 1})
    if mongo_handle.count() > 0:
        print 'company need fetch: %d' % (mongo_handle.count())
        for item in mongo_handle:
            redis_db.lpush('COMPANY_NAME_QUEUE', item['company_name'])

print '%s COMPANY_URL_QUEUE %d' % (datetime.datetime.now(), redis_db.llen('COMPANY_URL_QUEUE'))
if redis_db.llen('COMPANY_URL_QUEUE') == 0:
    mongo_handle = mongo_db.fill_info.find({'web_status': 0}, {'web_url': 1})
    if mongo_handle.count() > 0:
        print 'url need fetch: %d' % (mongo_handle.count())
        for item in mongo_handle:
            redis_db.lpush('COMPANY_URL_QUEUE', item['web_url'])
