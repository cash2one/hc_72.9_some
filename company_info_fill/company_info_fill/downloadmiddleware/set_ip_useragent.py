#!/usr/bin/python
from scrapy import log
#-*-coding:utf-8-*-

import random
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware
from scrapy.http import TextResponse

class IpAndUserAgentMiddleware(UserAgentMiddleware):
    """
        a useragent middleware which rotate the user agent when crawl websites
        
        if you set the USER_AGENT_LIST in settings,the rotate with it,if not,then use the default user_agent_list attribute instead.
    """

    #the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape
    #for more user agent strings,you can find it in http://www.useragentstring.com/pages/useragentstring.php

    def __init__(self, useragent_list, ip_list):
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17'
        self.ip= '127.0.0.1'
        self.useragent_list = useragent_list
        self.ip_list = ip_list

    @classmethod 
    def from_crawler(cls, crawler):
        return cls(
                    crawler.settings.get('USERAGENT_LIST'),
                    crawler.settings.get('IP_LIST')
                )

    def process_request(self, request, spider):
        if self.useragent_list:
            self.user_agent = random.choice(self.useragent_list)
            request.headers.setdefault('User-Agent', self.user_agent)
        if self.ip_list:
            self.ip = random.choice(self.ip_list)
            request.meta['bindaddress'] = (self.ip, 0)

    def process_exception(self, request, exception, spider):
        request.meta['errmsg'] = str(exception)
        return TextResponse(
            url=request.url,
            status=110,
            request=request)

