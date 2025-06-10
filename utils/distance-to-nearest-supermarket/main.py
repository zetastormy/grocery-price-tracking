import googlemaps
import os
import csv
from datetime import datetime

# Configuración de la API
api_key = os.environ.get('MAPS_API_KEY')
gmaps = googlemaps.Client(key=api_key)

# Datos de universidades y supermercados
universities = {
    "uach-mf": (-39.8329479334262, -73.2511942443009),
    "uach-teja": (-39.806088494536944, -73.25164778408663),
    "uss": (-39.82145384984739, -73.24995683146737),
    "ust": (-39.81735094591222, -73.23314353146745),
    "inacap": (-39.80496976406447, -73.21489143331709)
}

supermarkets = {
    "acuenta": [(-39.850114249731554, -73.231054806329), (-39.834488731560974, -73.21465377017593), (-39.81553498961656, -73.23601018728954)],
    "eltit": [(-39.8174652106114, -73.24474567440642)],
    "eltrebol": [(-39.84183808299696, -73.24558252332072), (-39.84801567242141, -73.21904170746593)],
    "jumbo": [(-39.81838008358224, -73.23457995437096)],
    "santaisabel": [(-39.81364704556594, -73.24217601219996), (-39.83863836270679, -73.20985523969343)],
    "unimarc": [(-39.837462772595124, -73.23101179492134), (-39.816440905598505, -73.2415152399612), (-39.81309398073948, -73.2473120850604), (-39.812999338251586, -73.22205854418874)]
}

# Función para calcular distancias
def get_distances(university_coords, supermarket_coords):
    result = gmaps.distance_matrix(university_coords, supermarket_coords, mode="walking", departure_time=datetime.now())
    distances = []
    for element in result['rows'][0]['elements']:
        if element['status'] == 'OK':
            distances.append(element['distance']['value'])  # En metros
        else:
            distances.append(None)
    return distances

# Crear el archivo CSV y escribir los encabezados
with open('distances.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["university", "supermarket", "distance"])

    # Calcular las distancias y escribirlas en el archivo CSV
    for university, uni_coords in universities.items():
        for supermarket, super_coords in supermarkets.items():
            distances = get_distances([uni_coords] * len(super_coords), super_coords)
            for i, dist in enumerate(distances):
                writer.writerow([university, f"{supermarket}_{i+1}", dist])
                
print("Las distancias se han guardado en 'distances.csv'.")
