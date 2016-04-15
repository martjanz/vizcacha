# -*- coding: utf-8 -*-
import sys

from urllib2 import urlopen
from bs4 import BeautifulSoup
import csv
from datetime import date

def getArticles(url):
	html = urlopen(url)

	bs_obj = BeautifulSoup(html.read(), 'html.parser')

	products = bs_obj.findAll(
		'li',
		{
			'class': 'peyaCard',
			'class': 'product',
			'class': 'most'
		}
	)

	result = []

	for product in products:
		article = {}
		article['name'] = product.h4.get_text().strip().encode('utf-8')

		# Para casos con descuentos, donde es distinta la estructura
		if product.div.findAll('span', {'class': 'discounted-price'}):
			price = product.div.find(
				'span',
				{'class': 'discounted-price'}
			)
 		else:
			price = product.div

		price = price.get_text().strip().encode('utf-8').replace('$', '')
		article['price'] = price
		
		result.append(article)

	return result


def main(argv):
	sources = [
		{
			'POS': 'Grido',
			'url': 'http://www.pedidosya.com.ar/restaurantes/buenos-aires'\
				'/grido-helados-liniers-menu'
		},
		{
			'POS': 'Freddo',
			'url': 'http://www.pedidosya.com.ar/restaurantes/buenos-aires/'\
				'freddo-puerto-madero-menu'
		},
		{
			'POS': 'La Continental',
			'url': 'http://www.pedidosya.com.ar/restaurantes/buenos-aires/'\
				'la-continental-menu'
		},
		{
			'POS': 'Tercera Docena',
			'url': 'http://www.pedidosya.com.ar/restaurantes/buenos-aires/'\
				'tercera-docena-barracas-menu'
		},
		{
			'POS': 'Cremolatti',
			'url': 'http://www.pedidosya.com.ar/restaurantes/buenos-aires/'\
				'cremolatti-saavedra-menu'
		},
		{
			'POS': 'Prosciutto Ristorante',
			'url': 'http://www.pedidosya.com.ar/restaurantes/buenos-aires/'\
				'prosciutto-ristorante-monserrat-menu'
		},
		{
			'POS': 'La Fábrica',
			'url': 'http://www.pedidosya.com.ar/restaurantes/buenos-aires/'\
				'la-fabrica-barracas-menu'
		},
		{
			'POS': 'Agatta',
			'url': 'http://www.pedidosya.com.ar/restaurantes/buenos-aires/'\
				'agatta-menu'
		},
		{
			'POS': 'Los 36 Billares',
			'url': 'http://www.pedidosya.com.ar/restaurantes/buenos-aires/'\
				'los-36-billares-menu'
		},
		{
			'POS': 'Burger King',
			'url': 'http://www.pedidosya.com.ar/restaurantes/buenos-aires/'\
				'burger-king-canning-menu'
		},
		{
			'POS': "Amelia's",
			'url': 'http://www.pedidosya.com.ar/restaurantes/buenos-aires/'\
				'amelias-balvanera-menu'
		},
	]

	csvFilename = 'data/' + date.today().strftime('%Y%m%d') + '.csv'
	csvFile = open(csvFilename, 'w+')
	writer = csv.writer(csvFile)

	# csv headers
	writer.writerow(('POS', 'article_name', 'article_price'))
	
	for source in sources:
		print 'Getting prices from ' + source['POS'] + '...'
		articles = getArticles(source['url'])
		
		for article in articles:	
			writer.writerow((source['POS'], article['name'], article['price']))

	csvFile.close()


if __name__ == "__main__":
    main(sys.argv)