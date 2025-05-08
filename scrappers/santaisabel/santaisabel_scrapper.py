from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
import csv
import os

# Configurar navegador en modo headless
options = webdriver.ChromeOptions()
arguments = ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-renderer-backgrounding", "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows", "--disable-client-side-phishing-detection", "--disable-crash-reporter", "--disable-oopr-debug-crash-dump",
            "--no-crash-upload", "--disable-gpu", "--disable-extensions", "--disable-low-res-tiling", "--log-level=3", "--silent"]
for argument in arguments: options.add_argument(argument)
driver = webdriver.Chrome(options=options)

actual = datetime.now().strftime("%d-%m-%Y")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
archivo_salida = os.path.join(BASE_DIR, f"results/{actual}.csv")
search_file_path = os.path.join(BASE_DIR, "search_list.txt")

with open(archivo_salida, "w", encoding="utf-8") as archivo:
    with open(search_file_path, "r", encoding="utf-8") as lista:
        writer = csv.writer(salida)
        writer.writerow(["search","found", "price","pre_discount"])
        for linea in lista:
            producto = linea.strip()
            if producto:
                url = f"https://www.santaisabel.cl/buscar?ft={producto}"
                print(f"Buscando: {producto}")
                driver.get(url)

                num = random.randint(2, 5)

                try:
                    # Esperar a que cargue el primer producto
                    productos_encontrados = WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card-wrap"))
                    )
                    for card in productos_encontrados:
                        marca_elemento = card.find_element(By.CSS_SELECTOR, ".product-card .product-card-brand").text
                        nombre = f"{marca_elemento} {card.find_element(By.CLASS_NAME, "product-card-name").text}"
                        precio_elemento = card.find_element(By.CLASS_NAME, "prices-main-price").text
                        precio_elemento = precio_elemento.replace("$", "")
                        precio_elemento = precio_elemento.replace(".", "")
                        try:
                            old_price = card.find_element(By.CLASS_NAME, "prices-old-price").text
                            old_price=old_price.replace(".", "")
                            old_price=old_price.replace("$","")
                        except:
                            old_price = precio_elemento
                        print(f"✔ {nombre}: {precio_elemento}")
                            
                        writer.writerow([producto,nombre, precio_elemento,old_price])
                            
                except Exception as e:
                    print(f"❌ No se encontraron resultados para: {producto}")

                time.sleep(num)  # Pausa entre búsquedas

driver.quit()
print("\n✅ Búsqueda finalizada. Resultados guardados en:", archivo_salida)
