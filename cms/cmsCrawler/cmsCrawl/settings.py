# -*- coding: utf-8 -*-

# Scrapy settings for cmsCrawl project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'cmsCrawl'

SPIDER_MODULES = ['cmsCrawl.spiders']
NEWSPIDER_MODULE = 'cmsCrawl.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'cmsCrawl (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'cmsCrawl.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'cmsCrawl.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html

ITEM_PIPELINES = {
    'cmsCrawl.pipelines.CmscrawlPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
    "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
    "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
    "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
    "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
    "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
    "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
    "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
]

IPPOOLS = ['210.82.113.14', '210.82.113.15', '210.82.113.16', '210.82.113.17']

COOKIES={
        '21cp' : 'pgv_pvi=1607283712; pgv_si=s186267648; ASPSESSIONIDAACACDSD=PFIPOIPCJKFHCEEFIHEMOFCM; SessionID=a3d53944a130443bb5d8b8184a705eb5; Hm_lvt_5f657133fe3a739c5dfcc2e306267320=1472093942; Hm_lpvt_5f657133fe3a739c5dfcc2e306267320=1472095279',
        'sinopecnews' : "__utmt=1; __utma=168696867.1709325640.1472527644.1472527644.1472527644.1; __utmb=168696867.2.10.1472527644; __utmc=168696867; __utmz=168696867.1472527644.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_cc6817a41bad7f8ee9b15d9ab15e7ac8=1472527602; Hm_lpvt_cc6817a41bad7f8ee9b15d9ab15e7ac8={0:d}"
}

ORACLE_SERVER_ADDR = '192.168.44.250:1521'
ORACLE_SERVER_USERNAME = 'snatchdb'
ORACLE_SERVER_PASSWORD = 'bfdds06fd'
ORACLE_SERVER_DBNAME = 'prod'

#ORACLE_SERVER_ADDR = '192.168.44.131:1521'
#ORACLE_SERVER_USERNAME = 'cemmall'
#ORACLE_SERVER_PASSWORD = 'bfdds06fd'
#ORACLE_SERVER_DBNAME = 'trade'

PIC_THRIFT_SERVER_IP = "192.168.44.161"
PIC_THRIFT_SERVER_PORT = 8332

ARTICLE_INSERTSQL = 'insert into CHEMICAL_ARTICLE_TBL(ID, ARTICLE_NAME, ARTICLE_AUTHOR, SOURCE, SOURCE_WEB, ARTICLE_CONTENT, ARTICLE_URL, PUBLISH_TIME) VALUES(:ID, :ARTICLE_NAME, :ARTICLE_AUTHOR, :SOURCE, :SOURCE_WEB, :ARTICLE_CONTENT, :ARTICLE_URL, :PUBLISH_TIME)'
PIC_INSERTSQL = "insert into CHEMICAL_ARTICLE_PIC_TBL(ID, ARTICLE_URL, SOURCE_PIC_URL, HC_PIC_URL)VALUES(CHEMICAL_ARTICLE_PIC_TBL_SEQ.NEXTVAL,'{0:s}', '{1:s}', '{2:s}')"

