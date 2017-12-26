#!/usr/bin/env python
# encoding: utf-8
# -*- coding: UTF-8 -*-

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium import selenium
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import os
import sys 
import pdb 
import time
import datetime

from scrapy import Selector
import xlrd
import urllib
import logging
import json
from PIL import Image
from codeCheck import PicRecognise
import zlib
import time

import pymongo
from pymongo import MongoClient
import random

reload(sys)
sys.setdefaultencoding('UTF-8')


def getId(mongodbConn):
    if not mongodbConn:
        return
    if not isinstance(mongodbConn, pymongo.MongoClient):
        return

    db = mongodbConn['chinabidding']
    collection = db['autoId']
    ret = collection.find_and_modify({"name" : "AutoId"}, {"$inc" : {"count" : 1}})
    return int(ret['count'])

def DupFilted(mongodbConn, url):
    if not mongodbConn:
        return
    if not isinstance(mongodbConn, pymongo.MongoClient):
        return

    db = mongodbConn['chinabidding']
    collection = db['todayFetchedUrls']
    count = collection.count({"bc_id" : url})
    if count == 0:
        return False
    return True

def insertFetchedUrl(mongodbConn, url):
    if not mongodbConn:
        return
    if not isinstance(mongodbConn, pymongo.MongoClient):
        return

    db = mongodbConn['chinabidding']
    collection = db['todayFetchedUrls']
    collection.insert({'bc_id' : url})


def insertMongodb(mongodbConn, bc_id, content):
    #pdb.set_trace()
    if not mongodbConn:
        return
    if not isinstance(mongodbConn, pymongo.MongoClient):
        return

    countId =  getId(mongodbConn)
    if not countId:
        return
    #CompressedContent = zlib.compress(content)
    db = mongodbConn['chinabidding']
    collection = db['content']
    collection.insert({'content' : content, 'bc_id' : bc_id, 'id' : countId})
    insertFetchedUrl(mongodbConn, bc_id)
    logging.info("insert url {0:s} page content to mongodb success!".format(bc_id))


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
    mongodbConn = MongoClient('192.168.60.64:10010,192.168.60.65:10010,192.168.60.4:10010')
    today = datetime.datetime.today()
    logging.basicConfig(level = logging.DEBUG,
            format = '%(asctime)s - %(levelname)s - [process: %(process)d, thread: %(thread)d] - %(message)s',
            filename = './logs/{0:04d}-{1:02d}-{2:02d}'.format(today.year, today.month, today.day),
            filemode = 'w',
            datefmt = '%a, %d %b %Y %H:%M:%S')

    browser = None
    tryCount = 3
    while tryCount > 0:
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap['phantomjs.page.setting.user_agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
        try:
            #browser = webdriver.PhantomJS()
            #browser = webdriver.PhantomJS(executable_path='F:\phantomjsz_windows\phantomjs_windows\bin\phantomjs', desired_capabilities = dcap)
            browser = webdriver.Chrome(executable_path='C:\Documents and Settings\Administrator\Local Settings\Application Data\Google\Chrome\Application\chromedriver.exe', desired_capabilities = dcap)
        except Exception, err:
            print err.message
            logging.error('loading webDriver error!')
            tryCount = tryCount - 1
            continue
        wait = ui.WebDriverWait(browser, 30)
        #login
        browser.get('http://www.chinabidding.cn/cblcn/member.login/login')
        browser.maximize_window()
        browser.save_screenshot('aa.png')
        imgelement = browser.find_element_by_xpath('//*[@id="img_random"]')
        location = imgelement.location
        size = imgelement.size
        rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']), int(location['y'] + size['height']))
        i = Image.open('aa.png')
        frame4 = i.crop(rangle)
        frame4.save('frame.png')
        #uuYun
        picrecognise = PicRecognise()
        try:
            checkedResult = picrecognise.getRecogResult('frame.png')
        except:
            browser.quit()
            tryCount = tryCount - 1
            logging.error('get codeCheck error,try again, tryCount:{0:d}'.format(tryCount))
            continue
        coordinate  = checkedResult[1]
        ##login in 
        elem_username = wait.until(lambda browser: browser.find_element_by_xpath('//*[@id="u_name"]'))
        elem_username.send_keys('hcxf119')
        elem_username = wait.until(lambda browser: browser.find_element_by_xpath('//*[@id="u_pwd1"]'))
        elem_username.send_keys('aaa666888')

        elem_code = wait.until(lambda browser: browser.find_element_by_xpath('//*[@id="yzm"]'))
        elem_code.send_keys(coordinate)

        #click 
        try:
            action_chains = ActionChains(browser)
            action_chains.click(browser.find_element_by_xpath('/html/body/div/div[2]/div[2]/div[3]/div[1]')).release().perform()
        except:
            browser.quit()
            tryCount = tryCount - 1
            continue

        if browser.current_url == u'http://www.chinabidding.cn/':
            logging.info('login success!')
            break
        tryCount = tryCount - 1
        
    #dowork now
    browser.get('http://www.chinabidding.cn/search/searchzbw/search2?keywords=%E6%B6%88%E9%98%B2&categoryid=&areaid=&b_date=day&table_type=1000')
    content = browser.page_source
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
        time.sleep(60)
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

    #pdb.set_trace()
    for url in fetchFinalUrls:
        time.sleep(random.choice([58, 30, 48, 60, 20, 45]))
        if not url.startswith('http://'):
            url = 'http://www.chinabidding.cn/' + url
        browser.get(url)
        bc_id = browser.current_url
        if DupFilted(mongodbConn, bc_id):
            logging.error('url : {0:s} has fetched already, ignore!'.format(bc_id))
            continue

        content = browser.page_source
        insertMongodb(mongodbConn, bc_id, content)

    browser.quit()

