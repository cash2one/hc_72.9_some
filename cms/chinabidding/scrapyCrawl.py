#!/usr/bin/env python
# encoding: utf-8
# -*- coding: UTF-8 -*-

from ctypes import *
import sys
import os
import hashlib
import binascii
import random
import sys
import time
from ctypes import *
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import selenium
import selenium.webdriver.support.ui as ui
import time
import pdb
from scrapy import Selector
import xlrd
import datetime
import logging
from scrapy import Selector
import datetime
import re

import pymongo


def filterDate(url, date):
    #pdb.set_trace()
    shouldFetchNextPage  = True
    finalUrls  = []
    today = datetime.datetime.today()
    yesterday = today + datetime.timedelta(days = -1)
    todayStr = '{0:04d}-{1:02d}-{2:02d}'.format(today.year, today.month, today.day)
    result = zip(url, date)
    for ele in result:
        if ele[1] != todayStr:
            shouldFetchNextPage = False
        else:
            finalUrls.append(ele[0])
    return (finalUrls, shouldFetchNextPage)





if __name__ == '__main__':
    pdb.set_trace()
    logging.basicConfig(level = logging.DEBUG,
                        format = '%(asctime)s - %(levelname)s - [process: %(process)d, thread : %(thread)d] - %(message)s',
                        filename = './BaiduSaledCheck.log',
                        filemode = 'w',
                        datefmt = '%a, %d %b %Y %H:%M:%S')
    now_day = datetime.datetime.today()
    browser = None

    browser = webdriver.Chrome(executable_path='C:\Documents and Settings\Administrator\Local Settings\Application Data\Google\Chrome\Application\chromedriver.exe')
    wait = ui.WebDriverWait(browser,30)
    browser.get('http://www.chinabidding.cn/cblcn/member.login/login')
    browser.get('http://www.chinabidding.cn/search/searchzbw/search2?keywords=%E6%B6%88%E9%98%B2&categoryid=&areaid=&b_date=day&table_type=1000')
            #time.sleep(10)
    #elem_username = wait.until(lambda browser: browser.find_element_by_xpath('//*[@id="u_name"]'))
    #elem_username.send_keys('hcxf119')
    #elem_username = wait.until(lambda browser: browser.find_element_by_xpath('//*[@id="u_pwd1"]'))
    #elem_username.send_keys('aaa666888')
    #browser.find_element_by_id("index-bn").send_keys(Keys.ENTER)

    fetchFinalUrls = []
    sel = Selector(text = browser.page_source)
    finalUrls = sel.xpath('//table[@class="table_body"]/tbody/tr[re:test(@class, "listrow[0-9]+")]/td[2]/a/@href').extract()
    publish_date = sel.xpath('//table[@class="table_body"]/tbody/tr[re:test(@class, "listrow[0-9]+")]/td[7]/div/text()').extract()
    publish_date = [ele.split(' ')[0] for ele in publish_date]
    #pdb.set_trace()
    filtedUrl, shouldFetchNextPage = filterDate(finalUrls, publish_date)
    #pdb.set_trace()
    fetchFinalUrls.extend(filtedUrl)

    while shouldFetchNextPage:
        nextPageUrl = sel.xpath('//div[@id="pages"]/span/a/@href').extract()
        if nextPageUrl:
            nextPageUrl = nextPageUrl[-2]
        if not nextPageUrl.startswith('http://'):
            nextPageUrl = 'http://www.chinabidding.cn/' + nextPageUrl
        browser.get(nextPageUrl)
        sel = Selector(text = browser.page_source)
        finalUrls = sel.xpath('//table[@class="table_body"]/tbody/tr[re:test(@class, "listrow[0-9]+")]/td[2]/a/@href').extract()
        publish_date = sel.xpath('//table[@class="table_body"]/tbody/tr[re:test(@class, "listrow[0-9]+")]/td[7]/div/text()').extract()
        publish_date = [ele.split(' ')[0] for ele in publish_date]
        filtedUrl, shouldFetchNextPage = filterDate(finalUrls, publish_date)
        fetchFinalUrls.extend(filtedUrl)

    print fetchFinalUrls
    pdb.set_trace()
    for url in fetchFinalUrls:
        if not url.startswith('http://'):
            url = 'http://www.chinabidding.cn/' + url
        browser.get(url)
        sel = Selector(browser.page_source)
        bc_id = browser.current_url
        title = sel.xpath('//div[@class="f_l z_nr"]//div[@class="f_l ll_bt fw_b"]/text()').extract()[0]
        publish_date, source = re.split('[\r\n\t\ ]+', sel.xpath('//div[@class="f_l z_nr"]//div[@class="f_l ll_sj"]/text()').extract()[0].strip())
        content = sel.xpath('//div[@class="f_l z_nr"]//div[@class="f_l ll_nr1"]').extract()


