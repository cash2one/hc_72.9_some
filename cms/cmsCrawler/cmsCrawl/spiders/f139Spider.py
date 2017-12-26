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
import w3lib
import w3lib.html


reload(sys)
sys.setdefaultencoding("utf-8")

class f139Spider(Spider):
    name = 'f139Spider'
    allowed_domains = ['f139.com', 'news.f139.com']


    def __init__(self, *args, **kwargs):
        super(f139Spider, self).__init__(*args, **kwargs)
        today = datetime.datetime.today()
        self.todayFilter = '{0:04d}-{1:02d}-{2:02d}'.format(today.year, today.month, today.day) 
        self.start_urls = []
        self.start_urls.extend(
                [
                    'http://news.f139.com/list.do?channelID=79&categoryID=6',
                ]
            )


    def start_requests(self):
        #pdb.set_trace()
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
                        'Host' : 'news.f139.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )


    def parse_list_page(self, response):
        #pdb.set_trace()
        sel = Selector(response)
        contentlist = sel.xpath('//div[@class="width635_2 left"]/div[@class="width635"]/ul/li')
        shouldNextPage = True 
        for row in contentlist:
            publish_date = row.xpath('span/text()').extract()[0].strip()
            finalpageUrl = row.xpath('a/@href').extract()[0].strip()
            if not finalpageUrl.startswith('http'):
                finalpageUrl = 'http://news.f139.com' + finalpageUrl
            title = row.xpath('a/text()').extract()[0].strip()
            if publish_date.split(' ')[0]  != self.todayFilter:
                shouldNextPage = False
            else:
                item = CmscrawlItem() 
                item['title'] = title
                item['bc_id'] = finalpageUrl
                try:
                    item['publish_date'] = datetime.datetime.strptime(publish_date, '%Y-%m-%d %H:%M%:%S')
                except:
                    item['publish_date'] = datetime.datetime.strptime(self.todayFilter, '%Y-%m-%d')

                item['fromSite'] = u'news.f139.com'
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
                        'Host' : 'news.f139.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )

        #pdb.set_trace()
        if not shouldNextPage:
            return

        nextPageUrls = sel.xpath('//*[@id="list"]/div/div/table/tr/td/form/a/@href').extract()
        if nextPageUrls:
            nextPageUrls = nextPageUrls[-2][:1]
        for url in nextPageUrls:
            bindip = random.choice(settings['IPPOOLS'])
            ua = random.choice(settings['USER_AGENTS'])
            if not url.startswith('http'):
                url = 'http://news.f139.com' + url
            yield Request(
                    url = url,
                    callback = self.parse_list_page,
                    meta = {'bindaddress' : (bindip, 0)},
                    headers = {
                        'User-Agent': ua,
                        'Upgrade-Insecure-Requests' : '1',
                        'Host' : 'news.f139.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )


    def parse_final_page(self, response):
        #pdb.set_trace()
        sel = Selector(response)
        item = response.meta['item']
        source = sel.xpath('//div[@class="width635_2 left"]/div[@class="width635"]//span[@class="cGray"]').extract()[0].strip()
        ret = source.split(u'\u6765\u6e90\uff1a')
        if ret and len(ret) >= 2:
            item['source'] = ret[1].strip()
            item['source'] = w3lib.html.remove_tags(item['source'])
        else:
            item['source'] = u'\u5bcc\u5b9d\u8d44\u8baf' 
        item['source'] = u'\u5bcc\u5b9d\u8d44\u8baf' 
        item['author'] = u''
        item['content'] =sel.xpath('//div[@class="width635_2 left"]//div[@class="text f14"]').extract()[0]
        item['imgs'] = sel.xpath('//div[@class="width635_2 left"]//div[@class="text f14"]/img/@src').extract()
        yield item
