# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CotoArticle(scrapy.Item):
    id_coto = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    unit_price = scrapy.Field()
    categories = scrapy.Field()
    promo = scrapy.Field()