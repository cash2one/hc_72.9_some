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
import selenium.webdriver
import os
import sys 
import pdb 
import time
import datetime
from scrapy import Selector
import urllib
import logging
import json
from PIL import Image
from pic_recognise import PicRecognise
import zlib
import time
import pymongo
from pymongo import MongoClient
import random
from func import *

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


def insertMongodb(mongodbConn, bc_id, content, info_cls, db_name):
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
    collection.insert({'content' : content, 'bc_id' : bc_id, 'id' : countId, 'info_cls' : info_cls, 'db_name' : db_name})
    insertFetchedUrl(mongodbConn, bc_id)
    logging.info("insert url {0:s} page content to mongodb success!".format(bc_id))


def filterDate(url, date, filter_date):
    #pdb.set_trace()
    shouldFetchNextPage  = True
    finalUrls  = []
    dateStr = '{0:04d}-{1:02d}-{2:02d}'.format(filter_date.year, filter_date.month, filter_date.day)
    result = zip(url, date)
    for ele in result:
        if ele[1] != dateStr:
            shouldFetchNextPage = False
        else:
            finalUrls.append(ele[0])
    return (finalUrls, shouldFetchNextPage)

def browser_quit(browser, pid):
    try:
        if browser:
            browser.quit()
            os.kill(pid, 9)
    except Exception, e:
        pass
    finally:
        browser = None

CHINABIDDING_TIME_ZONE = [9, 11, 12, 15]

