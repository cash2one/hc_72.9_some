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

db_oracle_str ="corplib/UZl3#7R6z@192.168.100.114:1521/cplib"
oracle_conn = cx_Oracle.connect(db_oracle_str)
oracle_cur = oracle_conn.cursor()
mongo_db = MongoClient('192.168.60.64', 10010).company_info

sql = "SELECT company_name, url FROM QYK_BAIDU_V_TBL where STATUS = 3 and MOBILE is null and TELEPHONE is null"
oracle_handle = oracle_cur.execute(sql)
items = oracle_handle.fetchall()
company_names = {i[0].decode('gb18030').strip():i[1] for i in items}
for name in tqdm(company_names):
    try:
        mongo_db.fill_info.insert({
            'company_name': name,
            'web_url': company_names[name],
            'web_status': 0,
            'web_mp': '',
            'web_telephone': '',
            'baidu_v_status': 0,
            'qichacha_status':0,
            'qichacha_name': '',
            'qichacha_contacter': '',
            'qichacha_mp': '',
            'qichacha_telephone': '',
            'insert_date': datetime.datetime.now(),
            'update_date': datetime.datetime.now()
            })
    except pymongo.errors.DuplicateKeyError:
        continue

oracle_cur.close()
oracle_conn.close()
