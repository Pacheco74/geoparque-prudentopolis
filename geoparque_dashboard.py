import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Geoparque Prudentópolis | Dashboard 3D",
    page_icon="🏔️",
    layout="wide"
)

# Funções de Dados (Simuladas para Prudentópolis)
@st.cache_data
def get_elevation_data():
    lat_center, lon_center = -25.1973, -50.9780
    lats = np.linspace(lat_center - 0.1, lat_center + 0.1, 50)
    lons = np.linspace(lon_center - 0.1, lon_center + 0.1, 50)
    data = []
    for lat in lats:
        for lon in lons:
            elev = 800 + 150 * np.sin(lat*100) * np.cos(lon*100)
            data.append({'lat': lat, 'lon': lon, 'elevation': elev})
    return pd.DataFrame(data)

@st.cache_data
def get_waterfalls_data():
    return pd.DataFrame([
        {'name': 'Salto São Francisco', 'lat': -25.1523, 'lon': -50.9234, 'height': 196},
        {'name': 'Salto Barão do Rio Branco', 'lat': -25.2134, 'lon': -51.0123, 'height': 85}
    ])

def main():
    st.title("🏔️ GEOPARQUE PRUDENTÓPOLIS - Satélite & 3D")
    
    # --- BARRA LATERAL (Sidebar) ---
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # 🛰️ NOVIDADE: SELETOR DE SATÉLITE
        map_style_choice = st.radio(
            "Visualização de Fundo:",
            options=["Satélite", "Mapa Dark", "Terreno Outdoors"],
            index=0
        )
        
        st.markdown("---")
        exaggeration = st.slider("Exagero Vertical", 1.0, 10.0, 3.0)
        show_waterfalls = st.checkbox("Exibir Geossítios (Cachoeiras)", value=True)
        
        # Token do Mapbox (Necessário para satélite de alta qualidade)
        mapbox_token = st.text_input("Mapbox Access Token (Opcional)", type="password")

    # Mapeamento de Estilos
    styles = {
        "Satélite": "mapbox://styles/mapbox/satellite-v9",
        "Mapa Dark": "mapbox://styles/mapbox/dark-v10",
        "Terreno Outdoors": "mapbox://styles/mapbox/outdoors-v11"
    }

    # Carregar Dados
    elevation_df = get_elevation_data()
    waterfalls_df = get_waterfalls_data()

    # --- MAPA 3D (PYDECK) ---
    st.subheader(f"Visualização em Modo: {map_style_choice}")
    
    view_state = pdk.ViewState(
        latitude=-25.1973, longitude=-50.9780, 
        zoom=11, pitch=60, bearing=0
    )

    layers = [
        pdk.Layer(
            'GridLayer',
            data=elevation_df,
            get_position='[lon, lat]',
            get_elevation='elevation',
            elevation_scale=exaggeration,
            extruded=True,
            get_fill_color='[100, 150, 100, 100]' if map_style_choice == "Satélite" else '[200, 100, 50, 150]',
            pickable=True,
        )
    ]

    if show_waterfalls:
        layers.append(pdk.Layer(
            'ColumnLayer',
            data=waterfalls_df,
            get_position='[lon, lat]',
            get_radius=300,
            get_fill_color='[255, 215, 0, 255]',
            pickable=True,
        ))

    st.pydeck_chart(pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style=styles[map_style_choice],
        api_keys={'mapbox': mapbox_token} if mapbox_token else None,
        tooltip=True
    ))

    st.info("💡 **Dica:** Se o Satélite não carregar, use um Access Token gratuito do Mapbox.com")

if __name__ == "__main__":
    main()
