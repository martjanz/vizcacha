# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JumboArticle(scrapy.Item):
	internal_id = scrapy.Field()
	name = scrapy.Field()
	price = scrapy.Field()
	unit_price = scrapy.Field()
	measure_unit = scrapy.Field()
	brand = scrapy.Field()
	article_type = scrapy.Field()
	promo = scrapy.Field()
	weighable = scrapy.Field()
	categories = scrapy.Field()