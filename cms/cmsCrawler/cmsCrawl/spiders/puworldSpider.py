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

class puworldSpider(Spider):
    name = 'puworldSpider'
    allowed_domains = ['news.puworld.com', 'puworld.com']


    def __init__(self, *args, **kwargs):
        super(puworldSpider, self).__init__(*args, **kwargs)
        today = datetime.datetime.today()
        self.todayFilter = '{0:04d}-{1:02d}-{2:02d}'.format(today.year, today.month, today.day) 
        self.start_urls = []
        self.start_urls.extend(
                [
                    'http://news.puworld.com/newspuart-134.html',
                    'http://news.puworld.com/newspuart-137.html',
                    'http://news.puworld.com/newspuart-133.html',
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
                        'Host' : 'news.puworld.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )


    def parse_list_page(self, response):
        #pdb.set_trace()
        sel = Selector(response)
        contentlist = sel.xpath('//div[@class="Taymiddle left F14 t10"]/ul/li')
        shouldNextPage = True 
        for row in contentlist:
            publish_date = row.xpath('span/text()').extract()[0]
            finalpageUrl = row.xpath('span/a/@href').extract()[0]
            if not finalpageUrl.startswith('http'):
                finalpageUrl = 'http://news.puworld.com' + finalpageUrl
            title = row.xpath('span/a/text()').extract()[0]
            if publish_date != self.todayFilter:
                shouldNextPage = False
            else:
                item = CmscrawlItem() 
                item['title'] = title.strip()
                item['bc_id'] = finalpageUrl
                try:
                    item['publish_date'] = datetime.datetime.strptime(publish_date, '%Y-%m-%d')
                except:
                    item['publish_date'] = datetime.datetime.strptime(self.todayFilter, '%Y-%m-%d')
                item['fromSite'] = u'news.puworld.com'
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
                        'Host' : 'news.puworld.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )

        pdb.set_trace()
        if not shouldNextPage:
            return

        nextPageUrls = sel.xpath('//div[@class="page"]/a/@href').extract()
        if nextPageUrls:
            nextPageUrls = nextPageUrls[-1:]
        for url in nextPageUrls:
            bindip = random.choice(settings['IPPOOLS'])
            ua = random.choice(settings['USER_AGENTS'])
            if not url.startswith('http'):
                url = 'http://news.puworld.com' + url
            yield Request(
                    url = url,
                    callback = self.parse_list_page,
                    meta = {'bindaddress' : (bindip, 0)},
                    headers = {
                        'User-Agent': ua,
                        'Upgrade-Insecure-Requests' : '1',
                        'Host' : 'news.puworld.com',
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
        item['source'] = u''
        item['title'] = sel.xpath('//div[@class="L650 Textbox left"]//div[@class="Textwz"]/h5/text()').extract()[0].strip()
        item['content'] =sel.xpath('//div[@class="Textzw left F14 t10 over"]').extract()[0].strip()
        item['imgs'] = sel.xpath('//div[@class="Textzw left F14 t10 over"]//img/@src').extract()
        yield item
