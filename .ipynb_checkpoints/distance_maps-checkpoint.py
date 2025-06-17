import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path
from io import BytesIO
from collections import defaultdict

# ---- Información de supermercados
supermarkets = {
    "Acuenta – Pedro Montt":       {"coords": (-39.850114249731554, -73.231054806329), "direccion": "Pedro Montt 4300"},
    "Acuenta – Picarte":           {"coords": (-39.834488731560974, -73.21465377017593), "direccion": "Av. Ramón Picarte 2661"},
    "Acuenta – Anwandter":         {"coords": (-39.81553498961656, -73.23601018728954), "direccion": "Carlos Anwandter 930"},
    "Eltit":                       {"coords": (-39.8174652106114, -73.24474567440642), "direccion": "Camilo Henríquez 780"},
    "El Trébol – Simpson":         {"coords": (-39.84183808299696, -73.24558252332072), "direccion": "Av. Simpson 499"},
    "El Trébol – Schneider":       {"coords": (-39.84801567242141, -73.21904170746593), "direccion": "René Schneider 3722"},
    "Jumbo":                       {"coords": (-39.81838008358224, -73.23457995437096), "direccion": "Errázuriz 1040"},
    "Santa Isabel – Chacabuco":    {"coords": (-39.81364704556594, -73.24217601219996), "direccion": "Chacabuco 545"},
    "Santa Isabel – Picarte":      {"coords": (-39.83863836270679, -73.20985523969343), "direccion": "Av. Ramón Picarte 3057"},
    "Unimarc – Francia":           {"coords": (-39.837462772595124, -73.23101179492134), "direccion": "Av. Francia 2651"},
    "Unimarc – Yungay":            {"coords": (-39.816440905598505, -73.2415152399612), "direccion": "Yungay 420"},
    "Unimarc – Arauco":            {"coords": (-39.81309398073948, -73.2473120850604), "direccion": "Arauco 697"},
    "Unimarc – Aguirre Cerda":     {"coords": (-39.812999338251586, -73.22205854418874), "direccion": "Av. Pedro Aguirre Cerda 400"},
}
# ---- Información de universidades
universities = {
    "UACh Campus Isla Teja": {
        "coords": (-39.806088494536944, -73.25164778408663),
        "direccion": "Av. Elena Haverbeck s/n, Valdivia"
    },
    "UACh Campus Miraflores": {
        "coords": (-39.8329479334262, -73.2511942443009),
        "direccion": "General Lagos 2086, Valdivia"
    },
    "San Sebastián": {
        "coords": (-39.82145384984739, -73.24995683146737),
        "direccion": "General Lagos 1163, Valdivia."
    },
    "Sede Santo Tomás Valdivia": {
        "coords": (-39.81735094591222, -73.23314353146745),
        "direccion": "Av. Ramón Picarte 1160, Valdivia."
    },
    "Inacap": {
        "coords": (-39.80496976406447, -73.21489143331709),
        "direccion": "Av. Pedro Aguirre Cerda 2115, Valdivia."
    }
}

supermarket_colors = {
    "Acuenta": "blue",
    "Eltit": "green",
    "El Trébol": "purple",
    "Jumbo": "orange",
    "Santa Isabel": "red",
    "Unimarc": "darkred"
}

# Crear mapa centrado en Valdivia
m = folium.Map(location=[-39.82, -73.24], zoom_start=13)

# Agregar marcadores de supermercados
for name, info in supermarkets.items():
    color = "gray"  # valor por defecto
    for marca, c in supermarket_colors.items():
        if marca.lower() in name.lower():
            color = c
            break

    folium.Marker(
        location=info["coords"],
        popup=f"<b>{name}</b><br>{info['direccion']}",
        icon=folium.Icon(color=color)
    ).add_to(m)

# Agregar marcadores de universidades
for name, info in universities.items():
    folium.Marker(
        location=info["coords"],
        popup=f"<b>{name}</b><br>{info['direccion']}",
        icon=folium.Icon(color="cadetblue", icon="graduation-cap", prefix='fa')
    ).add_to(m)

# Mostrar el mapa en Streamlit
st.subheader("🗺️ Mapa de supermercados en Valdivia")
st_data = st_folium(m, width=700, height=500)

# Mostrar información al hacer clic en un marcador
if st_data and st_data.get("last_object_clicked"):
    clicked = st_data["last_object_clicked"]
    lat, lon = clicked["lat"], clicked["lng"]

# Inicializar variables de sesión si no existen
if 'primer_seleccionado' not in st.session_state:
    st.session_state.primer_seleccionado = None
if 'segundo_seleccionado' not in st.session_state:
    st.session_state.segundo_seleccionado = None

