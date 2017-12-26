#-*- coding:utf-8 -*-
from scrapy import Selector
import urllib
import requests
import random
import time
import re
import datetime
from pymongo import MongoClient
import pymongo
import redis
import sys
sys.path.append('/tools/python_common')
from anti_ban_requests import AntiBan
from common_func import *
from ipdb import set_trace
import traceback

class Cookie():
    """qichacha cookie manager"""

    def __init__(self):
        self.init_mongo_db()

    def init_mongo_db(self):
        while True:
            try:
                self.mongo_db = MongoClient('192.168.60.65', 10010).corplib
                break
            except Exception, e:
                self.logger.error('initialize mongo db error! (%s)', str(e))
                time.sleep(5)

    def ok(self):
        self.mongo_db.qq_cookie_tbl.update_one({'qq': self.qq}, {'$set': {'update_time': datetime.datetime.now()}, '$inc': {'use_times': 1}})
        item = self.mongo_db.qq_cookie_tbl.find_one({'qq': self.qq}, {'use_times': 1})
        return item.get('use_times', 0)

    def failed(self):
        self.mongo_db.qq_cookie_tbl.update_one({'qq': self.qq}, {'$set': {'status': 2}})

    def stop(self):
        self.mongo_db.qq_cookie_tbl.update_one({'qq': self.qq}, {'$set': {'status': 4, 'using': False}})

    def get_cookie(self):
        while True:
            item = self.mongo_db.qq_cookie_tbl.find_one({'status': 1, 'cookie': {'$ne': ''}, 'using': False}, {'qq': 1, 'cookie': 1})
            if item:
                self.qq = item['qq']
                self.mongo_db.qq_cookie_tbl.update_one({'qq': self.qq}, {'$set': {'login_time': datetime.datetime.now(), 'use_times': 0, 'using': True}})
                return {'cookie': item['cookie'], 'qq': self.qq}
            logging.error('not valid cookie get, wait 10s')
            time.sleep(10)

redis_hosts = ['172.16.252.22', '172.16.248.22', '10.10.10.27']
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


if __name__ == "__main__":
    DIR_PATH = os.path.split(os.path.realpath(__file__))[0]
    LOG_FILE = DIR_PATH + '/logs/spider.log'
    logging.getLogger("requests").setLevel(logging.WARNING)
    logInit(logging.INFO, LOG_FILE, 0, True)
    time_lis = [3,5,7,10]
    cookies = {'Cookie':'M_distinctid=15b651269fd26c-0c030a6793a3ab-4e47052e-1fa400-15b651269fe1f6; gr_user_id=231187ea-b260-4c69-a9f8-4973236ceee9; _uab_collina=149204938619711243935137; _umdata=37735FB50C0BFD5EC3A3F03F39155088686D5A16FD00563D36D777E44B3F93B67E7670A2D37709B9CD43AD3E795C914C7B3AD3E7779EC07235ED06D8022F9367; PHPSESSID=5n33n68100gssf4f5cd8ic86r0; gr_session_id_9c1eb7420511f8b2=7a3be926-2af7-487b-a5ba-70b50e117a99; CNZZDATA1254842228=224054499-1492046923-https%253A%252F%252Fwww.baidu.com%252F%7C1493033903'}
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

    c = Cookie()
    cookie_item = c.get_cookie()

    ab = AntiBan(True)
    r_item = ab.get_requests()

    redis_db = connect_redis()
    mongo_db = MongoClient('192.168.60.64', 10010).company_info
    queue_len = redis_db.llen('COMPANY_NAME_QUEUE')
    logging.info('use qq: %s queue len: %d', cookie_item['qq'], queue_len)
    ban_count = 0
    while True:
        # handle = mongo_db.fill_info.find({'company_name': '深圳市衔尾蛇网络科技有限公司'}, {'company_name': 1})
        name = redis_db.lpop('COMPANY_NAME_QUEUE')
        if not name:
            time.sleep(5)
            logging.info('no company need to fetch! sleep 5s')
            continue

        url = 'http://www.qichacha.com/search?key='+urllib.quote(name)
        name = name.decode('utf-8')
        try:
            cookies = {'Cookie': cookie_item['cookie']}
            s = r_item.get('requests')
            ip = r_item.get('ip')
            r = s.get(url, cookies=cookies, headers=header, allow_redirects=False)
            if r.status_code != 200 or (len(r.text)<1000 and r.text.find('index_verify') > 0):
                qq = cookie_item['qq']
                logging.warning('request failed! %d ip=%s qq=%s url=%s jump_url=%s body=%s', r.status_code, ip, qq, url, r.headers.get('Location', ''), r.text)
                r_item = ab.get_requests()
                if ban_count == 3:
                    c.failed()
                    cookie_item = c.get_cookie()
                    ban_count = 0
                else:
                    ban_count += 1
                continue

            ban_count = 0
            sel = Selector(text=r.text)
            qichacha_company_name = contact_man = contact_num = ""
            xpath_handles = sel.xpath("//table[@class='m_srchList']/tbody/tr")
            for xpath_handle in xpath_handles:
                items = filter(lambda x: x.strip(), xpath_handle.xpath('.//text()').extract())
                if len(items) < 3:
                    continue
                qichacha_company_name = items[0]
                tmp_name = items[0].replace(u'\uff08', u'(')
                tmp_name = tmp_name.replace(u'\uff09', u')')
                if tmp_name.upper() == name.upper():
                    for ele in items[1:]:
                        if ele.find(u'企业法人') != -1:
                            contact_man = ele.split(u'：')
                            contact_man = contact_man[1].strip() if len(contact_man[1]) > 1 else ''
                        if ele.find(u'联系方式') != -1:
                            contact_num = ele.split(u'：')
                            contact_num = contact_num[1].strip() if len(contact_num[1]) >= 7 else ''
                    break

            if contact_num:
                qichacha_mp = ''
                qichacha_telephone = ''
                if re.match('1\d{10}', contact_num):
                    qichacha_mp = contact_num
                elif len(contact_num) >= 7:
                    qichacha_telephone = contact_num

                mongo_db.fill_info.update_one({'company_name': name},
                        {'$set': {
                            'update_date': datetime.datetime.now(),
                            'qichacha_company_name': qichacha_company_name,
                            'qichacha_status': 1,
                            'qichacha_contacter': contact_man,
                            'qichacha_mp': qichacha_mp,
                            'qichacha_telephone': qichacha_telephone}})
            else:
                mongo_db.fill_info.update_one({'company_name': name},
                        {'$set': {
                            'update_date': datetime.datetime.now(),
                            'qichacha_company_name': qichacha_company_name,
                            'qichacha_contacter': contact_man,
                            'qichacha_status': 2}})
            qq_count = c.ok()
            logging.info('%s [%s:%s:%d] %s %s %s %s',
                         'find' if contact_num else 'not find',
                         ip, cookie_item['qq'], qq_count, name, qichacha_company_name, contact_man, contact_num)
            # if qq_count > 1000:
                # c.stop()
                # cookie_item = c.get_cookie()
                # r_item = ab.get_requests()
        except Exception,e:
            logging.info("%s", str(traceback.print_exc()))
        time.sleep(random.choice(time_lis))
