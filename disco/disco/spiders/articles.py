# -*- coding: utf-8 -*-
import scrapy
import re 		# Regex (stdlib)
import js2py    # JavaScript interpreter
import pickle   # Serialization (stdlib) 

from disco.items import DiscoArticle

class ArticlesSpider(scrapy.Spider):
    name = "articles"
    allowed_domains = ["www3.discovirtual.com.ar"]
    start_urls = (
        'https://www3.discovirtual.com.ar/_UserControls/JpegImage.aspx',
    )


    # Get articles list with their IDs
    #
    # Request structure
    # curl 'https://www3.discovirtual.com.ar/Comprar/Menu.aspx?IdLocal=9119&IdTipoCompra=8&Fecha=20160118'
    #   method: POST
    #   -H 'Content-Type: application/json; charset=utf-8'
    #   -H 'Cookie: ASP.NET_SessionId=td1shuuvsyclls45buyjhri5;
    def parse(self, response):
    	# Get session id (cookie)
        match = re.search('\w{16,}', response.headers['Set-Cookie'])
        self.sessionID = match.group(0)

        yield scrapy.Request(
            url = "https://www3.discovirtual.com.ar/Login/Invitado.aspx",
            method = 'GET',
            headers = {
                'Referer': 'https://www3.discovirtual.com.ar/Login/PreHome.aspx',
                'Host': 'www3.discovirtual.com.ar'
            },
            cookies = {
                'ASP.NET_SessionId': self.sessionID,
            },
            callback = self.getCategoryTree
        )


    def getCategoryTree(self, response):

        yield scrapy.Request(
            url = ("https://www3.discovirtual.com.ar/Comprar/Menu.aspx"
                "?IdLocal=9235&IdTipoCompra=4"),
            method = 'GET',
            headers = {
                'Referer': 'https://www3.discovirtual.com.ar/Comprar/Home.aspx',
                'Host': 'www3.discovirtual.com.ar'
            },
            cookies = {
                'ASP.NET_SessionId': self.sessionID,
            },
            callback = self.parseMenu
        )

    	pass


    def parseMenu(self, response):
        script = response.body

        # Replace unusable javascript code
        script = script.replace("document.write(CrearMenu());", "g")

        treeMenu = js2py.eval_js(script)

        treeMenu = list(treeMenu) # cast JSObjectWrapper to list

        categories = self.extractLeafCategories(treeMenu)

        return self.traverseCategories(categories)
    

    # Extracts last categories (greatest disaggregation) from menu
    def extractLeafCategories(self, treeItem, parents = []):
        result = []

        if isinstance(treeItem[0], list):
            for item in treeItem:
                result += self.extractLeafCategories(item, parents)

        elif isinstance(treeItem, list):
            if (treeItem[2] is not None):
                categoryParents = parents + [treeItem[1]]
                items = self.extractLeafCategories(treeItem[2], categoryParents)
                result += items
            else:
                result += [{
                    'id': treeItem[0],
                    'name': treeItem[1],
                    'parents': parents
                }]

        return result

    def traverseCategories(self, categoryTree):
        for category in categoryTree:
            requestBody = '{"idMenu":' + \
                str(category['id']).encode('utf-8') + '}'

            request = scrapy.Request(
                url = ("https://www3.discovirtual.com.ar/ajaxpro/"
                    "_MasterPages_Home"
                    ",DiviComprasWeb.ashx?method=MostrarGondola"),
                method = 'POST',
                headers = {
                    'Referer': 'https://www3.discovirtual.com.ar/Comprar/Home.aspx',
                    'Host': 'www3.discovirtual.com.ar',
                    'X-AjaxPro-Method': 'MostrarGondola',
                    'Content-Type': ('application/x-www-form-urlencoded; '
                        'charset=UTF-8'),
                    'Content-Length': len(requestBody)
                },
                cookies = {
                    'ASP.NET_SessionId': self.sessionID,
                },
                body = requestBody,
                callback = self.parseArticles
            )

            request.meta['parents'] = category['parents'] + [category['name']]
            request.meta['idMenu'] = category['id']

            yield request

    def parseArticles(self, response):
        articlesXPathQuery = '//tr[@class="filaListaDetalle"]'

        try:
            pageNumber = response.meta['pageNumber']
        except:
            pageNumber = 1

        sel = scrapy.Selector(text=response.body.replace("\\\"", "\""))
        
        for articleSelector in sel.xpath(articlesXPathQuery):
            article = DiscoArticle()

            # Clean article name
            articleName = articleSelector.xpath('td/a/text()')\
                .extract_first().encode('utf-8').strip() # Nombre
            # Trim multiple spaces
            articleName = re.sub(' {2,}', ' ', articleName)

            articleId = articleSelector.xpath('td/a/@id')\
                .extract_first().encode('utf-8').strip() # Nombre
            articleId = re.sub('dla_', '', articleId)

            unitPrice = articleSelector\
                .xpath('td/font[@class="txt-6"]/text()')\
                .extract_first().encode('utf-8') # Precio por unidad
            unitPrice = re.sub(' {2,}', ' ', unitPrice)

            oferta = articleSelector\
                .xpath('td/img/@title[contains(.,"oferta")]')\
                .extract_first()

            article['id_disco'] = articleId
            article['name'] = articleName
            article['unit_price'] = unitPrice 
            article['price'] = articleSelector.xpath('td/text()').extract_first()\
                .encode('utf-8') # Precio
            article['parents'] = response.meta['parents'] # Categorías padre

            if (oferta is not None) and (len(oferta) > 0):
                article['oferta'] = True

            yield article

        # Checks if there is next page and send the request
        nextPageXPathQuery = ("//td[@class='celdaListaBotonesYPaginado']"
                "//a[@class='txt-3']/text()[contains(.,'>>')]")

        if (len(sel.xpath(nextPageXPathQuery)) > 0):
            yield self.followNextPage(response.meta['idMenu'],\
                response.meta['parents'], pageNumber + 1)

        pass


    def followNextPage(self, idMenu, parents, nextPageNumber):
        requestBody = ('{"pecActualizarFuncion":0,"pecControlUniqueID":"",'
                '"pecTablaOrden":1,"pecTablaElementoOrden":0,"pecOpcion":1,'
                '"textoBusqueda":"","idPromo":0,"idPECListaCompraParametro":0,'
                '"idPedido":0,"sortDirection":0,"visualizarFotosArticulos":true,'
                '"sortExpresion":0,"paginacion":20,"idMiLista":0,'
                '"paginaActual":' + str(nextPageNumber) + ','
                '"idMenu":' + str(idMenu) + '}:""')

        request = scrapy.Request(
            url = ("https://www3.discovirtual.com.ar/ajaxpro/"
                "_MasterPages_Home"
                ",DiviComprasWeb.ashx?method=PecActualizar"),
            method = 'POST',
            headers = {
                'Referer': 'https://www3.discovirtual.com.ar/Comprar/Home.aspx',
                'Host': 'www3.discovirtual.com.ar',
                'X-AjaxPro-Method': 'PecActualizar',
                'Content-Type': ('application/x-www-form-urlencoded; '
                    'charset=UTF-8'),
                'Content-Length': len(requestBody)
            },
            cookies = {
                'ASP.NET_SessionId': self.sessionID,
            },
            body = requestBody,
            callback = self.parseArticles
        )

        request.meta['parents'] = parents
        request.meta['idMenu'] = idMenu
        request.meta['pageNumber'] = nextPageNumber

        return request