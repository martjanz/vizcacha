# Scrapy Crawlers

Recolectores de precios de supermercados y otros catálogos usando
[Scrapy](https://scrapy.org/) Framework.


## Primero
Salvo el de Walmart, el resto de los scrapers estaban funcionando al menos hasta
mediados de 2016. Dado que los scrapers dependen directamente de la estructura
del sitio web posiblemente ahora (casi un año después) no funcionen correctamente.

Cuando vayas a ejecutar cada crawler chequeá antes su correspondiente `settings.py`,
donde se determinan los límites de conexiones simultáneas, cantidad de requests
por segundo, etc. Un request por segundo es una buena medida. Más que eso es vicio.

## Crawlers

Todos supermercados online, salvo donde se aclara.

* [Coto Digital](www.cotodigital.com.ar)
* [Disco.com.ar](http://disco.com.ar/)
* [Jumbo Supermercado Online](https://www.jumbo.com.ar/)
* [Kairos Web](http://ar.kairosweb.com/) (vademecum de medicamentos)
* [Tu Alacena](http://tualacena.com/) (agregador de precios de supermercados)
* [Vea Digital](http://veadigital.com.ar/)
* [Walmart Online](http://walmartonline.com.ar/)

## Requerimientos previos

* Git
* Python
* pip (Python Package Manager)
* Virtualenv (Python Virtual Environment Builder)

  ```sh
  # Para instalarlo
  pip install virtualenv
  ```

## Instalación

* Cloná este repositorio

  ```sh
  git clone http://github.com/martjanz/scrawls
  ```

* Entrá al directorio

  ```sh
  cd scrawls
  ```

* Creá y activá el entorno virtual Python

  ```sh
  virtualenv venv
  source venv/bin/activate
  ```

* Instalá dependencias

  ```
  pip install -r requirements.txt
  ```

## Uso

Para bajar precios de, por ejemplo, Coto Digital a un archivo separado por comas (_.csv_).

```sh
# Si no tenés activado el entorno virtual...
source venv/bin/activate

# ...y luego
cd coto
scrapy crawl coto_articles -o ../coto.csv
```


## Colaboraciones, a voluntad
Cualquier mejora o correción va a ser muy bienvenida. Para eso:
  * Hacé un fork de este repo.
  * Hacé commits (en tu repo) con los cambios.
  * Mandame un Pull Request con los cambios, explicando qué cambiaste o agregaste.
