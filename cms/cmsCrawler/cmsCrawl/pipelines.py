# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from imgClient import ImgClient
import logging
import sys 
import pdb 
import cx_Oracle
import pymongo
import datetime
import os

from pymongo import MongoClient

#reload(sys)
#sys.setdefaultencoding("utf-8")

#os.system('export LANG=zh_CN.GB18030')
#os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.ZHS16GBK'


class CmscrawlPipeline(object):
    def __init__(self):
        self.logger = logging.getLogger('pipeline')
        self.oracleConn = None
        try:
            connstr = "%s/%s@%s/%s" % (
                    settings['ORACLE_SERVER_USERNAME'],
                    settings['ORACLE_SERVER_PASSWORD'],
                    settings['ORACLE_SERVER_ADDR'],
                    settings['ORACLE_SERVER_DBNAME'])
            self.oracleConn = cx_Oracle.connect(connstr)
        except Exception, err:
            self.logger.error("Connection Oracle Error!: %s" % (err,))
        self.imgClient = ImgClient(
            settings['PIC_THRIFT_SERVER_IP'],
            settings['PIC_THRIFT_SERVER_PORT'])


    def process_item(self, item, spider):
        pdb.set_trace()
        index = self.getNextId()
        try:
            cr = self.oracleConn.cursor()
            cr.setinputsizes(
                    ID = cx_Oracle.NUMBER,
                    ARTICLE_NAME = cx_Oracle.STRING,
                    ARTICLE_AUTHOR = cx_Oracle.STRING,
                    SOURCE = cx_Oracle.STRING,
                    SOURCE_WEB = cx_Oracle.STRING,
                    ARTICLE_CONTENT = cx_Oracle.CLOB,
                    ARTICLE_URL = cx_Oracle.STRING,
                    PUBLISH_TIME = cx_Oracle.DATETIME
                    )
            cr.execute(settings['ARTICLE_INSERTSQL'],
                    ID = index,
                    ARTICLE_NAME = item.get('title', u''),
                    ARTICLE_AUTHOR = item.get('author', u''), 
                    SOURCE = item.get('source', u''),
                    SOURCE_WEB = item.get('fromSite', u''),
                    ARTICLE_CONTENT = item.get('content', u''),
                    ARTICLE_URL = item.get('bc_id', u''),
                    PUBLISH_TIME = item.get('publish_date', datetime.datetime.now())
                    )
            self.oracleConn.commit()
            if item['imgs']:
                self.saveImgs(item['bc_id'], item['imgs'])
            return item
        except Exception, err:
            self.logger.error("Connection Oracle Error!: %s" % (err,))
            return item



    def getNextId(self):
        pdb.set_trace()
        if not self.oracleConn:
            return None
        cr = self.oracleConn.cursor()
        ret = cr.execute('select CHEMICAL_ARTICLE_TBL_SEQ.NEXTVAL from sys.dual')
        index = 0
        for ele in ret:
            index = ele[0]
        cr.close()
        return index



    def saveImgs(self, bc_id, imgList):
        pdb.set_trace()
        for img in imgList:
            tryCount = 0
            while tryCount < 3: 
                hcimg = self.imgClient.getHcImgUrl(img)
                tryCount += 1
                if hcimg:
                    self.logger.info('after fetch url: %s, img: %s save to mongodb ok!' % (bc_id, img, ))
                    break
                else:
                    self.logger.info('after fetch url: %s, img: %s save to mongodb ERROR! count : %d' % (bc_id, img, tryCount))
                    continue
            self.doSaveImgToOracle(bc_id, img, hcimg)

    def doSaveImgToOracle(self, bc_id, img, hcimg, ):
        #pdb.set_trace()
        cr = None
        if hcimg:
            try:
                exesql = settings['PIC_INSERTSQL'].format(bc_id, img, hcimg)
                cr = self.oracleConn.cursor()
                cr.execute(exesql)
                self.oracleConn.commit()
                cr.close()
                self.logger.info("ORACLE: execute sql: %s OK!" % (exesql,)) 
            except Exception, err:
                self.logger.info("after fetch url: %s , but save img: %s  and hcimg: %s to oracle error: %s!" % (bc_id, img, hcimg, str(err).decode('GBK')))
