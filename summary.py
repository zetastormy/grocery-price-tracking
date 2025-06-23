import pandas as pd
from pathlib import Path
from datetime import datetime

supermarkets = {
    "acuenta": ([], [], [], "aCuenta"), 
    "eltit": ([], [], [], "Eltit"), 
    "eltrebol": ([], [], [], "El Trébol"), 
    "jumbo": ([], [], [], "Jumbo"), 
    "santaisabel": ([], [], [], "Santa Isabel"), 
    "unimarc": ([], [], [], "Unimarc")
}

total_product_amount = 0

for name, sp_data in supermarkets.items():
    dates = []
    averages = []
    amounts = []

    for child in Path(f'./scrappers/{name}/results/').iterdir():
        if child.is_file():
            data = pd.read_csv(child)

            data['price'] = pd.to_numeric(data['price'], errors='coerce')
            dates.append(datetime.strptime(child.name.replace(".csv", ""), "%d-%m-%Y").date())
            averages.append(int(data['price'].mean()))
            amounts.append(len(data['found']))

    dates, averages, amounts = zip(*sorted(zip(dates, averages, amounts)))
    total_product_amount += sum(amounts)

    print("---------------------------------")
    print(f"{sp_data[3]}:")
    print("---------------------------------")
    for i in range(len(dates)):
        print(f"- {dates[i]}:")
        print(f"    - Productos encontrados: {amounts[i]}")
        print(f"    - Promedio: {averages[i]}")

    sp_data[0].append(dates)
    sp_data[1].append(averages)
    sp_data[2].append(amounts)

print(f"\nVolumen de datos: {total_product_amount}\n")

print("---------------------------------")
print(f"Datos filtrados:")
print("---------------------------------")

total_product_amount_filtered = 0

for child in Path(f'./utils/common-products-filter/results/').iterdir():
    data = pd.read_csv(child)
    date = datetime.strptime(child.name.replace(".csv", ""), "%d-%m-%Y").date()
    data_amount = len(data["search"])

    print(f"- {date}:")
    print(f"    - Productos en común: {data_amount}")

    total_product_amount_filtered += data_amount

print(f"\nVolumen de datos filtrado: {total_product_amount_filtered}")
