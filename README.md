# Análisis de Precios de Supermercados en Valdivia

Repositorio de códigos utilizados para scrappear datos y realizar análisis de los precios de supermercados en Valdivia, para la asignatura "Computación Científica con Python" - INFO147.

###  Estructura del repositorio

- `graphs`: Contiene archivos de Jupyter Notebook utilizados para elaborar los gráficos del informe.

- `scrappers`: Contiene scripts de Python por supermercado, para extraer los datos de sus productos, junto con los resultados de cada extracción.

- `utils`: Contiene scripts de Python para varias utilidades, tales como filtrado o búsqueda de distancias.

    - `common-products-filter`: Búsqueda de productos en común entre los distintos supermercados evaluados. Los resultados de los productos en común se almacenan dentro de la carpeta `results`.

    - `distance-to-nearest-supermarket`: Calcula la distancia caminando hacia cada supermercado utilizado en el informe desde las universidades de Valdivia.