#!/usr/bin/env python
# encoding: utf-8
# -*- coding: UTF-8 -*-


import sys
import os
import cx_Oracle
import pymongo
from pymongo import MongoClient
from scrapy import Selector
import pdb
import logging
import datetime
import re
import w3lib
import w3lib.html
import time
import os

#reload(sys)
#sys.setdefaultencoding('UTF-8')
import datetime
os.system('export LANG=zh_CN.GB18030')
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.ZHS16GBK'

#def deleteContent(mongodbConn, index):
#    if not mongodbConn:
#        return
#    if not isinstance(mongodbConn, pymongo.MongoClient):
#        return
#
#    db = mongodbConn['chinabidding']
#    collection = db['content']
#    collection.remove({'id' : index})
#ORACLE_SERVER_USERNAME = 'fire'
#ORACLE_SERVER_PASSWORD = 'jk7lm9nc'
#ORACLE_SERVER_ADDR = '192.168.119.15:1521'
#ORACLE_SERVER_DBNAME = 'infodb3'

ORACLE_SERVER_USERNAME = 'cer'
ORACLE_SERVER_PASSWORD = 'jk7lm9nc'
ORACLE_SERVER_ADDR = '192.168.245.31:8010'
ORACLE_SERVER_DBNAME = 'infodb1'

ORACLE_DICT = {
        'fire' : 'fire/jk7lm9nc@192.168.119.15:1521/infodb3',
        'cer' : 'cer/jk7lm9nc@192.168.245.31:8010/infodb1',
}

#INSERT_SQL=u"insert into INFO_ITEM(II_ID, TITLE, CONTENT, INFOSOURCE, MAKE_DATE, AUTHOR, INFO_STATION, INFO_CLS) values(info_item_seq.nextval, '{0:s}', \"{1:s}\", '{2:s}', to_date('2016-08-15', 'yyyy-mm-dd'),'{3:s}', 1, '001014021')"
#INSERT_SQL = u"insert into INFO_ITEM(II_ID, TITLE, CONTENT, INFOSOURCE, MAKE_DATE, AUTHOR, INFO_STATION, INFO_CLS) values(info_item_seq.nextval, :TITLE, :CONTENT, :INFOSOURCE , to_date(:MAKE_DATE, 'yyyy-mm-dd'), :AUTHOR, 1, '001014021')"
INSERT_SQL = u"insert into INFO_ITEM(II_ID, TITLE, CONTENT, INFOSOURCE, INPUT_DATE, AUTHOR, INFO_STATION, INFO_CLS, INFO_ORIGIN, INFOSOURCE_WEB) values(:ID, :TITLE, :CONTENT, :INFOSOURCE , :INPUT_DATE, :AUTHOR, :INFO_STATION, :INFO_CLS, :INFO_ORIGIN, :INFOSOURCE_WEB)"
RELAGED_INSERT_SQL = "insert into info_class(INC_ID, II_ID, CLSID, SORT_VAL, MAKE_DATE, INFO_CLS, INFO_STATION) values(info_class_seq.nextval, {0:d}, '{1:s}', 1000, SYSDATE, '{1:s}', 1)"

def getNextId(conn):
    if not conn:
        return 
    cr = conn.cursor()
    ret = cr.execute('select info_item_seq.nextval from sys.dual')
    index = 0
    for ele in ret:
        index = ele[0]
    return index

def updateContentState(conn, index):
    if not conn:
        return
    if not isinstance(conn, pymongo.MongoClient):
        return
    db = conn['chinabidding']
    collection = db['content']
    collection.update({'id' : index}, {'$set' : {'status' : 2}})

def removeDone(conn):
    if not conn:
        return
    if not isinstance(conn, pymongo.MongoClient):
        return
    db = conn['chinabidding']
    collection = db['content']
    collection.remove({'status' : 2})

                #INFO_CLS = u'001014021',
