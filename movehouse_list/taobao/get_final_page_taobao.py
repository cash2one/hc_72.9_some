#encoding=gb18030
#-*- coding:gb18030-*-
import os
import sys
import logging
import re
import json
import codecs
import urllib
import Queue
import threading
import requests
from lxml import etree
import time
import pymongo
from pymongo import MongoClient
import random
import traceback
from iplist import *
from func import *
import cx_Oracle
from anti_ban_selenium import AntiBan
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


DB_STR='match/jkn65#ud@192.168.100.111:1521/move' #product
DIR_PATH = sys.path[0] + '/' if sys.path[0] else ''
LOG_FILE = DIR_PATH + 'logs/spider.log'
SPIDER_THREAD_DOWN = False
WEBSITEQUEUE_THREAD_DOWN = False
INTERVALSEC = random.randint(3, 5)
INTERVALSEC_LIST = random.uniform(1, 3)
WAIT_TIME = 20
THREAD_NUM = 1


class WebSite():
    url = ''
    memberId = ''
    appid = -1
    category_count = 0
    page_count = 0
    type = TYPES['INVALID']
    code = -1
    errmsg = ''
    net_time = 0.0
    parse_time = 0.0
    user_defined = True
    has_page = True
    try_count = 2

    def __init__(self, memberid, url, appid, type):
        self.url = url 
        self.memberid = memberid.strip()
        self.appid = appid
        self.type = type 

