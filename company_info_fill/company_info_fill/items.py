# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CompanyInfoFillItem(scrapy.Item):
    mp = scrapy.Field()
    telephone = scrapy.Field()
    company_name = scrapy.Field()
    web_url = scrapy.Field()
    mobile_contact = scrapy.Field()
    telephone_contact = scrapy.Field()
