# -*- coding: utf-8 -*-
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
import logging
import pdb

from PIL import Image
reload(sys)
sys.setdefaultencoding('utf-8')
UUDLL=os.path.join(os.path.dirname(__file__), 'UUWiseHelper_x64.dll')

class PicRecognise():
    s_id  = 109525
    s_key = "3e5d3a91433148498af80f81aa3d4246"
    softVerifyKey="28195A79-EDC1-4B53-AE33-F562283B751A"
    user = c_wchar_p("guonana")
    passwd = c_wchar_p("22cf2e77")
    #UU = cdll.LoadLibrary(UUDLL)
    UU = CDLL(UUDLL)
    __recognizeByCodeTypeAndBytes = UU.uu_recognizeByCodeTypeAndBytesW
    __uu_recognizeByCodeTypeAndUrlA = UU.uu_recognizeByCodeTypeAndUrlA
    __uu_recognizeByCodeTypeAndUrlW = UU.uu_recognizeByCodeTypeAndUrlW
    __uu_recognizeByCodeTypeAndPathW = UU.uu_recognizeByCodeTypeAndPathW
    uu_easyRecognizeFileW = UU.uu_easyRecognizeFileW
    __setSoftInfo = UU.uu_setSoftInfoW
    __login = UU.uu_loginW
    #recognizeByCodeTypeAndPath = UU.uu_recognizeByCodeTypeAndPathW
    __getResult = UU.uu_getResultW
    __uploadFile = UU.uu_UploadFileW
    __getScore = UU.uu_getScoreW
    __checkAPi=UU.uu_CheckApiSignW
    def __int__(self):
        pass
    def getFileMd5(self,strFile):
        file = None;
        bRet = False;
        strMd5 = "";
        try:
            file = open(strFile, "rb");
            md5 = hashlib.md5();
            strRead = "";

            while True:
                strRead = file.read(8096);
                if not strRead:
                    break;
                md5.update(strRead);
            #read file finish
            bRet = True;
            strMd5 = md5.hexdigest();
        except:
            bRet = False;
        finally:
            if file:
                file.close()

        return [bRet, strMd5];

    def getFileCRC(self,filename):
        f = None;
        bRet = False;
        crc = 0;
        blocksize = 1024 * 64
        try:
                    f = open(filename, "rb")
                    str = f.read(blocksize)
                    while len(str) != 0:
                            crc = binascii.crc32(str,crc) & 0xffffffff
                            str = f.read(blocksize)
                    f.close()
                    bRet = True;
        except:
            print "compute file crc failed!"+filename
            return 0
        return [bRet, '%x' % crc];

    def checkResult(self,dllResult, s_id, softVerifyKey, codeid):
        bRet = False;
        print(dllResult);
        print(len(dllResult));
        if(len(dllResult) < 0):
            return [bRet, dllResult];
        items=dllResult.split('_')
        verify=items[0]
        code=items[1]

        localMd5=hashlib.md5('%d%s%d%s'%(s_id, softVerifyKey, codeid, (code.upper()))).hexdigest().upper()
        if(verify == localMd5):
            bRet = True;
            return [bRet, code];
        return [bRet, "校验结果失败"]

    def getUUScore(self):
        ret = self.__getScore(self.user, self.passwd)                            #获取用户当前剩余积分
        print('The Score of User : %s  is :%d' % (self.user.value, ret))

    def checkUU(self):
        dllMd5=self.getFileMd5(UUDLL)
        dllCRC32=self.getFileCRC(UUDLL)
        randChar=hashlib.md5(random.choice('abcdefghijklmnopqrstuvwxyz!@#$%^&*()')).hexdigest()
        checkStatus=hashlib.md5('%d%s%s%s%s'%(self.s_id,(self.softVerifyKey.upper()),(randChar.upper()),(dllMd5[1].upper()),(dllCRC32[1].upper()))).hexdigest()
        serverStatus=c_wchar_p("")
        self.__checkAPi(c_int(self.s_id), c_wchar_p(self.s_key.upper()),c_wchar_p(randChar.upper()),c_wchar_p(dllMd5[1].upper()),c_wchar_p(dllCRC32[1].upper()),serverStatus)
        if not (checkStatus == serverStatus.value):
            print("sorry, api file is modified")
            sys.exit(0)

    def loginUU(self):
        ret = self.__login(self.user, self.passwd)
        if ret > 0:
            print('login ok, user_id:%d' % ret)
        else:
            print('login error,errorCode:%d' %ret )
            sys.exit(0)

    def getRecogResult(self, path):
        result=c_wchar_p("                                              ")
        code_id = self.uu_easyRecognizeFileW(c_int(109525), c_wchar_p('3e5d3a91433148498af80f81aa3d4246'), c_wchar_p('guonana'), c_wchar_p('22cf2e77'),c_wchar_p(path),  c_int(1004), result)
        if code_id <= 0:
           print('get result error ,ErrorCode: %d' % code_id)
        else:
            checkedRes=self.checkResult(result.value, self.s_id, self.softVerifyKey, code_id);
            print("the resultID is :%d result is %s" % (code_id,checkedRes[1]))
            return checkedRes


if __name__ == '__main__':
    pdb.set_trace()
    picrecognise = PicRecognise()
    checkedResult = picrecognise.getRecogResult('frame.png')
    coordinate  = checkedResult[1]
