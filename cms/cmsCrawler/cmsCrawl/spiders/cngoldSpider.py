# encoding: utf-8
# -*- coding: UTF-8 -*-


from scrapy.contrib.spiders import CrawlSpider, Rule, Spider

from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.conf import settings
import random

from cmsCrawl.items import CmscrawlItem 
import re
 
import pdb
import sys
import random
import time
import datetime


reload(sys)
sys.setdefaultencoding("utf-8")

class cngoldSpider(Spider):
    name = 'cngoldSpider'
    allowed_domains = ['energy.cngold.org', 'cngold.org']


    def __init__(self, *args, **kwargs):
        super(cngoldSpider, self).__init__(*args, **kwargs)
        today = datetime.datetime.today()
        self.todayFilter = '{0:04d}-{1:02d}-{2:02d}'.format(today.year, today.month, today.day) 
        self.start_urls = []
        self.start_urls.extend(
                [
                    'http://energy.cngold.org/news/',
                    'http://energy.cngold.org/news/list_422_2.html',
                    'http://energy.cngold.org/news/list_422_3.html',
                ]
            )


    def start_requests(self):
        pdb.set_trace()
        for url in self.start_urls:
            bindip = random.choice(settings['IPPOOLS'])
            ua = random.choice(settings['USER_AGENTS'])
            yield Request(url = url,
                    callback = self.parse_list_page,
                    meta = {
                        'bindaddress' : (bindip, 0),
                    },
                    headers = {
                        'User-Agent': ua,
                        'Upgrade-Insecure-Requests' : '1',
                        'Host' : 'energy.cngold.org',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )


    def parse_list_page(self, response):
        pdb.set_trace()
        sel = Selector(response)
        contentlist = sel.xpath('//div[@class="inMid fl"]/ul/li')
        shouldNextPage = True 
        for row in contentlist:
            if u'原油'  not in row.xpath('div/a[1]/text()').extract()[0]:
                continue
            publish_date = row.xpath('span/text()').extract()[0]
            finalpageUrl = row.xpath('div/a[2]/@href').extract()[0]
            title = row.xpath('div/a[2]/text()').extract()[0]
            if publish_date != self.todayFilter:
                shouldNextPage = False
            else:
                item = CmscrawlItem() 
                item['title'] = title
                item['bc_id'] = finalpageUrl
                item['publish_date'] = publish_date
                item['fromSite'] = u'energy.cngold.org'
                bindip = random.choice(settings['IPPOOLS'])
                ua = random.choice(settings['USER_AGENTS'])
                yield Request(url = finalpageUrl,
                    callback = self.parse_final_page,
                    meta = {
                        'bindaddress' : (bindip, 0),
                        'item' : item,
                    },
                    headers = {
                        'User-Agent': ua,
                        'Upgrade-Insecure-Requests' : '1',
                        'Host' : 'energy.cngold.org',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch',
                        'Referer' : 'http://energy.cngold.org',
                    },
                )

    def parse_final_page(self, response):
        #pdb.set_trace()
        sel = Selector(response)
        item = response.meta['item']
        item['publish_date'] = sel.xpath('//div[@class="zsctop clearfix"]/p[@class="left_p"]//span[1]')
        try:
            item['publish_date'] = datetime.datetime.strptime(item['publish_date'], '%Y-%m-%d %H:%M:%S')
        except:
            item['publish_date'] = datetime.datetime.strptime(self.todayFilter, '%Y-%m-%d')
        item['source'] = u'金投原油'
        item['author'] = u''
        item['title'] = item['title'].strip()
        item['content'] =sel.xpath('//div[@class="content w680"]').extract()[0].replace(u'\xa0', u'').replace(u'\u2014', u'').replace(u'\xb7', u'').replace(u'\xd8', u'')
        item['imgs'] = sel.xpath('//div[@class="content w680"]//img/@src').extract()
        yield item
