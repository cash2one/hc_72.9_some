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

class pla86Spider(Spider):
    name = 'pla86Spider'
    allowed_domains = ['86pla.com']


    def __init__(self, *args, **kwargs):
        super(pla86Spider, self).__init__(*args, **kwargs)
        today = datetime.datetime.today()
        self.todayFilter = '{0:04d}-{1:02d}-{2:02d}'.format(today.year, today.month, today.day) 
        self.start_urls = []
        self.start_urls.extend(
                [
                    'http://www.86pla.com/news/T14/list.html',
                    'http://www.86pla.com/news/T12/list.html',
                    'http://www.86pla.com/news/T9/list.html',
                    'http://www.86pla.com/news/T13/list.html',
                    'http://www.86pla.com/news/T10/list.html',
                    'http://www.86pla.com/news/T147/list.html',
                    'http://www.86pla.com/news/T5609/list.html',
                    'http://www.86pla.com/news/t15/list.html',
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
                        'Host' : 'www.86pla.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )


    def parse_list_page(self, response):
        #pdb.set_trace()
        sel = Selector(response)
        contentlist = sel.xpath('//div[@class="mainLeft"]/div[@class="techLeftList"]/dl')
        shouldNextPage = True 
        for row in contentlist:
            publish_date = row.xpath('dt/span/text()').extract()[0]
            finalpageUrl = row.xpath('dt/a/@href').extract()[0]
            if not finalpageUrl.startswith('http'):
                finalpageUrl = 'http://www.86pla.com' + finalpageUrl
            title = row.xpath('dt/a/text()').extract()[0]
            if publish_date != self.todayFilter:
                shouldNextPage = False
            else:
                item = CmscrawlItem() 
                item['title'] = title
                item['bc_id'] = finalpageUrl
                try:
                    item['publish_date'] = datetime.datetime.strptime(publish_date, '%Y-%m-%d')
                except:
                    item['publish_date'] = datetime.datetime.strptime(self.todayFilter, '%Y-%m-%d')

                item['fromSite'] = u'www.86pla.com'
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
                        'Host' : 'www.86pla.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )

        #pdb.set_trace()
        if not shouldNextPage:
            return

        nextPageUrls = sel.xpath('//div[@class="newspages"]/a/@href').extract()
        if nextPageUrls:
            nextPageUrls = nextPageUrls[-2][:-1]
        for url in nextPageUrls:
            bindip = random.choice(settings['IPPOOLS'])
            ua = random.choice(settings['USER_AGENTS'])
            if not url.startswith('http'):
                url = 'http://www.86pla.com' + url 
            yield Request(
                    url = url,
                    callback = self.parse_list_page,
                    meta = {'bindaddress' : (bindip, 0)},
                    headers = {
                        'User-Agent': ua,
                        'Upgrade-Insecure-Requests' : '1',
                        'Host' : 'www.86pla.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )


    def parse_final_page(self, response):
        pdb.set_trace()
        sel = Selector(response)
        item = response.meta['item']
        item['author'] = u''
        item['source'] = u'\u4e2d\u56fd\u5851\u6599\u673a\u68b0\u7f51'
        item['content'] =sel.xpath('//div[@class="newsShow"]').extract()[0].replace(u'\xa0', u'').replace(u'\u2014', u'').replace(u'\xb7', u'')
        item['imgs'] = sel.xpath('//div[@class="newsShow"]//img/@src').extract()
        yield item