class WebSiteQueue(threading.Thread):
    __queue = Queue.Queue(0)
    __start_event = threading.Event()
    __mutex = threading.Lock()
    __mutex_record = threading.Lock()

    def __init__(self):
        threading.Thread.__init__(self)
        self.record = {}

    def initialize(self):
        try:
            self.mongo_db = MongoClient('192.168.60.64', 10010).m1688
            self.__mutex.acquire()
            self.oracle_db = cx_Oracle.connect(DB_STR)
            self.__mutex.release()
            return True
        except Exception, e:
            logging.error('init MemberIdQueue failed! err=%s', str(e))
            return False

    def getSize(self):
        return self.__queue.qsize()

    def getWebSite(self):
        return self.__queue.get(True)

    def isEmpty(self):
        return self.__queue.empty()

    def waitStart(self):
        self.__start_event.wait()

    def newWebSite(self, memberid, url, appid, type):
        if memberid and url:
            self.__queue.put(WebSite(memberid, url, appid, type))
            return True
        return False

    def waitEnd(self):
        while self.isAlive():
            time.sleep(1)

    def insert(self, website, records):
        if records and website.memberid:
            try:
                self.mongo_db.content_tbl.remove({'memberId':website.memberid})
                for record in records:
                    try:
                        self.mongo_db.content_tbl.insert(record)
                    except pymongo.errors.DuplicateKeyError, e:
                        logging.warning('insert record duplicatekey error! memberid=%s\n %s', website.memberid, str(record))
                        continue
            except Exception, e:
                logging.error('insert records error url=%s memberid=%s! err=%s', website.url, website.memberid, str(traceback.format_exc()))
                return False
            return True
        else:
            logging.error('insert records error len(records)=%d memberid=%s', len(records), website.memberid)
            return True

    def setStatus(self, website, status):
        try:
            website.status = status
            self.mongo_db.url_tbl.find_one_and_update({'url':website.url}, {'$set':{'status':status, 'count':website.page_count}})
            return True
        except Exception, e:
            logging.error('set status error! err=%s', str(e))
            return False

    def setListPageStatus(self, appid, url, status):
        self.__mutex.acquire()
        while True:
            try:
                if appid > 0:
                    cur = self.oracle_db.cursor()
                    sql_str = "update cor_website_move set SEARCH_LISTPAGE_STATUS=:1 where id=:2 or website=:3"
                    cur.execute(sql_str, (status, appid, url))
                    self.oracle_db.commit()
                    cur.close()
                    self.__mutex.release()
                    break
            except Exception, e:
                logging.error('set list page status error reconnect! sql=%s err=%s', sql_str, str(e))
                self.oracle_db.close()
                self.oracle_db = cx_Oracle.connect(DB_STR)
                continue

    def havingFetchOracle(self, url):
        self.__mutex.acquire()
        while True:
            try:
                sql_str = "select count(1) from cor_website_move where STATES in (0, 7, 9) and SEARCH_LISTPAGE_STATUS = 1 and website=:1"
                cur = self.oracle_db.cursor()
                result = cur.execute(sql_str, (url,))
                items = result.fetchall()
                cur.close()
                self.__mutex.release()
                return bool(items[0][0])
            except Exception, e:
                if str(e).find('ORA-03114') >= 0:
                    self.oracle_db.close()
                    self.oracle_db = cx_Oracle.connect(DB_STR)
                    continue
                logging.error('havingFetchOracle oracle connect error reconnect! sql=%s err=%s', sql_str, str(e))
                return True



    def setListPageStatusFailed(self, appid, url):
        self.setListPageStatus(appid, url, ORACLE_SEARCH_LISTPAGE_STATUS['FAILED'])
        self.deleteRecord(url)

    def setListPageStatusOK(self, appid, url):
        self.setListPageStatus(appid, url, ORACLE_SEARCH_LISTPAGE_STATUS['OK'])
        self.deleteRecord(url)

    def setListPageStatusStandby(self, appid):
        self.setListPageStatus(appid, url, ORACLE_SEARCH_LISTPAGE_STATUS['STANDBY'])

    def setRecord(self, url):
        self.__mutex_record.acquire()
        self.record[url] = 1
        self.__mutex_record.release()

    def hasRecord(self, url):
        self.__mutex_record.acquire()
        ret = url in self.record
        self.__mutex_record.release()
        return ret

    def deleteRecord(self, url):
        self.__mutex_record.acquire()
        self.record.pop(url, 1)
        self.__mutex_record.release()
 
    def run(self):
        try:
            # first set event 
            self.__start_event.set()

            self.info = logging.info('read website start!')
            while not WEBSITEQUEUE_THREAD_DOWN:
                logging.info('get url from mongo before')
                items = self.mongo_db.url_tbl.find({'type':{'$in':[TYPES['TAOBAO']]}, 'status':STATUS['STANDBY']}, {'appid':1, 'url':1, 'type':1})
                # items = self.mongo_db.url_tbl.find({'url': 'http://shop131004500.taobao.com'},
                #                                    {'appid':1, 'url':1, 'type':1})
                items = [item for item in items]
                logging.info('get url from oracle after count=%d', len(items))
                if not items:
                    time.sleep(60)
                    continue

                taobao_count = tmall_count = other_count = running_count = 0
                for i, item in enumerate(items):
                    while self.getSize() >= 1:
                        time.sleep(60)

                    url = item['url']
                    appid = item['appid']
                    url_type = item['type']
                    if url:
                        logging.info('before url=%s', url)

                        if url_type == TYPES['TAOBAO']:
                            taobao_count += 1
                        elif url_type == TYPES['TMALL']:
                            tmall_count += 1
                        else:
                            other_count += 1
                            continue

                        try:
                            r = requests.get(url, headers=HEADERS_HOMEPAGE)

                            if r.status_code != 200 or len(r.text) <= 0:
                                self.setListPageStatusFailed(appid, url)
                                self.mongo_db.url_tbl.update({'url':url}, {'$set':{'status':STATUS['OK'], 'count':0}})
                                logging.warning('website invalid! url=%s status=%d', url, r.status_code)
                                continue

                            memberId = re.findall(r'(?<=shopId=)\d+(?=;)', r.text)

                            if memberId:
                                self.newWebSite(memberId[0], url, appid, url_type)
                                self.setRecord(url)
                                self.mongo_db.url_tbl.update({'url':url}, {'$set':{'type':url_type, 'memberId':memberId[0]}})
                                logging.info('insert new website url=%s memberid=%s', url, memberId[0])
                            else:
                                self.setListPageStatusFailed(appid, url)
                                self.mongo_db.url_tbl.update({'url':url}, {'$set':{'status':STATUS['OK'], 'count':0}})
                                logging.warning('website invalid not find memberId! url=%s', url)
                        except Exception, e:
                            err_str = str(traceback.format_exc())
                            logging.error('get homepage failed! url=%s err=%s', url, err_str)
                            if err_str.find('Name or service not known') >= 0 or err_str.find('InvalidURL') >= 0 or err_str.find('SSLError') >= 0:
                                self.setListPageStatusFailed(appid, url)
                                self.mongo_db.url_tbl.update({'url':url}, {'$set':{'status':STATUS['OK'], 'count':0}})
                                logging.warning('website invalid! url=%s', url)

                logging.info('read oracle complete! taobao_count=%d tmall_count=%d other_count=%d running_count=%d', \
                    taobao_count, tmall_count, other_count, running_count)
        except Exception, e:
            self.__start_event.set()
            logging.error('run websitequeue happen error! err=%s', str(traceback.format_exc()))


