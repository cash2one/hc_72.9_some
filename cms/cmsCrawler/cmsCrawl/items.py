# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CmscrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
	fromSite = scrapy.Field()
	bc_id = scrapy.Field()
	title = scrapy.Field()
	source = scrapy.Field()
	publish_date = scrapy.Field()
	author = scrapy.Field()
	content = scrapy.Field()
	imgs = scrapy.Field()
