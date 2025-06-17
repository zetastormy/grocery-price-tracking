import googlemaps
import os
import csv
from datetime import datetime
from itertools import product, combinations

# Configuración de la API
api_key = os.environ.get('MAPS_API_KEY')
gmaps = googlemaps.Client(key=api_key)

# Datos originales
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

# Función optimizada para calcular distancias
def get_distances(origins, destinations):
    result = gmaps.distance_matrix(origins, destinations, mode="walking", departure_time=datetime.now())
    distances = []
    for row in result['rows']:
        row_distances = []
        for element in row['elements']:
            if element['status'] == 'OK':
                row_distances.append(element['distance']['value'])  # En metros
            else:
                row_distances.append(None)
        distances.append(row_distances)
    return distances

# Generar nombres completos de supermercados
supermarket_locations = {}
for sup_name, locations in supermarkets.items():
    supermarket_locations.update({f"{sup_name}_{i+1}": loc for i, loc in enumerate(locations)})

# Crear el archivo CSV
with open('all_distances_complete.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["type", "origin", "destination", "distance"])
    
    # 1. Universidades a Supermercados
    print("Calculando distancias universidades-supermercados...")
    for uni_name, uni_coords in universities.items():
        distances = get_distances([uni_coords], list(supermarket_locations.values()))
        for (sup_name, sup_coords), dist in zip(supermarket_locations.items(), distances[0]):
            writer.writerow(["university-supermarket", uni_name, sup_name, dist])
    
    # 2. Universidades entre sí
    print("Calculando distancias entre universidades...")
    uni_pairs = combinations(universities.items(), 2)
    for (uni1, coords1), (uni2, coords2) in uni_pairs:
        dist = get_distances([coords1], [coords2])[0][0]
        writer.writerow(["university-university", uni1, uni2, dist])
    
    # 3. TODOS los supermercados entre sí (incluyendo diferentes cadenas)
    print("Calculando distancias entre todos los supermercados...")
    sup_pairs = combinations(supermarket_locations.items(), 2)
    for (sup1, coords1), (sup2, coords2) in sup_pairs:
        dist = get_distances([coords1], [coords2])[0][0]
        writer.writerow(["supermarket-supermarket", sup1, sup2, dist])

print("¡Todas las distancias calculadas y guardadas en 'all_distances_complete.csv'!")