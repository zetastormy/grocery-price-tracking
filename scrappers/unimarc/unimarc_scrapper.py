from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from datetime import datetime

# Configurar el navegador
options = webdriver.ChromeOptions()
arguments = ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-renderer-backgrounding", "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows", "--disable-client-side-phishing-detection", "--disable-crash-reporter", "--disable-oopr-debug-crash-dump",
            "--no-crash-upload", "--disable-gpu", "--disable-extensions", "--disable-low-res-tiling", "--log-level=3", "--silent"]
for argument in arguments: options.add_argument(argument)
driver = webdriver.Chrome(options=options)

# Archivo donde se guardarán los resultados

actual = datetime.now().strftime("%d-%m-%Y")
archivo_salida = f"results/{actual}.csv"

with open(archivo_salida, "w", encoding="utf-8") as archivo:
    with open("search_list.txt", "r", encoding="utf-8") as lista:
        writer = csv.writer(archivo)
        writer.writerow(["search","found", "price", "pre_discount"])
        for linea in lista:
            producto = linea.strip()
            if producto:
                producto2 = producto.replace(" ", "-")
                url = f"https://www.unimarc.cl/search?q={producto2}"
                print(f"\n Buscando: {producto}")
                driver.get(url)

                try:
                    # Esperar hasta que aparezcan contenedores de productos
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                            ".baseContainer_container__TSgMX.ab__shelves.abc__shelves.baseContainer_align-start__6PKCY.baseContainer_absolute-default--topLeft__lN1In"))
                    )

                    contenedores = driver.find_elements(By.CSS_SELECTOR,
                        ".baseContainer_container__TSgMX.ab__shelves.abc__shelves.baseContainer_align-start__6PKCY.baseContainer_absolute-default--topLeft__lN1In")

                    if not contenedores:
                        raise Exception("No se encontraron contenedores")

                    for contenedor in contenedores:
                        try:
                            nombre_elemento = contenedor.find_element(By.CSS_SELECTOR,
                                ".Text_text__cB7NM.Shelf_nameProduct__CXI5M.Text_text--left__1v2Xw.Text_text--black__zYYxI.Text_text__cursor--pointer__WZsQE.Text_text--none__zez2n")
                            nombre_producto = nombre_elemento.text
                        except:
                            nombre_producto = "Nombre no disponible"

                        # Intentar precio en oferta
                        try:
                            precio_elemento = contenedor.find_element(By.XPATH, ".//*[starts-with(@id, 'listPrice__offerPrice--discountprice-')]").text
                            precio_normal = contenedor.find_element(By.XPATH, ".//*[starts-with(@id, 'listPrice__offerPrice--listprice-')]").text
                        except:
                            precio_elemento = contenedor.find_element(By.XPATH, ".//*[starts-with(@id, 'listPrice__offerPrice--listprice-')]").text
                            precio_normal = contenedor.find_element(By.XPATH, ".//*[starts-with(@id, 'listPrice__offerPrice--listprice-')]").text
                        precio_normal = precio_normal.replace(".", "")
                        precio_normal = precio_normal.replace("$", "")
                        print(f" {nombre_producto} | 💲 {precio_elemento}")
                        precio_elemento = precio_elemento.replace(".", "")
                        precio_elemento = precio_elemento.replace("$", "")
                        writer.writerow([producto,nombre_producto, precio_elemento,precio_normal])

                except Exception as e:
                    print(f" No se encontró información para {producto}")
                time.sleep(2)

driver.quit()
print(f"\n :D Datos guardados en '{archivo_salida}'")
