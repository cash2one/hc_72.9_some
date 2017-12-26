#coding=gb18030

import cx_Oracle
import sys
sys.path.append('/tools/python_common')
import os
import re
from pymongo import MongoClient
import pymongo
import datetime
from tqdm import tqdm

os.system('export LANG=zh_CN.GB18030')
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.ZHS16GBK'

reload(sys)
sys.setdefaultencoding('gb18030')

print datetime.datetime.now()

mongo_db = MongoClient('192.168.60.64', 10010).company_info

items = mongo_db.fill_info.find({'qichacha_status': 1, 'qichacha_telephone': {'$ne': ''}}, {'company_name':1, 'qichacha_telephone':1})
cur_count = 0
for item in items:
    qichacha_telephone = item['qichacha_telephone']
    if len(qichacha_telephone) >= 11 and qichacha_telephone.find('-') >= 0:
        if qichacha_telephone[:1] != '0':
            new_telephone = qichacha_telephone.replace('-', '')
            mongo_db.fill_info.update_one({'company_name': item['company_name']}, {'$set': {'qichacha_telephone': new_telephone}})
            cur_count += 1
            print cur_count, item['company_name'], qichacha_telephone, new_telephone
        # new_telephone = ''
        # if qichacha_telephone[:2] in ('01', '02'):
            # new_telephone = qichacha_telephone[:3] + '-' + qichacha_telephone[3:]
        # elif qichacha_telephone[:2] == '00':
            # new_telephone = qichacha_telephone[:5] + '-' + qichacha_telephone[5:]
        # else:
            # new_telephone = qichacha_telephone[:4] + '-' + qichacha_telephone[4:]

        # mongo_db.fill_info.update_one({'company_name': item['company_name']}, {'$set': {'qichacha_telephone': new_telephone}})
        # cur_count += 1
        # print cur_count, item['company_name'], qichacha_telephone, new_telephone
    # elif len(qichacha_telephone) < 7:
        # mongo_db.fill_info.update_one({'company_name': item['company_name']}, {'$set': {'qichacha_telephone': ''}})
