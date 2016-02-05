# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JumboArticle(scrapy.Item):
	idJumbo = scrapy.Field()
	descripcion = scrapy.Field()
	precio = scrapy.Field()
	precioUnitario = scrapy.Field()
	unidadMedida = scrapy.Field()
	marca = scrapy.Field()
	tipo = scrapy.Field()
	oferta = scrapy.Field()
	pesable = scrapy.Field()
	categories = scrapy.Field()