# Mostrar información al hacer clic en un marcador
if st_data and st_data.get("last_object_clicked"):
    clicked = st_data["last_object_clicked"]
    lat, lon = clicked["lat"], clicked["lng"]

    # Variable para controlar si encontramos el lugar clickeado
    found = False
    
    # Buscar en supermercados
    for name, info in supermarkets.items():
        if abs(info["coords"][0] - lat) < 0.0001 and abs(info["coords"][1] - lon) < 0.0001:
            st.sidebar.markdown(f"### Supermercado Seleccionado")
            st.sidebar.write(f"**Nombre:** {name}")
            st.sidebar.write(f"**Dirección:** {info['direccion']}")
            found = True
            
            # Si es el primer clic, guardar como primer seleccionado
            if st.session_state.primer_seleccionado is None:
                st.session_state.primer_seleccionado = name
            # Si ya hay un primer seleccionado y es diferente, guardar como segundo seleccionado
            elif st.session_state.segundo_seleccionado is None and name != st.session_state.primer_seleccionado:
                st.session_state.segundo_seleccionado = name
            break
            
    # Si no se encontró en supermercados, buscar en universidades
    if not found:
        for name, info in universities.items():
            if abs(info["coords"][0] - lat) < 0.0001 and abs(info["coords"][1] - lon) < 0.0001:
                st.sidebar.markdown(f"### Universidad Seleccionada")
                st.sidebar.write(f"**Nombre:** {name}")
                st.sidebar.write(f"**Dirección:** {info['direccion']}")
                found = True
                
                # Si es el primer clic, guardar como primer seleccionado
                if st.session_state.primer_seleccionado is None:
                    st.session_state.primer_seleccionado = name
                # Si ya hay un primer seleccionado y es diferente, guardar como segundo seleccionado
                elif st.session_state.segundo_seleccionado is None and name != st.session_state.primer_seleccionado:
                    st.session_state.segundo_seleccionado = name
                break

# ---- Cargar el CSV con las distancias desde la ruta específica ----
@st.cache_data
def load_distances():
    # Asume que el CSV está en una subcarpeta 'data' dentro del proyecto
    current_dir = Path(__file__).parent  # Carpeta donde está este script
    csv_path = current_dir / "utils" / "distance-to-nearest-supermarket" / "all_distances_complete.csv"
    return pd.read_csv(csv_path)

distances_df = load_distances()

# ---- Mapeo de nombres a IDs del CSV ----
name_to_id = {
    # Universidades
    "UACh Campus Isla Teja": "uach-teja",
    "UACh Campus Miraflores": "uach-mf",
    "San Sebastián": "uss",
    "Sede Santo Tomás Valdivia": "ust",
    "Inacap": "inacap",
    
    # Supermercados
    "Acuenta – Pedro Montt": "acuenta_1",
    "Acuenta – Picarte": "acuenta_2",
    "Acuenta – Anwandter": "acuenta_3",
    "Eltit": "eltit_1",
    "El Trébol – Simpson": "eltrebol_1",
    "El Trébol – Schneider": "eltrebol_2",
    "Jumbo": "jumbo_1",
    "Santa Isabel – Chacabuco": "santaisabel_1",
    "Santa Isabel – Picarte": "santaisabel_2",
    "Unimarc – Francia": "unimarc_1",
    "Unimarc – Yungay": "unimarc_2",
    "Unimarc – Arauco": "unimarc_3",
    "Unimarc – Aguirre Cerda": "unimarc_4",
}

#1. Primero verificamos si se hizo clic en el botón
if st.sidebar.button("🗑️ Eliminar selección", type="primary", key="reset_button"):
    st.session_state.primer_seleccionado = None
    st.session_state.segundo_seleccionado = None
    st.experimental_rerun()


# 2. Luego mostramos la información (solo si no se acaba de borrar)
if not st.session_state.get('reset_triggered', False):
    # Mostrar primer seleccionado
    if st.session_state.primer_seleccionado:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Primer Seleccionado:")
        st.sidebar.write(st.session_state.primer_seleccionado)

    # Mostrar segundo seleccionado
    if st.session_state.segundo_seleccionado:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Segundo Seleccionado:")
        st.sidebar.write(st.session_state.segundo_seleccionado)
        
        # Mostrar distancia
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Distancia entre:")
        st.sidebar.write(f"{st.session_state.primer_seleccionado} y {st.session_state.segundo_seleccionado}")
        
        id1 = name_to_id.get(st.session_state.primer_seleccionado)
        id2 = name_to_id.get(st.session_state.segundo_seleccionado)
        
        if id1 and id2:
            distance_row = distances_df[
                ((distances_df['origin'] == id1) & (distances_df['destination'] == id2)) |
                ((distances_df['origin'] == id2) & (distances_df['destination'] == id1))
            ]
            
            if not distance_row.empty:
                distance = distance_row.iloc[0]['distance']
                st.sidebar.write(f"**Distancia:** {distance} metros")
                st.sidebar.write(f"**Tipo de conexión:** {distance_row.iloc[0]['type']}")

# 3. Añadir un pequeño delay después de borrar
if st.session_state.get('reset_triggered', False):
    st.session_state.reset_triggered = False
    st.experimental_rerun()