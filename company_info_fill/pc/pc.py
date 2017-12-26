# -*- coding: utf-8 -*-
import sys
import os
import logging
import time
import datetime
import redis
import re
from pymongo import MongoClient
sys.path.append('/tools/python_common')
from common_func import logInit
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import selenium.webdriver.support.ui as ui
from leads_rules import get_company_name, get_company_name_from_title, clearCompany_name, get_contacter

redis_hosts = ['10.10.10.27', '192.168.245.31', '172.16.252.22', '172.16.248.22']
MOBILE_PREFIX_LIST=['130','131','132','133','134','135','136','137','138','139','150','151','152','153','155','156','157','158','159','170','176','177','178','180','181','182','183','184','185','186','187','188','189']
CONTACT_US_LIST = [u'联系我们', u'关于']

class PcCompany():
    def __init__(self, browser_type='chrome'):
        self.logger = logging.getLogger('PcCompany')
        self.init_mongo()
        self.init_redis()
        self.init_browser(browser_type)

    def __del__(self):
        self.browser_quit()

    def init_redis(self):
        for host in redis_hosts:
            redis_pool = redis.ConnectionPool(host=host, port=6379, socket_timeout=2)
            # redis_pool = redis.ConnectionPool(host=host, port=7901, socket_timeout=2)
            r = redis.Redis(connection_pool = redis_pool)
            try:
                last_len = r.llen('ALI_COMPANY_KEYWORD_LIST')
                break
            except redis.exceptions.ConnectionError:
                continue
        self.redis_db = redis.Redis(connection_pool = redis_pool)

    def init_mongo(self):
        self.mongo_db = MongoClient('192.168.60.64', 10010).company_info

    def init_browser(self, browser_type):
        if browser_type == 'chrome':
            opts = Options()
            opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36")
            self.browser = webdriver.Chrome(chrome_options=opts)
        else:
            dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
            service_log_path = dirname + '/ghostdriver.log'
            webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
            webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.Accept-Language'] = 'zh-CN,zh;q=0.8'
            webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.resourceTimeout'] = '5000'
            service_args = [
                '--ignore-ssl-errors=true',
                #'--load-images=false',
                # '--disk-cache=true',
                # '--disk-cache-path=%s' % (dirname + '/disk_cache')
            ]
            service_args = service_args.extend(['--proxy=http://127.0.0.1:8888', '--proxy-type=http'])
            self.browser = webdriver.PhantomJS(service_log_path=service_log_path, service_args=service_args)
            self.browser.set_script_timeout(5)
        self.browser.maximize_window()
        self.pid = self.browser.service.process.pid
        self.wait = ui.WebDriverWait(self.browser, 10)

    def browser_quit(self):
        try:
            if self.browser:
                self.browser.quit()
                os.kill(self.pid, 9)
        except Exception, e:
            self.logger.warning("browser quit error:%s" %(str(e)))
        finally:
            self.browser = None

    def browser_quit_others(self):
        if len(self.browser.window_handles) == 1:
            self.browser.switch_to_window(self.browser.window_handles[0])
        else:
            for h in self.browser.window_handles[1:]:
                self.browser.switch_to_window(h)
                self.browser.close()
            self.browser.switch_to_window(self.browser.window_handles[0])

    def get_url(self):
        while True:
            url = self.redis_db.lpop('COMPANY_URL_QUEUE')
            if not url and self.redis_db.llen('COMPANY_URL_QUEUE') > 0:
                continue
            break
        return url

    def parse(self, url):
        if url[:4] != 'http':
            url = 'http://' + url
        self.browser.get(url)

        ## parse home page
        home_item = self.parse_item()
        self.logger.info('home parse %s (%s)', url, home_item)
        ##parse contact us page
        xpath_handles = self.browser.find_elements_by_xpath('//a')
        contact_us_url = ''
        for key in CONTACT_US_LIST:
            for x in xpath_handles:
                if key in x.text:
                    contact_us_url = x.get_attribute('href')
                    break
            if contact_us_url:
                break

        contact_us_item = {}
        if contact_us_url:
            logging.info('find contact us page %s %s', x.text, contact_us_url)
            x.click()
            self.browser.switch_to_window(self.browser.window_handles[-1])
            contact_us_item = self.parse_item()
            self.logger.info('contact up parse %s (%s)', contact_us_url, contact_us_item)
            self.browser_quit_others()

        item = self.combine_item(home_item, contact_us_item)
        return item

    def parse_item(self):
        item = {}
        xpath_handle = self.browser.find_element_by_xpath('/html')
        body = xpath_handle.text
        regex_mp = re.compile(u'(?<![0-9])1[0-9]{10}(?![0-9])')
        regex_phone = re.compile(u'400[0-9]{7}|800[0-9]{7}|0\d{2,3}-\d{5,9}|0\d{2,3}-\d{5,9}')

        result_mp=regex_mp.findall(body, re.S)
        result_phone = regex_phone.findall(body, re.S)
        item['telephone'] = result_phone
        mobile_contact = filter(lambda x: x[:3] in MOBILE_PREFIX_LIST, set(result_mp))
        item['mp'] = mobile_contact

        company_name = get_company_name_from_title(self.browser.title)
        if company_name:
            item['company_name'] = company_name
        else:
            company_name = get_company_name(body)
            item['company_name'] = company_name

        contacters = get_contacter(body)
        contacter = ''
        if contacters:
            contacter = contacters[0]
            for c in contacters:
                contacter = c if len(contacter) > len(c) else contacter
        contacter = contacter[:50]
        item['contacter'] = contacter
        return item

    def combine_item(self, home_item, contact_us_item):
        item = {}
        if contact_us_item:
            item['telephone'] = ','.join(contact_us_item.get('telephone', []) + home_item.get('telephone', []))
            item['mp'] = ','.join(contact_us_item.get('mp', []) + home_item.get('mp', []))
        else:
            item['telephone'] = ','.join(home_item.get('telephone', []))
            item['mp'] = ','.join(home_item.get('mp', []))
        item['company_name'] = contact_us_item['company_name'] if contact_us_item.get('company_name', []) else home_item.get('company_name', [])
        item['company_name'] = item['company_name'][0] if len(item['company_name']) > 0 else ''
        return item

    def update_mongo(self, url, item):
        try:
            if item.get('telephone', '') or item.get('mp', ''):
                self.mongo_db.fill_info.update({'web_url': url},
                                     {'$set': {
                                         'web_company_name': item.get('company_name', ''),
                                         'web_contacter': item.get('contacter', ''),
                                         'web_mp': item.get('mp', ''),
                                         'web_telephone': item.get('telephone', ''),
                                         'web_status': 1,
                                         'update_date': datetime.datetime.now()
                                     }})
                self.logger.info('update mongo find %s', url)
            else:
                self.mongo_db.fill_info.update({'web_url': url},
                                     {'$set': {
                                         'web_status': 2,
                                         'update_date': datetime.datetime.now()
                                     }})
                self.logger.info('update mongo not find %s', url)
        except Exception, e:
            self.logger.warning('update mongo failed! (%e) item=%s', str(e), str(item))


if __name__ == '__main__':
    DIR_PATH = os.path.split(os.path.realpath(__file__))[0]
    LOG_FILE = DIR_PATH + '/logs/spider.log'
    logInit(logging.INFO, LOG_FILE, 0, True)

    pc = PcCompany(browser_type='PhantomJS')
    while True:
        url = pc.get_url()
        # url = 'www.jinwangfeed.com'
        if not url:
            logging.info('no url need to fetch! sleep 5s')
            time.sleep(5)
            continue
        logging.info('fetch url %s', url)
        item = pc.parse(url)
        pc.update_mongo(url, item)

