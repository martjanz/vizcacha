# -*- coding: utf-8 -*-
import scrapy
import re # Regex library
import json

from jumbo.items import JumboArticle

class ArticlesSpider(scrapy.Spider):
    handle_httpstatus_list = [500]
    name = "articles"
    allowed_domains = ["www.jumbo.com.ar"]
    start_urls = (
        'https://www.jumbo.com.ar/Login/PreHome.aspx',
    )

    # Get articles list with their IDs
    #
    # Request structure
    # curl 'https://www.jumbo.com.ar/Login/PreHomeService.aspx/CategoriaSubcategoria'
    #   method: POST
    #   -H 'Content-Type: application/json; charset=utf-8'
    #   -H 'Cookie: ASP.NET_SessionId=td1shuuvsyclls45buyjhri5;
    #       queueit_js_jumbo_cyberdayjumbocomar_userverified=notverified'
    #   -H 'Content-Length: 2'
    #   -d '{}'
    def parse(self, response):
        # Get session id (cookie)
        match = re.search('\w{16,}', response.headers['Set-Cookie'])
        self.sessionID = match.group(0)

        yield scrapy.Request(
            url = ("https://www.jumbo.com.ar/Login/PreHomeService.aspx"
                "/CategoriaSubcategoria"),
            method = 'POST',
            headers = {'Content-Type': 'application/json; charset=utf-8'},
            cookies = {
                'ASP.NET_SessionId': self.sessionID,
                'queueit_js_jumbo_cyberdayjumbocomar_userverified': 'notverified'
            },
            body = '{}',
            callback = self.parseMenu
        )


    def parseMenu(self, response):
        jsonString = json.loads(response.body)
        jsonString = jsonString['d'].encode('utf-8')

        # Corrects json. Wrongly formatted from origin. 
        jsonString = jsonString.replace('{"Menu":{', '{"Menu":[', 1)
        jsonString = jsonString.replace('"Categoria":', '')
        jsonString = re.sub('}}$', ']}', jsonString)

        menu = json.loads(jsonString)

        categories = self.parseCategoriesTree(menu['Menu'])

        return self.traverseCategoriesTree(categories)

    
    def parseCategoriesTree(self, categories, parents = []):
        # Recibe lista de categorías
        #   * Si tiene subcategorías se invoca a sí misma pasando la lista de
        #       subcategorías y las categorías padre
        #   * Si es la última categoría del árbol (elementos subcategorías = 0)
        #       resuelve y devuelve datos de la categoría
        
        result = []

        for category in categories:
            if len(category['Subcategoria']) > 0:
                categoryParents = parents + [category['Nombre']]

                items = self.parseCategoriesTree(category['Subcategoria'],
                    categoryParents)
                result += items
            else:
                item = {}
                item['id'] = category['IdMenu']
                item['name'] = category['Nombre']
                item['parents'] = parents

                result += [item]

        return result


    def traverseCategoriesTree(self, categories):
        for category in categories:
            requestBody = ('{IdMenu:"' + category['id'].encode("utf-8") + 
                '", textoBusqueda:"", producto:"", '
                'marca:"", pager:"", ordenamiento:0, precioDesde:"", '
                'precioHasta:""}')

            request = scrapy.Request(
                url = ("https://www.jumbo.com.ar/Comprar/HomeService.aspx/"
                    "ObtenerArticulosPorDescripcionMarcaFamiliaLevex"),
                method = 'POST',
                headers = {'Content-Type': 'application/json; charset=utf-8',
                    'Content-Length': str(len(requestBody))},
                cookies = {
                    'ASP.NET_SessionId': self.sessionID,
                    'queueit_js_jumbo_cyberdayjumbocomar_userverified': 'verified'
                },
                body = requestBody,
                callback = self.parseArticles
            )

            request.meta['cat_levels'] = category['parents']

            yield request

# 'https://www.jumbo.com.ar/Comprar/HomeService.aspx/ObtenerArticulosPorDescripcionMarcaFamiliaLevex'
# Method: POST
# -H 'Content-Type: application/json; charset=utf-8'
# -H 'Cookie: _ga=GA1.3.849741137.1450573952;
#   _ga=GA1.1.849741137.1450573952;
#   ASP.NET_SessionId=14eegnzmbp0sein1snduo545;
#   queueit_js_jumbo_cyberdayjumbocomar_userverified=verified;
#   _gat=1'
# -H 'Content-Length: 113'
# -d {IdMenu:"5238",textoBusqueda:"", producto:"", marca:"", pager:"",
#   ordenamiento:0, precioDesde:"", precioHasta:""}

# -H 'Host: www.jumbo.com.ar'
# -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:38.0) Gecko/20100101 Firefox/38.0'
# -H 'Accept: application/json, text/javascript, */*; q=0.01'
# -H 'Accept-Language: en-US,en;q=0.5'
# -H 'DNT: 1'
# -H 'Cache-Control: no-cache'
# -H 'X-Requested-With: XMLHttpRequest'
# -H 'Referer: https://www.jumbo.com.ar/Comprar/Home.aspx'
# -H 'Connection: keep-alive'
# -H 'Pragma: no-cache'
# --compressed

    # Parse articles json
    def parseArticles(self, response):
        jsonString = json.loads(response.body)
        jsonString = jsonString['d'].encode('utf-8')
        articleTree = json.loads(jsonString)['ResultadosBusquedaLevex']
        for article in articleTree:
            yield self.parseArticle(article, response.meta['cat_levels'])

    # Parse article, return item
    def parseArticle(self, article, categories):
        item = JumboArticle()

        item['idJumbo'] = article['IdArticulo']
        item['descripcion'] = article['DescripcionArticulo']
        item['precio'] = article['Precio']
        item['precioUnitario'] = article['precioUnidad_0']
        item['unidadMedida'] = article['precioUnidad_1']
        item['marca'] = article['Grupo_Marca']
        item['tipo'] = article['Grupo_Tipo']
        item['oferta'] = article['Articulo_Oferta']
        item['pesable'] = article['Pesable']
        item['categories'] = categories

        return item