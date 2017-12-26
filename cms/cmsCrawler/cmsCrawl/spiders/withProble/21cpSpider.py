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

class cp21Spider(Spider):
    name = '21cpSpider'
    allowed_domains = ['info.21cp.com', '21cp.com']


    def __init__(self, *args, **kwargs):
        super(cp21Spider, self).__init__(*args, **kwargs)
        today = datetime.datetime.today()
        self.todayFilter = [
                '{0:04d}-{1:02d}-{2:02d}'.format(today.year, today.month, today.day),
                '{0:02d}-{1:02d}'.format(today.month, today.day), 
        ]
        self.start_urls = []
        self.start_urls.extend(
                [
                    'http://info.21cp.com/PP/Shichang/',
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
                        'Host' : 'info.21cp.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch',
                        'Cookie' : settings['COOKIES']['21cp'],
                        'Referer' : 'http://info.21cp.com/',
                    },
                )


    def parse_list_page(self, response):
        #pdb.set_trace()
        sel = Selector(response)
        contentlist = sel.xpath('//div[@class="borderTno fontSize14 list"]//tr')
        shouldNextPage = True 
        for row in contentlist:
            publish_date = row.xpath('td/font/text()').extract()[0]
            finalpageUrl = row.xpath('td/a/@href').extract()[0]
            title = row.xpath('td/a/text()').extract()[0]
            if publish_date in self.todayFilter:
                shouldNextPage = False
            else:
                item = CmscrawlItem() 
                item['title'] = title
                item['bc_id'] = finalpageUrl
                item['publish_date'] = publish_date
                item['fromSite'] = u'info.21cp.com'
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
                        'Host' : 'info.21cp.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch',
                        'Cookie' : settings['COOKIES']['21cp'],
                        'Referer' : response.url,
                    },
                )

        pdb.set_trace()
        if not shouldNextPage:
            return

        nextPageUrls = sel.xpath('//div[@class="showpage"]/a/@href').extract()
        if nextPageUrls:
            nextPageUrls = nextPageUrls[-2][-1:]
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
                        'Host' : 'info.21cp.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch',
                        'Cookie' : settings['COOKIES']['21cp'],
                        'Referer' : response.url,
                    },
                )


    def parse_final_page(self, response):
        #pdb.set_trace()
        sel = Selector(response)
        item = response.meta['item']
        item['publish_date'] = self.todayFilter[0] + ' ' + sel.xpath('//div[@class="mian_title"]/ul[@class="subctitle"]/li[1]').extract()[0].split(' ')[-1]
        item['source'] = u'中塑在线原创'
        item['author'] = u''
        item['content'] =sel.xpath('//div[@class="content"]').extract()[0]
        item['imgs'] = sel.xpath('//div[@class="content"]//img/@src').extract()
        yield item
