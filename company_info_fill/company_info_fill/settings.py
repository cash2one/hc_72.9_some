# -*- coding: utf-8 -*-

# Scrapy settings for company_info_fill project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'company_info_fill'

SPIDER_MODULES = ['company_info_fill.spiders']
NEWSPIDER_MODULE = 'company_info_fill.spiders'


HTTPERROR_ALLOW_ALL = True
DOWNLOAD_TIMEOUT = 10

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS=32

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
DEFAULT_REQUEST_HEADERS = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'zh-CN,zh;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch',
		'Cache-Control': 'max-age=0',
		'Connection': 'keep-alive',
        'Cookie': 'ASPSESSIONIDQSABSCDR=ALCLAPJCGINJBJDLGIDKNBGL',
		'Host': 'www.sxjdcmy.com',
		'Upgrade-Insecure-Requests': 1
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'company_info_fill.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'company_info_fill.middlewares.MyCustomDownloaderMiddleware': None,
    'company_info_fill.downloadmiddleware.anti_ban.AntiBanMiddleware': 100,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'company_info_fill.pipelines.CompanyInfoFillPipeline': 300,
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

MOBILE_PREFIX_LIST=['130','131','132','133','134','135','136','137','138','139','150','151','152','153','155','156','157','158','159','170','176','177','178','180','181','182','183','184','185','186','187','188','189']

LOG_FILE = 'logs/spider.log'
LOG_LEVEL = 'INFO'
LOG_BACKUP_COUNT = 10

SPIDER_INFO = {
    'ID': 'TJ_02',
    'SUB_ID': 0,
    'SUB_NUM': 1,
    'TJ_PROXY': False,
    'PUB_PROXY': False,
    'MULTI_IP': {'MONGO': False,
                 'LOCALE_ALL': True,
                 'LOCALE_ONE': False,
                 'NEED_AUTH': False}
}
