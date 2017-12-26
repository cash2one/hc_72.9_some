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

class cpciaSpider(Spider):
    name = 'cpciaSpider'
    allowed_domains = ['cpcia.com', 'cpcia.org.cn']


    def __init__(self, *args, **kwargs):
        super(cpciaSpider, self).__init__(*args, **kwargs)
        today = datetime.datetime.today()
        self.todayFilter = [
                '{0:04d}-{1:02d}-{2:02d}'.format(today.year, today.month, today.day),
                '{0:04d}-{1:02d}-{2:d}'.format(today.year, today.month, today.day),
                '{0:04d}-{1:d}-{2:02d}'.format(today.year, today.month, today.day), 
                '{0:04d}-{1:d}-{2:d}'.format(today.year, today.month, today.day), 
                '{0:04d}/{1:02d}/{2:02d}'.format(today.year, today.month, today.day),
                '{0:04d}/{1:02d}/{2:d}'.format(today.year, today.month, today.day),
                '{0:04d}/{1:d}/{2:02d}'.format(today.year, today.month, today.day), 
                '{0:04d}/{1:d}/{2:d}'.format(today.year, today.month, today.day), 
        ]
        self.start_urls = []
        self.start_urls.extend(
                [
                    'http://www.cpcia.org.cn/html/13/news_page1.html',
                    'http://www.cpcia.org.cn/news/hyfx/',
                    'http://www.cpcia.org.cn/html/16/news_page1.html',
                    'http://www.cpcia.org.cn/html/19/news_page1.html',
                    'http://www.cpcia.org.cn/news/index.asp?atype=127',
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
                        'Host' : 'www.cpcia.org.cn',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )


    def parse_list_page(self, response):
        pdb.set_trace()
        sel = Selector(response)
        contentlist = sel.xpath('//div[@class="page_list"]/ul/li')
        shouldNextPage = True 
        for row in contentlist:
            publish_date = row.xpath('span/text()').extract()[0]
            finalpageUrl = row.xpath('a/@href').extract()[0]
            if not finalpageUrl.startswith('http'):
                finalpageUrl = 'http://www.cpcia.org.cn' + finalpageUrl
            title = row.xpath('a/text()').extract()[0]
            if publish_date not in self.todayFilter:
                shouldNextPage = False
            else:
                item = CmscrawlItem() 
                item['title'] = title
                item['bc_id'] = finalpageUrl
                try:
                    item['publish_date'] = datetime.datetime.strptime(publish_date, '%Y-%m-%d')
                except:
                    item['publish_date'] = datetime.datetime.strptime(self.todayFilter, '%Y-%m-%d')

                item['fromSite'] = u'www.cpcia.org.cn'
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
                        'Host' : 'www.cpcia.org.cn',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )

        pdb.set_trace()
        if not shouldNextPage:
            return

        nextPageUrls = None
        if u'hyfx' not in response.url:
            nextPageUrls = sel.xpath('//div[@class="page_info"]/a/@href').extract()
            if not nextPageUrls:
                nextPageUrls = nextPageUrls[-1:]
        else:
            nextPageUrls = sel.xpath('//div[@class="page_info"]/ul/li/a/@href').extract()
            if not nextPageUrls:
                nextPageUrls = nextPageUrls[-2][-1:]
        for url in nextPageUrls:
            bindip = random.choice(settings['IPPOOLS'])
            ua = random.choice(settings['USER_AGENTS'])
            if not url.startswith('http'):
                url = 'http://www.cpcia.org.cn' + url
            yield Request(
                    url = url,
                    callback = self.parse_list_page,
                    meta = {'bindaddress' : (bindip, 0)},
                    headers = {
                        'User-Agent': ua,
                        'Upgrade-Insecure-Requests' : '1',
                        'Host' : 'www.cpcia.org.cn',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )


    def parse_final_page(self, response):
        #pdb.set_trace()
        sel = Selector(response)
        item = response.meta['item']
        item['author'] = u''
        item['content'] =sel.xpath('//div[@class="content"]').extract()[0]
        item['imgs'] = sel.xpath('//div[@class="content"]//img/@src').extract()
        yield item
