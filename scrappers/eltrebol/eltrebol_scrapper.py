from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
result_path = os.path.join(BASE_DIR, f"results/{actual}.csv")
search_file_path = os.path.join(BASE_DIR, "search_list.txt")
search_file = open(search_file_path, "r", encoding="utf-8")
arguments = ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-renderer-backgrounding", "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows", "--disable-client-side-phishing-detection", "--disable-crash-reporter", "--disable-oopr-debug-crash-dump",
            "--no-crash-upload", "--disable-gpu", "--disable-extensions", "--disable-low-res-tiling", "--log-level=3", "--silent"]
current_date = datetime.now().strftime("%d-%m-%Y")

with open(result_path, "w", newline = "", encoding = "utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["search", "found", "price", "pre_discount"])

    options = Options()
    for argument in arguments: options.add_argument(argument)
    driver = webdriver.Chrome(options = options)

    for search in search_file:
        search = search.strip()
        driver.get("https://www.supertrebol.cl/search?q=" + search)

        ul_productos = driver.find_element(By.CSS_SELECTOR, 'ul.products')
        productos_li = ul_productos.find_elements(By.TAG_NAME, 'li')

        for producto in productos_li:
            nombre = producto.find_element(By.CSS_SELECTOR, ".marca a").text + " " + producto.find_element(By.CSS_SELECTOR, "h3.product-model a").text
            precio_antes = producto.find_element(By.CLASS_NAME, "bootic-price-comparison").text.replace('$', '').replace('.', '')
            precio_actual = producto.find_element(By.CLASS_NAME, "bootic-price").text.replace('$', '').replace('.', '')

            if (precio_antes == ""): precio_antes = precio_actual

            print(f"Búsqueda: {search}")
            print(f"Encontrado: {nombre}")
            print(f"Precio anterior: {precio_antes}")
            print(f"Precio actual: {precio_actual}\n")

            writer.writerow([search, nombre, precio_actual, precio_antes])

        time.sleep(3)

    driver.quit()

search_file.close()

