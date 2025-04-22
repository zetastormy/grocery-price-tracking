from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from datetime import datetime

# Configurar navegador
options = webdriver.ChromeOptions()
arguments = ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-renderer-backgrounding", "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows", "--disable-client-side-phishing-detection", "--disable-crash-reporter", "--disable-oopr-debug-crash-dump",
            "--no-crash-upload", "--disable-gpu", "--disable-extensions", "--disable-low-res-tiling", "--log-level=3", "--silent"]
for argument in arguments: options.add_argument(argument)
driver = webdriver.Chrome(options=options)

actual = datetime.now().strftime("%d-%m-%Y")
archivo_salida = f"results/{actual}.csv"

with open(archivo_salida, "w", encoding="utf-8") as archivo:
    with open("search_list.txt", "r", encoding="utf-8") as lista:
        writer = csv.writer(archivo)
        writer.writerow(["search","found", "price","pre_discount"])

        for linea in lista:
            producto = linea.strip()
            if not producto:
                continue

            print(f"\n🔎 Buscando: {producto}")
            url = f"https://www.acuenta.cl/search?name={producto}"
            driver.get(url)

            try:
                # Esperar que carguen los productos
                contenedores = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "card-product-vertical.product-card-default"))
                )
                print(f"🧩 Se encontraron {len(contenedores)} productos")
                
                if not contenedores:
                    raise Exception("No se encontraron contenedores")


                for contenedor in contenedores:
                    try:
                        nombre = contenedor.find_element(By.CLASS_NAME, "prod__name").text
                    except Exception as e:
                        print("❌ No se encontró el nombre del producto")
                        nombre = "Nombre no disponible"

                    try:
                        precio = contenedor.find_element(By.CLASS_NAME, "prod__n-per-price__text").text
                    except:
                        precio = contenedor.find_element(By.CLASS_NAME, "base__price").text
                        
                    precio = precio.replace(".", "")
                    precio = precio.replace("$", "")

                    print(f"✔️ {nombre} | 💲 {precio}")
                    writer.writerow([producto,nombre, precio,precio])

            except Exception as e:
                print(f"🚫 No se encontró información para '{producto}': {e}")
                
            try:
                # Esperar que carguen los productos
                contenedores = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "card-product-vertical.product-card-crossedOut"))
                )
                print(f"🧩 Se encontraron {len(contenedores)} productos con descuento")
                for contenedor in contenedores:
                    try:
                        nombre = contenedor.find_element(By.CLASS_NAME, "prod__name").text
                    except Exception as e:
                        print("❌ No se encontró el nombre del producto")
                        nombre = "Nombre no disponible"

                    try:
                        precio = contenedor.find_element(By.CLASS_NAME, "prod__n-per-price__text").text
                    except:
                        precio = contenedor.find_element(By.CLASS_NAME, "base__price").text
                        
                    precio = precio.replace(".", "")
                    precio = precio.replace("$", "")
                    
                    try:
                        old_price = contenedor.find_element(By.CLASS_NAME, "prod-crossed-out__price__old").text
                        old_price = old_price.replace(".", "")
                        old_price = old_price.replace("$", "")
                        old_price = old_price.replace("(", "")
                        old_price = old_price.replace(")", "")
                        print("✅ old_price encontrado:", old_price)
                    except:
                        old_price = precio

                    print(f"✔️ {nombre} | 💲 {precio}")
                    writer.writerow([producto,nombre, precio,old_price])
            except:
                print(f"No hay descuentos para '{producto}'")

            time.sleep(2)  # Esperar un poco antes de buscar el siguiente

driver.quit()
print(f"\n✅ Datos guardados en '{archivo_salida}'")