class Spider(threading.Thread):

    def __init__(self, websitequeue):
        threading.Thread.__init__(self)
        self.websitequeue = websitequeue
        self.wid_lock = threading.Lock()
        self.wid = '13552995480'
        self.ab = AntiBan('chrome', True, True)
        self.broswer = None

    def getCategory(self, memberid):
        if not memberid:
            return []

        category_list = []
        url = 'https://mallbrand.m.tmall.com/service/shop/get_shop_cat.ajsonp?shop_id=%s&parentCatId=0' %(memberid)
        try:
            r = requests.get(url, headers=HEADERS_CATEGORY)
            results = json.loads(r.text[r.text.find('['):r.text.rfind(']')+1]) if r.text else ''
            title_map = {}
            for item in results:
                category_list.append([item['categoriesID'], '', item['categoriesName'], ''])
                title_map[item['categoriesID']] = item['categoriesName']
                if 'subShopCategoryList' in item:
                    for subItem in item['subShopCategoryList']:
                        category_list.append([subItem['categoriesID'], subItem['parentID'],\
                                subItem['categoriesName'], title_map[subItem['parentID']] if subItem['parentID'] in title_map else ''])
        except Exception, e:
            logging.error('get category failed! url=%s err=%s', url, str(e))

        category_list.append(['', '', '', ''])
        return category_list

    def getPageListTaobao(self, website, base_url, catid, catpid):
        pages = []
        pageid = 1
        shopid = website.memberId
        while True:
            try:
                url = base_url %(catpid, catid, catid, pageid)
                r = self.broswer.request('GET', url, allow_redirects=False)
                if r.status_code == 302:
                    global WAIT_TIME
                    logging.warning('get page list 302! shopid=%s pageid=%d catid=%s catpid=%s src_url=%s jump_url=%s wait_time=%d',
                            shopid, pageid, catid, catpid, url, r.headers['location'], WAIT_TIME)
                    time.sleep(WAIT_TIME * 60)
                    continue

                if len(r.text) < 50:
                    self.broswer = self.ab.get_broswer()
                    continue

                if r.text.find(u'很抱歉，搜索到“<em>0</em>”个宝贝') > 0:
                    break

                results = re.findall(r'(?<=itemIds=)[\d,]+(?=&)', r.text)
                if not results:
                    logging.warning('get page list not find url! shopid=%s pageid=%d catid=%s catpid=%s url=%s', shopid, pageid, catid, catpid, url)
                    break

                pages.extend(map(lambda x:'https://item.taobao.com/item.htm?id=' + x, results[0].split(',')))

                pageid += 1

                time.sleep(INTERVALSEC_LIST)
            except requests.exceptions.Timeout:
                logging.warning('get page list time out! retry it! url=%s shopid=%s count=%d err=%s', url, shopid, len(pages), str(traceback.format_exc()))
                continue
            except Exception, e:
                if str(e).find('Connection timed out') >= 0 or str(e).find('Name or service not known') >=0:
                    logging.warning('get page list time out! retry it! url=%s shopid=%s count=%d err=%s', url, shopid, len(pages), str(traceback.format_exc()))
                    continue
                else:
                    logging.warning('get page list failed! url=%s shopid=%s count=%d err=%s', url, shopid, len(pages), str(traceback.format_exc()))
                    break

        return set(pages)

    def get_all_urls(self):
        all_urls = []
        cur_url = self.broswer.current_url
        while True:
            try:
                time.sleep(1)
                ## get end
                if self.broswer.page_source.find(u'未找到符合的宝贝') > 0:
                    break
                ## get cur page url
                eles_page = self.broswer.find_elements_by_xpath("//ul[@id='js-goods-list-items']/li/a")
            except NoSuchElementException:
                break

            urls = [ele.get_attribute('href').replace('h5.m.taobao.com/awp/core/detail.htm', 'item.taobao.com/item.htm')
                    for ele in eles_page]
            all_urls.extend(urls)

            ## click next page
            while True:
                try:
                    for i in range(15):
                        ActionChains(self.broswer).key_down(Keys.PAGE_DOWN).perform()
                        time.sleep(0.1)
                    self.broswer.find_element_by_xpath("//a[@class='c-btn c-btn-awr c-p-next']").click()
                    break
                except NoSuchElementException:
                    return all_urls
                except Exception as e:
                    if e.message.find('not clickable') > 0:
                        continue
                    try:
                        # close login windows
                        self.broswer.find_element_by_xpath("//div[@class='J_MIDDLEWARE_FRAME_WIDGET']/div/a").click()
                    except:
                        pass

        time.sleep(random.randrange(2,10))
        return all_urls

    def combine_records(self, records, website, catid, catpid, catname, catpname, urls):
        website.page_count = website.page_count + len(urls)
        records.append({
            'memberId': website.memberid,
            'catid': catid,
            'catpid': catpid,
            'catname': catname,
            'catpname': catpname,
            'count':len(urls),
            'status':1,
            'updateTime':time.time(),
            'urls':reduce(lambda x,y: x+'|'+y, urls) if urls else ''
        })

    def run(self):
        while not SPIDER_THREAD_DOWN:
            website = self.websitequeue.getWebSite()
            records = []
            first_index = 0
            second_index = -1
            while True:
                try:
                    logging.info('open homepage with selenium url=%s memberid=%s first_index=%d second_index=%d',
                                 website.url, website.memberid, first_index, second_index)
                    self.broswer = self.ab.get_broswer()
                    self.broswer.get(website.url)
                    self.broswer.find_element_by_xpath("//span[@class='js-nav-csch fun csch']").click()
                    time.sleep(1)
                    first_eles = self.broswer.find_elements_by_xpath("//ul[@class='menu']/li")

                    if first_index == 0 and len(first_eles) > 1:
                        first_index = 1
                        if len(first_eles) >= 20:
                            first_index = 0
                        for ele in first_eles:
                            if len(ele.find_elements_by_xpath("./ul/li")) >= 20:
                                first_index = 0

                    for index in range(2, first_index+1):
                        try:
                            ## close befory first category
                            first_eles[index-1].find_element_by_xpath("./h2/span[@class='js-sc-arr sc-arr arr "
                                                                      "arr-d']").click()
                            time.sleep(1)
                        except:
                            pass

                    while first_index < len(first_eles):
                        second_eles = first_eles[first_index].find_elements_by_xpath("./ul/li")
                        if second_index < 0:
                            ## first category
                            if first_index > 1:
                                try:
                                    self.broswer.find_element_by_xpath("//span[@class='js-nav-csch fun csch']").click()
                                    time.sleep(1)
                                except:
                                    pass
                            first_ele = first_eles[first_index].find_element_by_xpath("./h2/span")
                            catpid = first_ele.get_attribute('data-id')
                            catpname = first_ele.text
                            try:
                                first_ele.click()
                            except Exception, e:
                                if str(e).find('Other element would receive the click') > 0:
                                    pass
                                else:
                                    raise
                            time.sleep(1)
                            urls = self.get_all_urls()
                            if len(urls) == 0 \
                                and self.broswer.find_element_by_xpath("//div[@id='we-page']").get_attribute('style').find('display: block;') >= 0:
                                raise NameError('need login')
                            logging.info('getpagelist one category complete. [master] url=%s memberid=%s catid=%s '
                                         'catname=%s count=%d',
                                         website.url, website.memberid, catpid, catpname, len(urls))
                            self.combine_records(records, website, catpid, '', catpname, '', urls)
                            if first_index == 0:
                                break
                            if len(second_eles) > 0:
                                second_index = 0
                            else:
                                first_index += 1

                        if second_index >= 0:
                            ## second category
                            while second_index < len(second_eles):
                                try:
                                    self.broswer.find_element_by_xpath("//span[@class='js-nav-csch fun csch']").click()
                                    time.sleep(1)
                                except:
                                    pass
                                catid = second_eles[second_index].get_attribute('data-id')
                                catname = second_eles[second_index].text
                                time.sleep(1)
                                second_eles[second_index].click()
                                time.sleep(1)
                                urls = self.get_all_urls()
                                if len(urls) == 0 \
                                    and self.broswer.find_element_by_xpath("//div[@id='we-page']").get_attribute('style').find('display: block;') >= 0:
                                    raise NameError('need login')

                                logging.info('getpagelist one category complete. [slaves] url=%s memberid=%s catid=%s catname=%s '
                                             'catpid=%s catpname=%s count=%d',
                                             website.url, website.memberid, catpid, catname, catpid, catpname, len(urls))
                                self.combine_records(records, website, catid, catpid, catname, catpname, urls)
                                second_index  += 1

                            try:
                                ## close befory first category
                                self.broswer.find_element_by_xpath("//span[@class='js-nav-csch fun csch']").click()
                                time.sleep(1)
                                first_eles[index-1].find_element_by_xpath("./h2/span[@class='js-sc-arr sc-arr arr "
                                                                          "arr-d']").click()
                                time.sleep(1)
                            except:
                                pass
                            first_index += 1
                            second_index = -1

                    # 3. write to mongo and change status from oracle
                    if websitequeue.insert(website, records):
                        if website.page_count > 0:
                            websitequeue.setListPageStatusOK(website.appid, website.url)
                        else:
                            websitequeue.setListPageStatusFailed(website.appid, website.url)
                        websitequeue.setStatus(website, STATUS['OK'])
                        logging.info('insert records succeed url=%s memberid=%s category_count=%d page_count=%d', \
                            website.url, website.memberid, website.category_count, website.page_count)
                    break
                except Exception, e:
                    logging.error('something error! %s', str(e))
                    time.sleep(60 * 10)
                    continue

if __name__ == '__main__':
    #daemonize('/dev/null', LOG_FILE, LOG_FILE)
    # set global coding to gb18030
    reload(sys)
    sys.setdefaultencoding('gb18030')

    logInit(logging.INFO, LOG_FILE, 0, True)
    logging.info('start')

    websitequeue = WebSiteQueue()
    websitequeue.daemon = True
    if not websitequeue.initialize():
        sys.exit(1)
    websitequeue.start()
    websitequeue.waitStart()

    # start spider thread
    spiders = []
    for i in range(THREAD_NUM):
        s = Spider(websitequeue)
        s.daemon = True
        spiders.append(s)
        s.start()

    websitequeue.waitEnd()

    logging.info('end')
