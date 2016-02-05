# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Medicamento(scrapy.Item):
    nombre = scrapy.Field()
    laboratorio = scrapy.Field()
    tipo = scrapy.Field()
    drogas = scrapy.Field()
    accion = scrapy.Field()
    presentaciones = scrapy.Field()
    pass

class Presentacion(scrapy.Item):
	descripcion = scrapy.Field()
	precio = scrapy.Field()
	fecha = scrapy.Field()
	coberturas = scrapy.Field()

	pami_cobertura = scrapy.Field()
	pami_monto_prestador = scrapy.Field()
	pami_monto_afiliado = scrapy.Field()

	ioma_cobertura = scrapy.Field()
	ioma_monto_prestador = scrapy.Field()
	ioma_monto_afiliado = scrapy.Field()
	pass