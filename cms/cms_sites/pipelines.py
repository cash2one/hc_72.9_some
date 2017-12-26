# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pyspider.result import ResultWorker

#from imgClient import ImgClient
import logging
import sys
import pdb
import cx_Oracle
import pymongo
import datetime
import os


#reload(sys)
#sys.setdefaultencoding("utf-8")

os.system('export LANG=zh_CN.GB18030')
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.ZHS16GBK'

ORACLE_DBS = {
	'gift' : 'gift/jk7lm9nc@192.168.245.31:8009/infodb3',
	'textile' : 'textile/jk7lm9nc@192.168.245.31:8009/infodb3',
	'machine' : 'machine/jk7lm9nc@192.168.245.31:8009/infodb3',
	'home' : 'home/jk7lm9nc@192.168.245.31:8009/infodb3',
	'printing' : 'printing/jk7lm9nc@192.168.245.31:8009/infodb3',
	'cloth' : 'cloth/jk7lm9nc@192.168.245.31:8009/infodb3',
	'wujin' : 'wujin/jk7lm9nc@192.168.245.31:8010/infodb1',
	'bm' : 'bm/jk7lm9nc@192.168.245.31:8010/infodb1',
    'motor' : 'motor/jk7lm9nc@192.168.245.31:8009/infodb3',
    'fj' : 'fj/jk7lm9nc@192.168.245.31:8009/infodb3',
    'instrument' : 'instrument/jk7lm9nc@192.168.245.31:8009/infodb3',
    'motors' : 'motors/jk7lm9nc@192.168.245.31:8009/infodb3',
    'liantiao' : 'liantiao/jk7lm9nc@192.168.245.31:8009/infodb3',
    'chilun' : 'chilun/jk7lm9nc@192.168.245.31:8009/infodb3',
    'jxjg' : 'jxjg/jk7lm9nc@192.168.245.31:8009/infodb3',
    'robot' : 'robot/jk7lm9nc@192.168.245.31:8009/infodb3',
}

INSERT_SQL=u""\
u"insert into info_item(II_ID, TITLE, CONTENT, INFOSOURCE, INPUT_DATE, AUTHOR, INFO_STATION, INFO_CLS, INFO_ORIGIN, INFOSOURCE_WEB) "\
u"values(:ID, :TITLE, :CONTENT, :INFOSOURCE, :INPUT_DATE, :AUTHOR, :INFO_STATION, :INFO_CLS, :INFO_ORIGIN, :INFOSOURCE_WEB)"

RELAGED_INSERT_SQL=u""\
u"insert into info_class(INC_ID, II_ID, CLSID, INFO_CLS, INFO_STATION)values(info_class_seq.nextval, {0:d}, '{1:s}', '{1:s}', '5')"




class CmscrawlPipeline(ResultWorker):
    def __init__(self, resultdb, inqueue):
        #pdb.set_trace()
        super(CmscrawlPipeline, self).__init__(resultdb, inqueue)
        self.oracleConn = None
        self.oracleConnDict = {}
        for key in ORACLE_DBS:
            if key not in self.oracleConnDict:
                self.oracleConnDict[key] = None
            self.oracleConnDict[key] = cx_Oracle.connect(ORACLE_DBS[key])
        #self.imgClient = ImgClient(
        #    PIC_THRIFT_SERVER_IP,
        #    PIC_THRIFT_SERVER_PORT)

    def on_result(self, task, result):
        if not result:
            return
        info = {}
        info['title'] = result.get('title', u'')
        info['author'] = result.get('author', u'')
        info['source'] = result.get('source', u'')
        info['fromSite'] = result.get('source_site', u'')
        info['content'] = result.get('content', u'')
        info['bc_id'] = result.get('url', u'')
        info['publish_date'] = result.get('publish_date', datetime.datetime.now())
        info['imgs'] = result.get('imgs', u'')
        info['types'] = result['types']
        info['info_cls'] = result['info_cls']
        info['info_origin'] = result['info_origin']
        self.insertOracle(self.oracleConnDict[info['types']], info)

    def getNextId(self, conn, types):
        if not conn:
            return False
        while True:
            try:
                cr = conn.cursor()
                ret = cr.execute('select info_item_seq.nextval from sys.dual').fetchone()
                cr.close()
                print ret[0]
                return ret[0]
            except Exception, e:
                if str(e).find('ORA-03114') >= 0:
                    conn = cx_Oracle.connect(ORACLE_DBS[types])
                    self.oracleConnDict[types] = conn
                else:
                    raise

    #def insertOracle(conn, bc_id, title, publish_date, source, content, contentIndex, mongodbConn):
    def insertOracle(self, conn, info):
        #pdb.set_trace()
        if not conn:
            return

        index = self.getNextId(conn, info['types'])
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
                    TITLE = info.get('title', u''),
                    CONTENT = info.get('content', u''),
                    INFOSOURCE = info.get('source', u''),
                    INPUT_DATE = datetime.datetime.now(),
                    AUTHOR = info['author'],
                    INFO_STATION = 1,
                    INFO_CLS = info['info_cls'],
                    INFO_ORIGIN = info['info_origin'],
                    INFOSOURCE_WEB = info['bc_id'] 
            )
    
            conn.commit()
            cr.close()
            logging.info('=========insert Oracle info_db: OK : url : %s' %(info['bc_id']))
        except Exception, err:
            logging.info('=========insert Oracle info_db:url : %s,  ERROR %s' %(info['bc_id'], str(err).decode('GBK')))
            return 
        self.insertRelatedTbl(conn, index, info['info_cls'])
    
    
    def insertRelatedTbl(self, conn, ii_id, info_cls):
        #pdb.set_trace()
        if not conn:
            return
        try:
            cr = conn.cursor()
            cr.execute(RELAGED_INSERT_SQL.format(ii_id, info_cls))
            conn.commit()
            cr.close()
        except Exception, err:
            logging.info('=========insert Oracle info_class:ii_id : %d,  ERROR %s' %(ii_id, str(err).decode('GBK')))
            pass
    
    def quit(self):
        super(CmscrawlPipeline, self).quit()
        self.oracleConn.close()


if __name__ == '__main__':
    pipe = CmscrawlPipeline() 
