# -*- coding: utf-8 -*-
import scrapy
import sys

from kairos.items import Medicamento
from kairos.items import Presentacion

class MedicamentosSpider(scrapy.Spider):
    handle_httpstatus_list = [500]

    name = "medicamentos"
    allowed_domains = ["ar.kairosweb.com"]
    start_urls = (
        'http://ar.kairosweb.com/laboratorios.html?g=1',
        'http://ar.kairosweb.com/laboratorios.html?g=2',
        'http://ar.kairosweb.com/laboratorios.html?g=3',
        'http://ar.kairosweb.com/laboratorios.html?g=4'
    )

    def parse(self, response):
    	# Recorrer laboratorios
    	xpath_query = '//table[@class="tabla_productos"]/tr[@class="productos"]/td/a'
    	labs = response.xpath(xpath_query)

    	for lab in labs:
    		url = response.urljoin(lab.xpath('@href').extract_first())
    		request = scrapy.Request(url, callback=self.parse_laboratorio)
    		request.meta['laboratorio'] = lab.xpath('text()').extract_first()
    		yield request

    	# Pasar a siguiente página
        pass

    def parse_laboratorio(self, response):
    	print "Scraping lab " + response.meta['laboratorio'] + "..."
        # TODO: Scrapear datos de laboratorio
        # response.xpath("//td[@class='lab_info']//text()").extract()
            # TODO: Ver cuál es la función de scrapy para joinear lista
        
        # Recorrer medicamentos
        xpath_query = '//div[@class="productos"]/table/tr/td/ul/li/a'
        meds = response.xpath(xpath_query)

        for med in meds:
            url = response.urljoin(med.xpath('@href').extract_first())
            request = scrapy.Request(url, callback=self.parse_medicamento)
            request.meta['laboratorio'] = response.meta['laboratorio']
            yield request

        pass

    def parse_medicamento(self, response):
        med = Medicamento()

        med['laboratorio'] = response.meta['laboratorio']
        med['nombre'] = response.xpath("//div[@class='nombre_produc']/text()").extract_first()
        med['tipo'] = response.xpath("//td[@class='descrip_derecha_tabla']/text()").extract_first()
        med['drogas'] = response.xpath("//td[@class='descrip_derecha_tabla']/a/text()").extract()
        med['accion'] = response.xpath("//table/tr[last()-1]/td[@class='descrip_derecha_tabla']/text()").extract_first()

        # Parsear presentaciones
        med['presentaciones'] = self.parse_presentaciones(response.xpath('//div[@class="caja_descripcion"]'))

        return med


    # parse_presentaciones: Parsea presentaciones
    # Recibe selector con div de presentaciones
    # returns dict(Presentacion)
    def parse_presentaciones(self, sel):
        presentaciones = []
        
        i = 0
        while True:
            xpath_query = './*[count(preceding-sibling::br)=' + str(i*2) + ']'
            
            # Selector de presentación
            sel_pres = sel.xpath(xpath_query)

            # Si no hay más presentaciones termina
            if (len(sel_pres) == 0):
                break

            pres = Presentacion()
            pres['precio'] = sel_pres[0].xpath("./b/text()").extract_first()
            pres['descripcion'] = sel_pres[1].xpath("text()").extract_first()
            pres['fecha'] = sel_pres[2].xpath("./i/text()").extract_first()

            try:
                pres['pami_monto_prestador'] = sel_pres.xpath('.//ancestor::div[@class="info_pami"]/div/b/text()').extract()[0]
                pres['pami_monto_afiliado'] = sel_pres.xpath('.//ancestor::div[@class="info_pami"]/div/b/text()').extract()[1]
                pres['pami_cobertura'] = sel_pres.xpath('.//ancestor::div[@class="info_pami"]/text()').extract()[1]
            except IndexError:
                pass

            try:
                pres['ioma_monto_prestador'] = sel_pres.xpath('.//ancestor::div[@class="info_ioma"]/div/b/text()').extract()[0]    
                pres['ioma_monto_afiliado'] = sel_pres.xpath('.//ancestor::div[@class="info_ioma"]/div/b/text()').extract()[1]
                pres['ioma_cobertura'] = sel_pres.xpath('.//ancestor::div[@class="info_ioma"]/text()').extract()[1]
            except IndexError:
                pass

            presentaciones.append(pres)

            i = i+1

        return presentaciones