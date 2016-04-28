# -*- coding: utf-8 -*-

import scrapy
import re # Regex library

from coto.items import CotoArticle

class ArticlesSpider(scrapy.Spider):
    name = "coto_articles"
    allowed_domains = ["www.cotodigital3.com.ar"]
    start_urls = [
        "https://www.cotodigital3.com.ar/sitios/cdigi"
    ]

    def parse(self, response):        
        # Recorre subclases (Ej: Alimentos secos -> Galletitas)
        for href in response.xpath('//ul[@class="sub_category"]/li/h2/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_subcategory)


    def parse_subcategory(self, response):
        category = response.xpath(\
            "//div[@class='atg_store_facetsGroup_options_catsub']/h5/text()")
        category = category.extract_first()

        if (category):
            str_match = re.search(u"Categoría", category)
        
        # Si hay elemento categoría recorrer categorías
        if (category) and (str_match is not None):
            
            xpathQuery = ('//div[@class="atg_store_facetsGroup_options_catsub"]'
                        '[1]/div/ul/li/a/@href')
            # Recorre subclases (Ej: Alimentos secos -> Galletitas)
            for href in response.xpath(xpathQuery):
                url = response.urljoin(href.extract())
                yield scrapy.Request(url,
                    callback=self.parse_articles_follow_next_page)
        else:  # Si no hay, recorrer elementos
            yield scrapy.Request(response.url,
                callback=self.parse_articles_follow_next_page,
                dont_filter=True)


    def parse_articles_follow_next_page(self, response):
        categories = []

        # 1st level category
        xpathQuery = ('//div[@class="atg_store_refinementAncestorsLinks"]/'
            'div[@class="atg_store_refinementAncestorsLinkCategory"][2]/'
            'a/text()')
        categories += response.xpath(xpathQuery).extract()

        # 2nd level category
        xpathQuery = ('//div[@class="atg_store_refinementAncestorsLinks"]/'
            'div[@class="atg_store_refinementAncestorsLinkCategory"][3]/'
            'a/text()')
        categories += response.xpath(xpathQuery).extract()  
        
        # 3rd level category
        xpathQuery = ('//div[@class="atg_store_refinementAncestorsLinks"]/'
            'span[@class="atg_store_refinementAncestorsLastLinkSpan"]/text()')
        categories += response.xpath(xpathQuery).extract()
    
        # Articles
        xpathQuery = '//ul[@id=\'products\']//li[starts-with(@class,"clearfix")]'

        for selector in response.xpath(xpathQuery):
            yield self.parse_article(selector, categories)

        # Search for next page button
        xpathQuery = ('//ul[@id="atg_store_pagination"]/'
            'li[contains(@class, "active")]/following-sibling::li[1]/a/@href')
        next_page = response.xpath(xpathQuery)

        # Follow next page, if exists
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_articles_follow_next_page)


    # Parse article
    def parse_article(self, selector, categories):
        item = CotoArticle()

        item['categories'] = categories

        # Nombre
        xpathQuery = ('div/div/a/span[@class="atg_store_productTitle"]/'
            'span[@class="span_productName"]/text()')

        regex = '((?:(\w|\/|\.|\-|\:|\&)+\s{0,2})+)'

        print "DEBUG: selector.xpath(xpathQuery)"
        print selector.xpath(xpathQuery)

        item['name'] = selector.xpath(xpathQuery).re(regex)
        item['name'] = item['name'][0].strip()

        # Precio
        xpathQuery = ('div[@class="rightList"]/'
            'div[@class="atg_store_productAddToCart"]/'
            'div[@class="info_discount"]/'
            'span[@class="atg_store_productPrice"][1]/'
            'span[@class="atg_store_newPrice"]/text()')

        regex = '(\d+\.\d+)'

        item['price'] = selector.xpath(xpathQuery).re(regex)
        item['price'] = item['price'][0].strip()

        # ID Coto (PLU)
        xpathQuery = ('div/div/a/span[@class="atg_store_productTitle"]/'
            'span[@class="span_codigoplu"]/text()')

        regex = '(\d+)'

        item['internal_id'] = selector.xpath(xpathQuery).re(regex)
        item['internal_id'] = item['internal_id'][0].strip()

        # Precio por unidad de medida
        xpathQuery = ('div/div/span[contains(@class, "unit")]/text()')
        unitPrice = selector.xpath(xpathQuery).extract()

        if unitPrice:
            # Concat list elements in string
            unitPrice = ' '.join(unitPrice)
            # Remove tabs, CR, LF
            unitPrice = re.sub('[\t\n\r]*', '', unitPrice)
            # Remove multiple spaces
            unitPrice = re.sub(' {2,}', ' ', unitPrice)
            # Trim spaces
            unitPrice = unitPrice.strip()
            
            item['unit_price'] = unitPrice

        # Promo (oferta || no acumulable con otras promos)
        xpathQuery = 'div/div[@class="promo"]/img/@src'
        urlImgSale = selector.xpath(xpathQuery).extract_first()

        if urlImgSale and len(urlImgSale) > 0:
            if re.search('oferta.png', urlImgSale):
                item['promo'] = "oferta simple"
            elif re.search('no_acumula.png', urlImgSale):
                item['promo'] = "no acumulable"
        
        return item