#encoding=gb18030
#-*- coding:gb18030-*-
import os
import sys
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import re

STATUS = {'STANDBY':0, 'OK':1, 'RETRY':2, 'FAILED':3}
TYPES = {'INVALID':-1, 'M1688':0, 'TMALL':1, 'TAOBAO':2}
ORACLE_SEARCH_LISTPAGE_STATUS = {'STANDBY':0, 'OK':1, 'FAILED':2}
ERR_CODE = {'OK':1, 'CLOSE':2, 'BLOCK':3, 'TEMP':4, 'ERROR': 5}
SLEEP_TIME = 10

def logInit(loglevel, log_file, backup_count=0, consoleshow=False):
    if not os.path.exists(log_file):
        dir_path, file_name = os.path.split(log_file)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
    fileTimeHandler = TimedRotatingFileHandler(log_file, "D", 10, backup_count)
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')
    fileTimeHandler.setFormatter(formatter)
    logging.getLogger('').addHandler(fileTimeHandler)
    logging.getLogger('').setLevel(loglevel)
    if consoleshow:
      console = logging.StreamHandler()
      console.setLevel(loglevel)
      console.setFormatter(formatter)
      logging.getLogger('').addHandler(console)

def daemonize(stdin='/dev/null',stdout= '/dev/null', stderr= 'dev/null'):
    #Perform first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  #first parent out
    except OSError, e:
        sys.stderr.write('fork #1 failed: (%d) %s\n' %(e.errno, e.strerror))
        sys.exit(1)

    os.chdir('/')
    os.umask(0)
    os.setsid()

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0) #second parent out
    except OSError, e:
        sys.stderr.write('fork #2 failed: (%d) %s]n' %(e.errno,e.strerror))
        sys.exit(1)

    for f in sys.stdout, sys.stderr: f.flush()
    si = file(stdin, 'r')
    so = file(stdout,'a+')
    se = file(stderr,'a+',0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def getUrlType(url):
    if url in ['http://apps.1688.com', 'http://i.alibaba.com', \
                'http://preview.alibaba.com', 'http://xp.1688.com', \
                'http://loginchina.alibaba.com', 'http://tiantai.1688.com']:
        return TYPES['INVALID']

    if re.findall(r'http[s]*://.*\.alibaba.com[/]*$', url) or \
            re.findall(r'http[s]*://.*\.1688.com[/]*$', url):
        return TYPES['M1688']

    if re.findall(r'http[s]*://.*\.tmall.com[/]*$', url):
        return TYPES['TMALL']

    if re.findall(r'http[s]*://.*\.taobao.com[/]*$', url):
        return TYPES['TAOBAO']

    return TYPES['INVALID']

def init_redis():
    import redis
    redis_hosts = [
        ('10.10.10.27', 6379),
        ('192.168.245.31', 7901),
        ('172.16.252.22', 6379),
        ('172.16.248.22', 6379)
    ]
    r = None
    for host, port in redis_hosts:
        redis_pool = redis.ConnectionPool(host=host, port=port, socket_timeout=2)
        r = redis.Redis(connection_pool = redis_pool)
        try:
            last_len = r.llen('ALI_COMPANY_KEYWORD_LIST')
            break
        except redis.exceptions.ConnectionError:
            continue

    return r

def get_errcode(status, jump_url):
    err_str = {
        '/wrongpage.html': ERR_CODE['CLOSE'],
        '/noshop.html': ERR_CODE['CLOSE'],
        '/close.html': ERR_CODE['CLOSE'],
        '/weidaoda.html': ERR_CODE['CLOSE'],
        '//wo.1688.com': ERR_CODE['CLOSE'],
        '/wgxj.html': ERR_CODE['CLOSE'],
        'login': ERR_CODE['BLOCK'],
        'anti': ERR_CODE['BLOCK'],
        '/deny.html': ERR_CODE['BLOCK'],
        'checkcodev': ERR_CODE['BLOCK'],
        'kylin': ERR_CODE['BLOCK']
    }

    if status == 404:
        return ERR_CODE['CLOSE']

    for k in err_str:
        if jump_url.find(k) >= 0:
            return err_str[k]
    print status
    return ERR_CODE['TEMP']
