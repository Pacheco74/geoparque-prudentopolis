import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Configuração da página
st.set_page_config(page_title="Geoparque Prudentópolis | 3D", layout="wide")

# Tentar buscar o token dos Secrets de forma segura
try:
    MAPBOX_TOKEN = st.secrets["MAPBOX_TOKEN"]
except:
    MAPBOX_TOKEN = None

@st.cache_data
def get_elevation_data():
    # Simulando relevo real da Serra da Esperança
    lat_center, lon_center = -25.1973, -50.9780
    lats = np.linspace(lat_center - 0.1, lat_center + 0.1, 80)
    lons = np.linspace(lon_center - 0.1, lon_center + 0.1, 80)
    data = []
    for lat in lats:
        for lon in lons:
            # Relevo sintético para teste
            elev = 850 + 200 * np.sin(lat*50) * np.cos(lon*50)
            data.append({'lat': lat, 'lon': lon, 'elevation': elev})
    return pd.DataFrame(data)

def main():
    st.title("🛰️ Geoparque Prudentópolis - Visualização de Satélite")

    # Sidebar
    with st.sidebar:
        st.header("Configurações")
        map_style = st.selectbox(
            "Camada de Fundo",
            ["Satélite", "Dark", "Outdoors"],
            index=0
        )
        exaggeration = st.slider("Exagero do Relevo", 1.0, 5.0, 2.0)

    styles = {
        "Satélite": "mapbox://styles/mapbox/satellite-v9",
        "Dark": "mapbox://styles/mapbox/dark-v10",
        "Outdoors": "mapbox://styles/mapbox/outdoors-v11"
    }

    elevation_df = get_elevation_data()

    # Configuração do Mapa
    view_state = pdk.ViewState(
        latitude=-25.1973, longitude=-50.9780, 
        zoom=11, pitch=50, bearing=0
    )

    # Camada de Terreno 3D
    layer = pdk.Layer(
        'GridLayer',
        data=elevation_df,
        get_position='[lon, lat]',
        get_elevation='elevation',
        elevation_scale=exaggeration,
        extruded=True,
        # Cor transparente para deixar o satélite brilhar por baixo
        get_fill_color='[255, 255, 255, 20]' if map_style == "Satélite" else '[184, 134, 11, 150]',
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style=styles[map_style],
        api_keys={'mapbox': MAPBOX_TOKEN} if MAPBOX_TOKEN else None
    ))

    if not MAPBOX_TOKEN:
        st.warning("⚠️ Token do Mapbox não detectado. As imagens de satélite podem não carregar em alta resolução.")

if __name__ == "__main__":
    main()
