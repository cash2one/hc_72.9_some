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

class citicsfSpider(Spider):
    name = 'citicsfSpider'
    allowed_domains = ['citicsf.com']


    def __init__(self, *args, **kwargs):
        super(citicsfSpider, self).__init__(*args, **kwargs)
        today = datetime.datetime.today()
        self.todayFilter = '{0:04d}-{1:02d}-{2:02d}'.format(today.year, today.month, today.day) 
        self.start_urls = []
        for i in range(1, 5):
            self.start_urls.append('http://www.citicsf.com/research/list.jsp?cid=19010101&hc=false&isTop=3&pn={0:d}'.format(i))


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
                        'Host' : 'www.citicsf.com',
                        'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding' : 'gzip, deflate, sdch'
                    },
                )


    def parse_list_page(self, response):
        pdb.set_trace()
        sel = Selector(response)
        contentlist = sel.xpath('//div[@id="list-right"]/ul')
        for row in contentlist:
            publish_date = row.xpath('li/span/text()').extract()[0].strip(' () ')
            finalpageUrl = row.xpath('li/a/@href').extract()[0]
            if not finalpageUrl.startswith('http'):
                finalpageUrl = 'http://www.citicsf.com' + finalpageUrl
            title = row.xpath('li/a/text()').extract()[0]
            if publish_date != self.todayFilter:
                continue    
            else:
                item = CmscrawlItem() 
                item['title'] = title
                item['bc_id'] = finalpageUrl
                try:
                    item['publish_date'] = datetime.datetime.strptime(publish_date, '(%Y-%m-%d)')
                except:
                    item['publish_date'] = datetime.datetime.strptime(self.todayFilter, '%Y-%m-%d')
                item['fromSite'] = u'www.citicsf.com'
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
                        'Host' : 'www.citicsf.com',
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
        item['source'] = u''
        item['title'] = item['title'].split(u'\u2014\u2014')[-1]
        item['content'] =sel.xpath('//div[@id="maincontent"]').extract()[0].replace(u'\xd8', u'').replace(u'\u2014', u'')
        item['imgs'] = sel.xpath('//div[@id="maincontent"]//img/@src').extract()
        yield item
