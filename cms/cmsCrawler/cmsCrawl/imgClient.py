#!/bin/env python
#encoding=utf-8
#-*- coding:utf-8-*-

from imgThrift.Img import FileStorageServiceThrift 
from imgThrift.Img.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import requests
import pdb
import logging


class ImgClient():
    def __init__(self, ip, port):
        self.ip =ip
        self.port = port
        self.logger = logging.getLogger('BaoPinCrawler')
    def download_img(self, url):
        #pdb.set_trace()
        response = requests.get(url, stream=True)
        return response.content
    def getHcImgUrl(self, url):
        #pdb.set_trace()
        try:
            socket = TSocket.TSocket(self.ip, self.port) 
            transport = TTransport.TBufferedTransport(socket)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            client = FileStorageServiceThrift.Client(protocol)
            socket.setTimeout(7000);
            #pdb.set_trace()
            transport.open()
            fileInfo = FileInfo()
            fileInfo.fileName = url.split('/')[-1:][0]
            fileInfo.fileContext = self.download_img(url)
            result = client.createFile([fileInfo])
            transport.close()
            self.logger.info("get hc url : %s  From url: %s Done" % (result[0].fileUrl, url))
            return result[0].fileUrl
        except Exception, e:
            self.logger.error("get hc url error From url: %s, errmsg: %s" % (url, e,))
            return ""



if __name__ == "__main__":

    client = ImgClient("192.168.44.161", 8332)
    #result = client.getHcImgUrl('http://static.grainger.cn/product_images_new/350/2A5/2013120216562159209.JPG')
    #result = client.getHcImgUrl('http://i04.c.aliimg.com/img/ibank/2014/740/434/1151434047_1268050241.jpg')
    result = client.getHcImgUrl('http://i00.c.aliimg.com/img/ibank/2015/386/861/1931168683_137054342.jpg')
    print(result)

