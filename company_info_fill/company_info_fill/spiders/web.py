# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy import log
from company_info_fill.items import CompanyInfoFillItem
from company_info_fill.settings import MOBILE_PREFIX_LIST
import cx_Oracle
from Queue import Queue
from pymongo import MongoClient
import time
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')


class WebSpider(scrapy.Spider):
    name = "web"

    def __init__(self, *args, **kwargs):
        super(WebSpider, self).__init__(*args,**kwargs)
        self.mongo_db = MongoClient('192.168.60.64', 10010).company_info

    def start_requests(self):
        mongo_handle = self.mongo_db.fill_info.find({'web_url': 'www.sxjdcmy.com'}, {'company_name': 1, 'web_url': 1})
        # mongo_handle = self.mongo_db.fill_info.find({'web_status': 0}, {'company_name': 1, 'web_url': 1})
        remain_count = mongo_handle.count()
        self.log('start %d' % (remain_count), level=log.INFO)
        for mongo_item in mongo_handle:
            company_name = mongo_item['company_name']
            item = CompanyInfoFillItem()
            item['company_name'] = company_name

            remain_count = remain_count - 1
            if not mongo_item['web_url']:
                url = 'https://www.baidu.com/s?wd=%s@v' % (company_name)
                self.log('insert baidu_v url %s (remain %d)' % (url, remain_count), level=log.INFO)
                yield scrapy.Request(url, meta={'item': item}, callback=self.parse_baidu_v, dont_filter=True)
            else:
                item['web_url'] = mongo_item['web_url']
                url = 'http://' + item['web_url'] if item['web_url'].find('http') < 0 else item['web_url']
                self.log('insert web homepage url %s (remain %d)' % (url, remain_count), level=log.INFO)
                yield scrapy.Request(url, meta={'item': item}, callback=self.parse_home, dont_filter=True)

    def parse_home(self, response):
        i = response.meta['item']
        if response.status != 200 or not hasattr(response, 'xpath'):
            self.log('parse web homepage failed! status_code is %d, company_name=%s, homepage=%s err=%s' %
                    (
                        response.status,
                        i['company_name'],
                        response.url,
                        response.meta['errmsg'] if 'errmsg' in response.meta else ''),
                    level=log.WARNING)
            self.mongo_db.fill_info.update({'company_name': i['company_name']}, {'$set': {'web_status': 2}})
            return

        # parse mp and phone from homepage
        regex_mp = re.compile(u'(?<![0-9])1[0-9]{10}(?![0-9])')
        regex_phone = re.compile(u'400[0-9]{7}|800[0-9]{7}|0\d{2,3}-\d{5,9}|0\d{2,3}-\d{5,9}')
        #regex_phone = re.compile(u'(?<![0-9])[0-9]{3,4}-[0-9, ]{7,8,9}(?![0-9])')
        result_mp=regex_mp.findall(response.body,re.S)
        result_phone = regex_phone.findall(response.body,re.S)
        i['telephone'] = result_phone
        i['mp'] = filter(lambda x: x[:3] in MOBILE_PREFIX_LIST,set(result_mp))

        # parse contact page url
        contact_str = [u'\u8054\u7cfb\u6211\u4eec', u'\u5173\u4e8e\u6211\u4eec']
        all_a = response.xpath("//a")
        contact_url_queue = Queue()
        from ipdb import set_trace
        set_trace()
        for a in all_a:
            if a.xpath('text()'):
                a_text = a.xpath('text()').extract()[0]
                for s in contact_str:
                    print a_text, a.xpath('@href').extract()
                    if a_text.find(s) > 0 and a.xpath('@href').extract():
                        contact_url = a.xpath('@href').extract()[0]
                        contact_url = response.url + contact_url if contact_url[0] == '/' else contact_url
                        self.log('prase contact url %s %s' % (a_text, contact_url), level=log.INFO)
                        contact_url_queue.put(contact_url)

        if contact_url_queue.qsize() == 0:
            self.log('not find contact url %s %s' % (i['company_name'], response.url), level=log.INFO)
       # if contact_url_queue.qsize() > 0:
           # url = contact_url_queue.get()
           # return scrapy.Request(url, meta={'item':i, 'contact_url_queue':contact_url_queue}, callback=self.parse_contact, dont_filter=True)
        # else:
            # return i

    def parse_contact(self, response):
        i = response.meta['item']
        if response.status != 200:
            self.log('parse contact failed! status_code is %d, home_url=%s contact_url=%s id=%d err=%s' %
                     (response.status,
                      i['grab_url'],
                      response.url,
                      i['id'],
                      response.meta['errmsg'] if 'errmsg' in response.meta else ''),
                     level=log.WARNING)
            return i

        regex_mp = re.compile(u'(?<![0-9])1[0-9]{10}(?![0-9])')
        #regex_phone = re.compile(u'0\d{2,3}-\d{5,9}|0\d{2,3}-\d{5,9}')
        regex_phone = re.compile(u'400[0-9]{7}|800[0-9]{7}|0\d{2,3}-\d{5,9}|0\d{2,3}-\d{5,9}')
        #regex_phone = re.compile(u'(?<![0-9])[0-9]{3,4}-[0-9]{7,8}(?![0-9])')
        result_mp=regex_mp.findall(response.body,re.S)
        result_phone = regex_phone.findall(response.body,re.S)
        i['telephone_contact'] = result_phone
        i['mobile_contact'] = filter(lambda x: x[:3] in MOBILE_PREFIX_LIST, set(result_mp))
        return i

    def url_clean(self, value):
        value = re.sub(u'[\u4e00-\u9fa5 \t\n>]+', '', value).strip()
        value = re.sub(r'\.$', '', value)
        value = re.sub(r'/.*$', '', value)
        return value
