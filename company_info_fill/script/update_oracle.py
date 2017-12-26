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

insert_oracle_nums = 3000
insert_new_count = 0
sql = "SELECT company_name FROM QYK_BAIDU_V_TBL where STATUS = 3 and MOBILE is null and TELEPHONE is null"
oracle_handle = oracle_cur.execute(sql)
items = oracle_handle.fetchall()
company_names = set([i[0].decode('gb18030').strip() for i in items])
mongo_names = mongo_db.fill_info.find({'qichacha_status': 1}, {'company_name':1})
mongo_names = set([i['company_name'] for i in mongo_names])
print len(company_names)
print len(mongo_names)
names = (mongo_names&company_names)
print len(names)

cur_date = datetime.datetime.now()
for name in names:
    if not insert_oracle_nums:
        break
    item = mongo_db.fill_info.find_one({'company_name': name})
    oracle_update_item = {'company_name': name.encode('gb18030'),
                          'CONTACT_STATUS': 2,
                          'CONTACT_UPDATE_DATE': cur_date}
    telephone = item['qichacha_telephone']
    if telephone and len(telephone) >= 11:
        oracle_update_item['telephone'] = telephone.encode('gb18030')
    mp = item['qichacha_mp']
    if mp:
        oracle_update_item['mobile'] = mp.encode('gb18030')

    if (oracle_update_item.get('telephone') or oracle_update_item.get('mobile')):
        insert_oracle_nums -= 1
        for tbl_name in ('BAIDU_V_TBL', 'QYK_BAIDU_V_TBL'):
            sql = 'update %s set ' % (tbl_name)
            for key in oracle_update_item:
                sql += '%s=:%s, ' % (key, key)
            sql = '%s where company_name=:company_name' % (sql[:-2])
            oracle_handle.execute(sql, oracle_update_item)

oracle_conn.commit()
oracle_cur.close()
oracle_conn.close()
