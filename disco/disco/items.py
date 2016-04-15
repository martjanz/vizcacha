# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class DiscoArticle(scrapy.Item):
    internal_id = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    unit_price = scrapy.Field()
    categories = scrapy.Field()
    oferta = scrapy.Field()
    pass
