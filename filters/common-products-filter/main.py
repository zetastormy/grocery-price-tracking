import pandas as pd
import re
import numpy as np
from rapidfuzz import fuzz, process
from datetime import datetime

def normalize_text(text):
    """Normaliza los nombres de los productos"""
    text = str(text).lower()
    text = re.sub(r"[°ºª#@&/\\]", "", text)
    text = re.sub(r"(\d+)rll\b", r"\1 unidades", text)
    text = re.sub(r"\b(rollos)\b", "unidades", text)
    text = re.sub(r"\b(dh)\b", "doble hoja", text)
    text = re.sub(r"\b(bolsa)\b", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def normalize_units(unit):
    unit = unit.lower()
    if unit in ['kg', 'kilo', 'kilos', 'kilogramo', 'kilogramos']:
        return 'kg'
    elif unit in ['g', 'gr', 'grs', 'gramo', 'gramos']:
        return 'g'
    elif unit in ['l', 'lt', 'lts', 'litro', 'litros']:
        return 'l'
    elif unit in ['ml', 'mililitro', 'mililitros']:
        return 'ml'
    elif unit in ['unidades', 'unidad', 'unid', 'und', 'u', 'uds']:
        return 'u'  # unidad
    return unit

def extract_capacity(text):
    """
    Extrae cantidad + unidad como (número, unidad normalizada)
    Soporta unidades como 'und', 'u', 'unid.', etc.
    """
    text = str(text).lower()

    # Buscar combinaciones como "150 unidades", "50 und", "3 unid."
    pattern = r"(\d+[,.]?\d*)\s*(kg|g|gr|grs|ml|l|lt|lts|unidades|unidad|unid|und|u|uds)"
    matches = re.findall(pattern, text)

    if matches:
        amount = float(matches[0][0].replace(',', '.'))
        unit = normalize_units(matches[0][1])
        return amount, unit

    return None, None

def convert_to_base_unit(amount, unit):
    """
    Convierte a una unidad base para comparar (g, ml, unidades)
    """
    if unit == "kg":
        return amount * 1000
    elif unit == "g":
        return amount
    elif unit == "l":
        return amount * 1000
    elif unit == "ml":
        return amount
    elif unit == "u":
        return amount  # "u" = unidad
    return None

def is_same_capacity(row1, row2, tolerance=0.05):
    """
    Compara capacidad entre dos productos, permitiendo un % de tolerancia
    Devuelve True si las unidades son compatibles y las cantidades son similares
    """
    cap1, unit1 = row1["capacity_num"], row1["capacity_unit"]
    cap2, unit2 = row2["capacity_num"], row2["capacity_unit"]

    # Ambos deben tener capacidad definida
    if pd.notna(cap1) and pd.notna(cap2):
        val1 = convert_to_base_unit(cap1, unit1)
        val2 = convert_to_base_unit(cap2, unit2)

        # Si no se puede convertir, asumir que no son iguales
        if val1 is None or val2 is None or unit1 != unit2:
            return False

        # Comparar con tolerancia (por defecto: 5%)
        return abs(val1 - val2) / max(val1, val2) <= tolerance

    # Si solo uno tiene capacidad → no comparar
    elif pd.notna(cap1) or pd.notna(cap2):
        return False

    # Si ambos están vacíos, considerar iguales (sin info)
    return True

def parse_price(price):
    """
    Convierte precios en formato '2 x 2990' a precio unitario (1495)
    También maneja casos normales como '2990'
    """
    if isinstance(price, str):
        # Busca patrones como "2 x 2990" o "2x2990" o "2*2990"
        match = re.search(r'(\d+)\s*[xX*]\s*(\d+)', price)
        if match:
            amount = float(match.group(1))
            total_price = float(match.group(2))
            return round(total_price / amount, 2)
        
        # Extraer solo números si hay otros caracteres
        numbers = re.search(r'(\d+[\.,]?\d*)', price.replace('.', '').replace(',', '.'))
        if numbers:
            return float(numbers.group(1))
    
    # Si ya es número o no se encontró patrón especial
    try:
        return float(price)
    except (ValueError, TypeError):
        return None  # Para manejar casos donde el precio no es válido

def get_best_match(row, target_df, threshold=68):
    if "toalla" in row["normalized"]: threshold = 90

    match = process.extractOne(row["normalized"],
                            target_df["normalized"].tolist(),
                            scorer=fuzz.token_set_ratio)

    if len(match) != 3:
        return None, None, None
    
    match_text, match_score, match_idx = match
    #match_idx = target_df.index[target_df["normalized"] == match_text][0]
    match_row = target_df.loc[match_idx]

    if match_score <= threshold or np.abs(match_row["price"] - row["price"]) > 1000 or not is_same_capacity(row, match_row):
        return None, None, None

    return match_row["found"], match_score, match_idx

actual = datetime.now().strftime("%d-%m-%Y")

df_acuenta = pd.read_csv(f"../acuenta/results/{actual}.csv")
df_eltit = pd.read_csv(f"../eltit/results/{actual}.csv")
df_eltrebol = pd.read_csv(f"../eltrebol/results/{actual}.csv")
df_jumbo = pd.read_csv(f"../jumbo/results/{actual}.csv")
df_santaisabel = pd.read_csv(f"../santaisabel/results/{actual}.csv")
df_unimarc = pd.read_csv(f"../unimarc/results/{actual}.csv")

supermercados = {
    "acuenta": df_acuenta,
    "eltit": df_eltit,
    "eltrebol": df_eltrebol,
    "jumbo": df_jumbo,
    "santaisabel": df_santaisabel,
    "unimarc": df_unimarc
}

for df in supermercados.values():
    df["capacity_num"], df["capacity_unit"] = zip(*df["found"].apply(extract_capacity))
    df["normalized"] = df["found"].apply(normalize_text)
    df['price'] = df['price'].apply(parse_price)
    df['pre_discount'] = df['pre_discount'].apply(parse_price)

max_df_name, max_df = max(supermercados.items(), key=lambda x: len(x[1]))
matches = []

for idx, row in max_df.iterrows():
    no_matches = False
    matched_products = {
        "acuenta": (row["found"], row["price"], row["pre_discount"]),
        "eltit": (None, None, None),
        "eltrebol": (None, None, None),
        "jumbo": (None, None, None),
        "santaisabel": (None, None, None),
        "unimarc": (None, None, None)
    }

    for df_name, current_df in supermercados.items():
        if max_df_name == df_name: continue

        matched_product, score, matched_idx = get_best_match(row, current_df)

        if matched_product:
            matched_products[df_name] = (matched_product, current_df.loc[matched_idx, "price"], current_df.loc[matched_idx, "pre_discount"])
        else:
            no_matches = True

    if no_matches: continue

    matches.append({
        "search": row["search"],
        "acuenta": matched_products["acuenta"][0],
        "eltit": matched_products["eltit"][0],
        "eltrebol": matched_products["eltrebol"][0],
        "jumbo": matched_products["jumbo"][0],
        "santaisabel": matched_products["santaisabel"][0],
        "unimarc": matched_products["unimarc"][0],
        "precio_acuenta": matched_products["acuenta"][1],
        "pre_discount_acuenta": matched_products["acuenta"][2],
        "precio_eltit": matched_products["eltit"][1],
        "pre_discount_eltit": matched_products["eltit"][2],
        "precio_eltrebol": matched_products["eltrebol"][1],
        "pre_discount_eltrebol": matched_products["eltrebol"][2],
        "precio_jumbo": matched_products["jumbo"][1],
        "pre_discount_jumbo": matched_products["jumbo"][2],
        "precio_santaisabel": matched_products["santaisabel"][1],
        "pre_discount_santaisabel": matched_products["santaisabel"][2],
        "precio_unimarc": matched_products["unimarc"][1],
        "pre_discount_unimarc": matched_products["unimarc"][2]
    })


df_matches = pd.DataFrame(matches)
df_matches.to_csv(f"results/{actual}.csv", index=False)

print(df_matches)
