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

class oiloneSpider(Spider):
    name = 'oiloneSpider'
    allowed_domains = ['oilone.cn']


    def __init__(self, *args, **kwargs):
        super(oiloneSpider, self).__init__(*args, **kwargs)
        today = datetime.datetime.today()
        self.todayFilter = '{0:04d}-{1:02d}-{2:02d}'.format(today.year, today.month, today.day) 
        self.start_urls = []
        self.start_urls.extend(
                [
                    'http://www.oilone.cn/list.jsp?classid=1252&typeid=1253',
                    'http://www.oilone.cn/list.jsp?classid=1252&typeid=1254',
                    'http://www.oilone.cn/list.jsp?classid=1252&typeid=1256',
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
                        'Host' : 'www.oilone.cn',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )


    def parse_list_page(self, response):
        pdb.set_trace()
        sel = Selector(response)
        contentlist = sel.xpath('//div[@class="listStyle7"]/dl')
        shouldNextPage = True 
        for row in contentlist:
            publish_date = row.xpath('dd/span/text()').extract()[0].replace(u'发布时间：', u'')
            finalpageUrl = row.xpath('dt/a/@href').extract()[0]
            title = row.xpath('dt/a/text()').extract()[0].strip()
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

                item['fromSite'] = u'www.oilone.cn'
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
                        'Host' : 'www.oilone.cn',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )

        pdb.set_trace()
        if not shouldNextPage:
            return

        nextPageUrls = sel.xpath('/html/body/div[10]/div[1]/div/div[2]/div/a[10]/@href').extract()
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
                        'Host' : 'www.oilone.cn',
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
        item['source'] = u'石油壹号网'
        item['title'] = item['title'].strip()
        item['content'] =sel.xpath('//div[@class="detailContent"]').extract()[0].replace(u'\xa0', u'').replace(u'\u2014', u'').replace(u'\xb7', u'').replace(u'\xd8', u'')
        item['imgs'] = sel.xpath('//div[@class="detailContent"]//img/@src').extract()
        yield item