def insertOracle(conn, bc_id, title, publish_date, source, content, contentIndex, mongodbConn, info_cls):
    #pdb.set_trace()
    today = datetime.datetime.today()
    if not conn:
        return

    index = getNextId(conn)
    try:
        cr = conn.cursor()
        cr.setinputsizes(
                ID = cx_Oracle.NUMBER,
                TITLE = cx_Oracle.STRING,
                CONTENT = cx_Oracle.CLOB,
                INFOSOURCE = cx_Oracle.STRING,
                INPUT_DATE = cx_Oracle.Date,
                AUTHOR = cx_Oracle.STRING,
                INFO_STATION = cx_Oracle.NUMBER,
                INFO_CLS = cx_Oracle.STRING,
                INFO_ORIGIN = cx_Oracle.STRING,
                INFOSOURCE_WEB = cx_Oracle.STRING,
        )
        cr.execute(INSERT_SQL, 
                ID = index,
                TITLE = title, 
                CONTENT = content,
                INFOSOURCE = source,
                INPUT_DATE = datetime.date(year = today.year, month=today.month, day=today.day),
                AUTHOR = u'',
                INFO_STATION = 1,
                #INFO_CLS = u'001012',
                INFO_CLS = info_cls,
                INFO_ORIGIN = u'信息采集',
                INFOSOURCE_WEB = bc_id
        )

        conn.commit()
        cr.close()
    except Exception, err:
        return 
    #insertRelatedTbl(conn, index, '001014021')
    #insertRelatedTbl(conn, index, '001012')
    insertRelatedTbl(conn, index, info_cls)
    updateContentState(mongodbConn, contentIndex)


def insertRelatedTbl(conn, ii_id, info_cls):
    #pdb.set_trace()
    if not conn:
        return
    try:
        cr = conn.cursor()
        cr.execute(RELAGED_INSERT_SQL.format(ii_id, info_cls))
        conn.commit()
        cr.close()
    except Exception, err:
        pass


if __name__ == '__main__':
    #pdb.set_trace()
    oracleFetchConnDict = {}
    while True:
        today = datetime.datetime.today()
        logging.basicConfig(level = logging.DEBUG,
                format = '%(asctime)s - %(levelname)s - [process: %(process)d, thread: %(thread)d] - %(message)s',
                filename = '/working/zhangjie/Work_scrapy/chinabidding/crawler/logs/{0:04d}-{1:02d}-{2:02d}.log'.format(today.year, today.month, today.day),
                filemode = 'w',
                datefmt = '%a, %d %b %Y %H:%M:%S')

        #try:
        #    connstr = "%s/%s@%s/%s" % (
        #            ORACLE_SERVER_USERNAME,
        #            ORACLE_SERVER_PASSWORD,
        #            ORACLE_SERVER_ADDR,
        #            ORACLE_SERVER_DBNAME)
        #    oracleFetchConn = cx_Oracle.connect(connstr)
        #except Exception, err:
        #    logging.error("Manager fetch aligoUrl Connection Oracle Error!: %s" % (err,))
        #    time.sleep(600)
        #    continue
        for key in ORACLE_DICT:
            if key not in oracleFetchConnDict:
                oracleFetchConnDict[key] = None
            oracleFetchConnDict[key] = cx_Oracle.connect(ORACLE_DICT[key])

        mongodbConn = MongoClient('192.168.60.64:10010,192.168.60.65:10010,192.168.60.4:10010')

        db = mongodbConn['chinabidding']
        collection = db['content']
        ret = collection.find({'status' : {'$exists' : False}})

        for ele in ret:
            try:
                index = ele['id']
                bc_id = ele['bc_id']
                content = ele['content']
                info_cls = ele['info_cls']
                db_name = ele['db_name']
                sel = Selector(text = content)
                #title = sel.xpath('//div[@class="f_l z_nr"]//div[@class="f_l ll_bt fw_b"]/text()').extract()[0]
                title = sel.xpath('//div[@class="cen_xq c_xq_b"]/h1[@class="da_biao"]/text()').extract()[0].replace(u'\xa0', u'')
                #publish_date = re.split('[\r\n\t\ ]+', sel.xpath('//div[@class="f_l z_nr"]//div[@class="f_l ll_sj"]/text()').extract()[0].strip())
                publish_date = sel.xpath('//div[@class="fl xiab_1"]/span/text()').extract()[0] 
                #source = sel.xpath('//div[@class="f_l z_nr"]//div[@class="f_l ll_sj"]/span/text()').extract()[0]
                source = sel.xpath('//div[@class="fl xiab_1"]/a[2]/@title').extract()
                source = source[0].replace(u'\xa0', u'') if source else u''
                #content = sel.xpath('//div[@class="f_l z_nr"]//div[@class="f_l ll_nr1"]').extract()[0]
                content = sel.xpath('//div[@class="xq_nr"]').extract()[0]
                content = w3lib.html.remove_tags(content, which_ones=('div', )).replace(u'\xa0', u'')
                insertOracle(oracleFetchConnDict[db_name], bc_id, title, publish_date, source, content, index, mongodbConn, info_cls)
            except:
                continue
        removeDone(mongodbConn)
        #break
        time.sleep(3600)