if __name__ == '__main__':
    #pdb.set_trace()

    mongodbConn = MongoClient('192.168.60.64:10010,192.168.60.65:10010,192.168.60.4:10010')
    today = datetime.datetime.today()
    dir_path, file_name = os.path.split(os.path.realpath(__file__))
    log_file = dir_path + '\\logs\\' + file_name.replace('.py', '.log')
    logInit(logging.INFO, log_file, 0, True)

    now = datetime.datetime.now()
    if int(now.hour) not in CHINABIDDING_TIME_ZONE:
        logging.info('{0:s} not in {1:s}'.format(now.strftime('%Y-%m-%d %H'), json.dumps(CHINABIDDING_TIME_ZONE)))
        next_hour = datetime.datetime.strptime((now + datetime.timedelta(seconds=+3600)).strftime('%Y-%m-%d %H:') + '00:00', '%Y-%m-%d %H:%M:%S')
        delta = next_hour - now
        logging.info('{0:s} not in {1:s}, will wait for {2:d} second'.format(now.strftime('%Y-%m-%d %H'), json.dumps(CHINABIDDING_TIME_ZONE), delta.seconds))
        time.sleep(delta.seconds)
        sys.exit(0)
    else:
        logging.info('{0:s}  in {1:s}'.format(now.strftime('%Y-%m-%d %H'), json.dumps(CHINABIDDING_TIME_ZONE)))
    browser = None
    tryCount = 3
    while tryCount > 0:
        try:
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap['phantomjs.page.setting.user_agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
            try:
                #browser = webdriver.PhantomJS()
                #browser = webdriver.PhantomJS(executable_path='F:\phantomjsz_windows\phantomjs_windows\bin\phantomjs', desired_capabilities = dcap)
                browser = webdriver.Chrome(executable_path='.\chromedriver_new.exe', desired_capabilities = dcap)

            except Exception, err:
                print err.message
                logging.error('loading webDriver error!')
                tryCount = tryCount - 1
                continue
            wait = ui.WebDriverWait(browser, 30)
        #login
            browser.get('http://www.chinabidding.cn/cblcn/member.login/login')
            browser.maximize_window()
            #划方块
            time.sleep(5)
            JMessageTag = None
            try:
                JMessageTag = browser.find_element_by_css_selector('#nc_1_n1z')
            except Exception, err:
                logging.error("不需要滑动方块！")
            if JMessageTag:
                try:
                    action_chains = ActionChains(browser)
                    action_chains.click_and_hold(JMessageTag).move_by_offset(258, 0).release().perform()
                except Exception, err:
                    logging.info("no block")

                #点击图片
                time.sleep(5)
                browser.save_screenshot('screen.png')
                imgelement = browser.find_element_by_css_selector('#WAF_NC_WRAPPER')
                location = imgelement.location
                size = imgelement.size
                rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),int(location['y'] + size['height']))
                i = Image.open('screen.png')
                rgb_i = i.convert('RGB')
                frame4 = rgb_i.crop(rangle)
                frame4.save('frame_hanzi.jpg')
                picrecognise = PicRecognise()
                checkedResult = picrecognise.getHanZiRecogResult('frame_hanzi.jpg')
                coordinate = checkedResult
                x,y = coordinate.split(',')
                action_chains = ActionChains(browser)
                action_chains.move_to_element_with_offset(browser.find_element_by_css_selector('#WAF_NC_WRAPPER'), int(x), int(y)).click().release().perform()
            #wait for 10
            time.sleep(10)
            #pdb.set_trace()
            picrecognise = PicRecognise()
            browser.save_screenshot('aa.png')
            imgelement = browser.find_element_by_xpath('//*[@id="img_random"]')
            location = imgelement.location
            size = imgelement.size
            rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']), int(location['y'] + size['height']))
            i = Image.open('aa.png')
            rgb_i = i.convert('RGB')
            frame4 = rgb_i.crop(rangle)
            frame4.save('frame.jpg')
            #uuYun

            try:
                checkedResult = picrecognise.PicRecognise('frame.jpg')
            except:
                browser_quit(browser, browser.service.process.pid)
                tryCount = tryCount - 1
                logging.error('get codeCheck error,try again, tryCount:{0:d}'.format(tryCount))
                continue
            coordinate  = checkedResult
            ##login in
            time.sleep(1)
            elem_username = wait.until(lambda browser: browser.find_element_by_xpath('//*[@id="u_name"]'))
            elem_username.send_keys('hcxf119')
            time.sleep(2)
            elem_username = wait.until(lambda browser: browser.find_element_by_xpath('//*[@id="u_pwd1"]'))
            #elem_username.send_keys('aaa666888')
            elem_username.send_keys('lius0803')
            time.sleep(3)
            elem_code = wait.until(lambda browser: browser.find_element_by_xpath('//*[@id="yzm"]'))
            elem_code.send_keys(coordinate)

        #click 
            try:
                action_chains = ActionChains(browser)
                action_chains.click(browser.find_element_by_xpath('/html/body/div/div[2]/div[2]/div[3]/div[1]')).release().perform()
            except:
                browser_quit(browser, browser.service.process.pid)
                tryCount = tryCount - 1
                continue

            if browser.current_url == u'https://www.chinabidding.cn/':
                logging.info('login success!')
                break
            tryCount = tryCount - 1
        except:
            pass
        #finally:
        #    if isinstance(browser, selenium.webdriver.chrome.webdriver.WebDriver):
        #        browser.quit()
        
    #dowork now
    time.sleep(10)
    #pdb.set_trace()
    targets = [
        ('https://www.chinabidding.cn/search/searchzbw/search2?keywords=%E6%B6%88%E9%98%B2&categoryid=&areaid=&b_date=day&table_type=1000', '001012', 'fire'),
        ('https://www.chinabidding.cn/search/searchzbw/search2?keywords=%E6%95%91%E6%8F%B4+&areaid=&categoryid=&b_date=month', '001001010001', 'cer'),
        ('https://www.chinabidding.cn/search/searchzbw/search2?keywords=%E9%98%B2%E6%97%B1&areaid=&categoryid=&b_date=month',  '001001010001', 'cer'),
        ('https://www.chinabidding.cn/search/searchzbw/search2?keywords=%E9%98%B2%E6%B1%9B&areaid=&categoryid=&b_date=month',  '001001010001', 'cer'),
        ('https://www.chinabidding.cn/search/searchzbw/search2?keywords=%E5%BA%94%E6%80%A5%E8%AE%BE%E5%A4%87&areaid=&categoryid=&b_date=month',  '001001010001', 'cer')
    ]
    for xiaofang_url, info_cls, db_name in targets:
        try:
            browser.get(xiaofang_url)
            content = browser.page_source
            fetchFinalUrls = []
            sel = Selector(text = browser.page_source)
            finalUrls = sel.xpath('//table[@class="table_body"]/tbody/tr[re:test(@class, "listrow[0-9]+")]/td[2]/a/@href').extract()
            publish_date = sel.xpath('//table[@class="table_body"]/tbody/tr[re:test(@class, "listrow[0-9]+")]/td[7]/div/text()').extract()
            publish_date = [ele.split(' ')[0] for ele in publish_date]
            today = datetime.datetime.today()
            yesterday = today - datetime.timedelta(days = 1)
            filter_date = today
            if db_name == 'fire':
                filter_date = yesterday
            filtedUrl, shouldFetchNextPage = filterDate(finalUrls, publish_date, filter_date)
            fetchFinalUrls.extend(filtedUrl)
            while shouldFetchNextPage:
                time.sleep(random.choice([40, 50, 30]))
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
                filtedUrl, shouldFetchNextPage = filterDate(finalUrls, publish_date, filter_date)
                if browser.current_url.find(nextPageUrl[-2]) > 0:
                    shouldFetchNextPage = False
                fetchFinalUrls.extend(filtedUrl)

            #pdb.set_trace()
            for url in fetchFinalUrls:
                if not url.startswith('http://'):
                    url = 'https://www.chinabidding.cn' + url
                if DupFilted(mongodbConn, url):
                    logging.error('url : {0:s} has fetched already, ignore!'.format(url))
                    continue
                #time.sleep(random.choice([58, 30, 48, 60, 20, 45]))
                #browser.implicitly_wait(10)
                browser.get(url)
                #myDynamicElement = browser.find_element_by_id('print_dom')
                time.sleep(10)
                if browser.current_url != url:
                    continue
                bc_id = browser.current_url


                content = browser.page_source
                sel = Selector(text = content)
                #login_status = sel.xpath('//div[@class="dl_k"]//p[@class="tx_mc_user_name"]/text()').extract()
                #if login_status and login_status[0] == 'hcxf119':
                #    pass
                #else:
                #    logging.error('===============login_status fail, should login!')
                #    if isinstance(browser, selenium.webdriver.chrome.webdriver.WebDriver):
                #        browser.quit()
                #    sys.exit(-1)
                insertMongodb(mongodbConn, bc_id, content, info_cls, db_name)
        except Exception, e:
            logging.error('something error! %s', str(e))
            if isinstance(browser, selenium.webdriver.chrome.webdriver.WebDriver):
                try:
                    browser_quit(browser, browser.service.process.pid)
                except:
                    pass

    if isinstance(browser, selenium.webdriver.chrome.webdriver.WebDriver):
        browser_quit(browser, browser.service.process.pid)

    now = datetime.datetime.now()
    next_hour = datetime.datetime.strptime((now + datetime.timedelta(seconds=+3600)).strftime('%Y-%m-%d %H:') + '00:00', '%Y-%m-%d %H:%M:%S')
    delta = next_hour - now
    time.sleep(delta.seconds)

