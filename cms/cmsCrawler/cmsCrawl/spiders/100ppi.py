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

class ppi100Spider(Spider):
    name = 'ppi100Spider'
    allowed_domains = ['100ppi.com']


    def __init__(self, *args, **kwargs):
        super(ppi100Spider, self).__init__(*args, **kwargs)
        today = datetime.datetime.today()
        self.todayFilter = '{0:04d}-{1:02d}-{2:02d}'.format(today.year, today.month, today.day) 
        self.start_urls = []
        self.start_urls.extend(
                [
                    'http://www.100ppi.com/news/list-14---1.html',
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
                        'Host' : 'www.100ppi.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch',
                    },
                )


    def parse_list_page(self, response):
        pdb.set_trace()
        sel = Selector(response)
        contentlist = sel.xpath('//div[@class="w640 fl"]//div[@class="list-c"]/ul/li')
        shouldNextPage = True 
        for row in contentlist:
            publish_date = row.xpath('span/text()').extract()[0]
            finalpageUrl = row.xpath('a[2]/@href').extract()[0]
            if not finalpageUrl.startswith('http'):
                finalpageUrl = 'http://www.100ppi.com/news' + finalpageUrl
            title = row.xpath('a[2]/text()').extract()[0]
            if publish_date.split(' ')[0]  != self.todayFilter:
                shouldNextPage = False
            else:
                item = CmscrawlItem() 
                item['title'] = title
                item['bc_id'] = finalpageUrl
                try:
                    item['publish_date'] = datetime.datetime.strptime(publish_date, '%Y-%m-%d %H:%M')
                except:
                    item['publish_date'] = datetime.datetime.strptime(self.todayFilter, '%Y-%m-%d')

                item['fromSite'] = u'www.100ppi.com'
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
                        'Host' : 'www.100ppi.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch',
                        'Referer': response.url,
                    },
                )

        pdb.set_trace()
        if not shouldNextPage:
            return

        nextPageUrls = sel.xpath('//div[@class="page-inc"]/a/@href').extract()
        if nextPageUrls:
            nextPageUrls = nextPageUrls[-1:]
        for url in nextPageUrls:
            bindip = random.choice(settings['IPPOOLS'])
            ua = random.choice(settings['USER_AGENTS'])
            yield Request(
                    url = url,
                    callback = self.parse_list_page,
                    meta = {'bindaddress' : (bindip, 0)},
                    headers = {
                        'User-Agent': ua,
                        'Upgrade-Insecure-Requests' : '1',
                        'Host' : 'www.100ppi.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch',
                        'Referer': response.url,
                    },
                )


    def parse_final_page(self, response):
        #pdb.set_trace()
        sel = Selector(response)
        item = response.meta['item']
        item['source'] = sel.xpath('//font[@class="redk"]/text()')
        item['author'] = u''
        item['content'] =sel.xpath('//div[@class="nd-c"]').extract()[0]
        item['imgs'] = sel.xpath('//div[@class="nd-c"]//img/@src').extract()
        yield item
