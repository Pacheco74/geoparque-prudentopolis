"""
Dashboard 3D de Topografia e Geodiversidade - Geoparque Prudentópolis/PR
Autor: Sistema de Geoprocessamento Avançado
Versão: 1.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import geopandas as gpd
from pathlib import Path
import io
import base64

# Configuração da página
st.set_page_config(
    page_title="Geoparque Prudentópolis | Dashboard 3D",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Personalizado - Tema Dark Geological
def load_css():
    st.markdown("""
    <style>
    /* Tema Dark Geological com detalhes em cobre/dourado */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
    }
    
    .-header {
        background: linear-gradient(90deg, #1a1a1a 0%, #2d2416 50%, #1a1a1a 100%);
        padding: 2rem;
        border-radius: 10px;
        border: 2px solid #b8860b;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(184, 134, 11, 0.2);
    }
    
    .-title {
        color: #d4af37;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        margin: 0;
    }
    
    .subtitle {
        color: #b8860b;
        text-align: center;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #1a1a1a, #252525);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #b8860b;
        box-shadow: 0 4px 16px rgba(184, 134, 11, 0.15);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #b8860b;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value {
        color: #d4af37;
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-delta {
        color: #8b7355;
        font-size: 0.85rem;
    }
    
    .info-box {
        background: rgba(184, 134, 11, 0.1);
        border-left: 4px solid #d4af37;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: #e0e0e0;
    }
    
    /* Estilo dos botões */
    .stButton>button {
        background: linear-gradient(135deg, #b8860b 0%, #d4af37 100%);
        color: #000;
        font-weight: 700;
        border: none;
        border-radius: 5px;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #d4af37 0%, #ffd700 100%);
        box-shadow: 0 4px 16px rgba(212, 175, 55, 0.5);
        transform: translateY(-2px);
    }
    
    /* Estilo dos sliders */
    .stSlider>div>div>div>div {
        background-color: #b8860b;
    }
    
    /* Tabelas */
    .dataframe {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
    }
    
    .dataframe th {
        background-color: #2d2416 !important;
        color: #d4af37 !important;
        font-weight: 700;
    }
    
    .dataframe td {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #0a0a0a;
    }
    
    .stSelectbox label, .stSlider label, .stFileUploader label {
        color: #d4af37 !important;
        font-weight: 600;
    }
    
    hr {
        border-color: #b8860b;
        opacity: 0.3;
    }
    </style>
    """, unsafe_allow_html=True)

# Função para gerar dados topográficos sintéticos (substituir por dados reais SRTM)
@st.cache_data
def generate_elevation_data(center_lat=-25.1973, center_lon=-50.9780, grid_size=100):
    """
    Gera dados de elevação sintéticos para Prudentópolis
    Em produção, substituir por leitura de arquivos SRTM .tif
    """
    
    # Criar grid de coordenadas
    lat_range = np.linspace(center_lat - 0.15, center_lat + 0.15, grid_size)
    lon_range = np.linspace(center_lon - 0.15, center_lon + 0.15, grid_size)
    
    data = []
    
    for i, lat in enumerate(lat_range):
        for j, lon in enumerate(lon_range):
            # Simulação de relevo complexo (Serra da Esperança)
            # Base elevada com variações
            base_elevation = 800
            
            # Componente de serra (inclinação NE-SW)
            serra_component = 300 * np.sin((lat - center_lat) * 30) * np.cos((lon - center_lon) * 20)
            
            # Cânions e vales
            canyon_component = -150 * np.exp(-((lat - center_lat + 0.05)**2 + (lon - center_lon - 0.03)**2) / 0.002)
            
            # Rugosidade do terreno basáltico
            noise = np.random.normal(0, 25)
            
            elevation = base_elevation + serra_component + canyon_component + noise
            elevation = max(500, min(1400, elevation))  # Limites realistas para a região
            
            data.append({
                'lat': lat,
                'lon': lon,
                'elevation': elevation
            })
    
    return pd.DataFrame(data)

# Função para calcular declividade
def calculate_slope(elevation_df, grid_size=100):
    """Calcula a declividade (slope) a partir dos dados de elevação"""
    
    # Reshape para matriz
    elevation_matrix = elevation_df['elevation'].values.reshape(grid_size, grid_size)
    
    # Calcular gradientes
    grad_y, grad_x = np.gradient(elevation_matrix)
    
    # Calcular slope em graus
    slope = np.arctan(np.sqrt(grad_x**2 + grad_y**2)) * (180 / np.pi)
    
    # Adicionar ao dataframe
    elevation_df['slope'] = slope.flatten()
    
    return elevation_df

# Dados de cachoeiras (geossítios)
@st.cache_data
def get_waterfalls_data():
    """Dados das principais cachoeiras de Prudentópolis"""
    
    waterfalls = [
        {
            'name': 'Salto São Francisco',
            'lat': -25.1523,
            'lon': -50.9234,
            'height': 196,
            'elevation': 920,
            'description': 'Segunda maior queda livre do Brasil'
        },
        {
            'name': 'Cachoeira Véu de Noiva',
            'lat': -25.1789,
            'lon': -50.9456,
            'height': 120,
            'elevation': 850,
            'description': 'Queda espetacular em formato de véu'
        },
        {
            'name': 'Salto Barão do Rio Branco',
            'lat': -25.2134,
            'lon': -51.0123,
            'height': 85,
            'elevation': 780,
            'description': 'Formação em degraus de basalto'
        },
        {
            'name': 'Cachoeira da Mariquinha',
            'lat': -25.1645,
            'lon': -50.9678,
            'height': 75,
            'elevation': 890,
            'description': 'Acesso por trilha em mata atlântica'
        },
        {
            'name': 'Salto Manduri',
            'lat': -25.2456,
            'lon': -51.0345,
            'height': 95,
            'elevation': 760,
            'description': 'Piscina natural na base da queda'
        },
        {
            'name': 'Cachoeira Santa Maria',
            'lat': -25.1912,
            'lon': -50.9890,
            'height': 60,
            'elevation': 820,
            'description': 'Conjunto de três quedas em sequência'
        }
    ]
    
    return pd.DataFrame(waterfalls)

# Função para criar mapa 3D com PyDeck
#def create_3d_terrain_map(elevation_df, waterfalls_df, exaggeration=3.0, show_waterfalls=True):
    """Cria visualização 3D do terreno usando PyDeck"""
    def create_3d_terrain_map(elevation_df, waterfalls_df, exaggeration=3.0, show_waterfalls=True, map_style='mapbox://styles/mapbox/satellite-v9', mapbox_key= None):
    
    # ... (mantenha o código das camadas terrain_layer, waterfalls_layer e text_layer igual ao seu)
    
    # Renderizar mapa
        r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style=map_style, # Usa o estilo selecionado na sidebar
        api_keys={'mapbox': mapbox_key} if mapbox_key else None,
        tooltip={
            'html': '<b>Elevação:</b> {elevation}m<br/><b>Nome:</b> {name}',
            'style': {'backgroundColor': '#1a1a1a', 'color': '#d4af37'}
        }
    )
    return r
    # Preparar dados de elevação para o GridLayer
    grid_data = elevation_df.copy()
    
    # Camada de terreno 3D
    terrain_layer = pdk.Layer(
        'GridLayer',
        data=grid_data,
        get_position='[lon, lat]',
        get_elevation='elevation',
        elevation_scale=exaggeration,
        extruded=True,
        coverage=1,
        get_fill_color='[200 - elevation/10, 100 + elevation/10, 50, 180]',
        pickable=True,
        auto_highlight=True
    )
    
    layers = [terrain_layer]
    
    # Camada de cachoeiras
    if show_waterfalls:
        waterfalls_layer = pdk.Layer(
            'ColumnLayer',
            data=waterfalls_df,
            get_position='[lon, lat]',
            get_elevation='elevation',
            elevation_scale=exaggeration,
            radius=500,
            get_fill_color='[212, 175, 55, 250]',
            pickable=True,
            auto_highlight=True
        )
        
        # Camada de texto para nomes
        text_layer = pdk.Layer(
            'TextLayer',
            data=waterfalls_df,
            get_position='[lon, lat]',
            get_text='name',
            get_size=16,
            get_color='[255, 215, 0, 255]',
            get_angle=0,
            get_alignment_baseline='"bottom"'
        )
        
        layers.extend([waterfalls_layer, text_layer])
    
    # Configuração da visualização
    view_state = pdk.ViewState(
        latitude=-25.1973,
        longitude=-50.9780,
        zoom=11,
        pitch=60,
        bearing=0
    )
    
    # Renderizar mapa
    r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/dark-v10',
        tooltip={
            'html': '<b>Elevação:</b> {elevation}m<br/><b>Nome:</b> {name}<br/><b>Altura da queda:</b> {height}m',
            'style': {
                'backgroundColor': '#1a1a1a',
                'color': '#d4af37',
                'border': '2px solid #b8860b'
            }
        }
    )
    
    return r

# Função para criar mapa de calor de declividade
def create_slope_heatmap(elevation_df):
    """Cria mapa de calor da declividade usando Plotly"""
    
    # Preparar dados
    grid_size = int(np.sqrt(len(elevation_df)))
    lats = elevation_df['lat'].unique()
    lons = elevation_df['lon'].unique()
    slope_matrix = elevation_df['slope'].values.reshape(grid_size, grid_size)
    
    fig = go.Figure(data=go.Heatmap(
        x=lons,
        y=lats,
        z=slope_matrix,
        colorscale=[
            [0, '#1a1a1a'],
            [0.2, '#2d4a2b'],
            [0.4, '#5d7d4e'],
            [0.6, '#b8860b'],
            [0.8, '#d4af37'],
            [1, '#ff4444']
        ],
        colorbar=dict(
            title=dict(text='Declividade (°)', 
            side='right'),
            tickmode='linear',
            tick0=0,
            dtick=10,
            tickfont=dict(color='#d4af37'),
            titlefont=dict(color='#d4af37')
        )
    ))
    
    fig.update_layout(
        title={
            'text': 'Mapa de Declividade - Análise de Slope',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'color': '#d4af37', 'size': 18}
        },
        xaxis_title='Longitude',
        yaxis_title='Latitude',
        plot_bgcolor='#0a0a0a',
        paper_bgcolor='#1a1a1a',
        font=dict(color='#e0e0e0'),
        xaxis=dict(gridcolor='#333', color='#d4af37'),
        yaxis=dict(gridcolor='#333', color='#d4af37'),
        height=500
    )
    
    return fig

# Função para calcular perfil altimétrico
def create_elevation_profile(elevation_df, point1, point2, num_points=100):
    """Cria perfil de elevação entre dois pontos"""
    
    lat1, lon1 = point1
    lat2, lon2 = point2
    
    # Interpolar pontos ao longo da linha
    lats = np.linspace(lat1, lat2, num_points)
    lons = np.linspace(lon1, lon2, num_points)
    
    elevations = []
    distances = []
    
    for i, (lat, lon) in enumerate(zip(lats, lons)):
        # Encontrar elevação mais próxima
        distances_to_point = np.sqrt(
            (elevation_df['lat'] - lat)**2 + 
            (elevation_df['lon'] - lon)**2
        )
        nearest_idx = distances_to_point.idxmin()
        elevations.append(elevation_df.loc[nearest_idx, 'elevation'])
        
        # Calcular distância acumulada (aproximação)
        if i == 0:
            distances.append(0)
        else:
            dist = np.sqrt((lat - lats[i-1])**2 + (lon - lons[i-1])**2) * 111  # km
            distances.append(distances[-1] + dist)
    
    # Criar gráfico
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=distances,
        y=elevations,
        mode='lines',
        fill='tozeroy',
        line=dict(color='#d4af37', width=3),
        fillcolor='rgba(184, 134, 11, 0.3)',
        name='Perfil de Elevação'
    ))
    
    fig.update_layout(
        title={
            'text': 'Perfil Altimétrico - Análise de Transecto',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'color': '#d4af37', 'size': 18}
        },
        xaxis_title='Distância (km)',
        yaxis_title='Elevação (m)',
        plot_bgcolor='#0a0a0a',
        paper_bgcolor='#1a1a1a',
        font=dict(color='#e0e0e0'),
        xaxis=dict(gridcolor='#333', color='#d4af37'),
        yaxis=dict(gridcolor='#333', color='#d4af37'),
        hovermode='x unified',
        height=400
    )
    
    return fig

# Interface Principal
def ():
    load_css()
    
    # Cabeçalho
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🏔️ GEOPARQUE PRUDENTÓPOLIS</h1>
        <p class="subtitle">Dashboard 3D de Topografia e Geodiversidade | Juliana Thaisa Rodrigues Pacheco</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Controles
    with st.sidebar:
        st.markdown("## ⚙️ Controles de Visualização")
# --- Adicione isso dentro do 'with st.sidebar:' ---
      st.markdown("---")
      st.markdown("## 🛰️ Camadas de Fundo")
     map_style_choice = st.sidebar.radio(
    "Escolha o estilo do mapa:",
    options=["Satélite", "Dark Geológico", "Relevo (Light)"],
    index=0
)

# Mapeamento para estilos oficiais do Mapbox
map_styles = {
    "Satélite": "mapbox://styles/mapbox/satellite-v9",
    "Dark Geológico": "mapbox://styles/mapbox/dark-v10",
    "Relevo (Light)": "mapbox://styles/mapbox/outdoors-v11"
}

# Campo opcional para o Token (Se você não tiver um, o satélite pode não carregar ou ficar em baixa resolução)
mapbox_token = st.sidebar.text_input("Mapbox Access Token (Opcional)", type="password", help="Cole seu token do mapbox.com para liberar satélite em HD")



        
        st.markdown("---")

            
        # Exagero vertical
        exaggeration = st.slider(
            "Exagero Vertical do Relevo",
            min_value=1.0,
            max_value=10.0,
            value=3.0,
            step=0.5,
            help="Aumenta a percepção das variações de altitude"
        )
        
        # Mostrar cachoeiras
        show_waterfalls = st.checkbox("Exibir Geossítios (Cachoeiras)", value=True)
        
        # Resolução do grid
        grid_resolution = st.selectbox(
            "Resolução do Terreno",
            options=[50, 100, 150],
            index=1,
            help="Maior = mais detalhes (mais lento)"
        )
        
        st.markdown("---")
        st.markdown("## 📊 Análises Disponíveis")
        
        show_slope = st.checkbox("Mapa de Declividade", value=True)
        show_profile = st.checkbox("Perfil Altimétrico", value=False)
        
        st.markdown("---")
        st.markdown("## 📤 Upload de Dados")
        
        uploaded_shapefile = st.file_uploader(
            "Shapefile/GeoJSON",
            type=['shp', 'geojson', 'json'],
            help="Adicione trilhas ou limites de preservação"
        )
        
        st.markdown("---")
        st.markdown("""
        <div class="info-box">
        <strong>💡 Dica:</strong><br>
        Rotacione o mapa 3D arrastando com o mouse e use o scroll para zoom.
        </div>
        """, unsafe_allow_html=True)
    
    # Carregar dados
    with st.spinner('Processando dados topográficos...'):
        elevation_df = generate_elevation_data(grid_size=grid_resolution)
        elevation_df = calculate_slope(elevation_df, grid_size=grid_resolution)
        waterfalls_df = get_waterfalls_data()
    
    # Estatísticas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Altitude Máxima</div>
            <div class="metric-value">{elevation_df['elevation'].max():.0f}m</div>
            <div class="metric-delta">Serra da Esperança</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Altitude Mínima</div>
            <div class="metric-value">{elevation_df['elevation'].min():.0f}m</div>
            <div class="metric-delta">Vales fluviais</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Desnível Total</div>
            <div class="metric-value">{elevation_df['elevation'].max() - elevation_df['elevation'].min():.0f}m</div>
            <div class="metric-delta">Amplitude altimétrica</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Geossítios</div>
            <div class="metric-value">{len(waterfalls_df)}</div>
            <div class="metric-delta">Cachoeiras catalogadas</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualização 3D principal
    st.markdown("### 🗺️ Visualização Tridimensional do Relevo")
    
   # --- Procure onde você chama a função e substitua por: ---
terrain_map = create_3d_terrain_map(
    elevation_df, 
    waterfalls_df, 
    exaggeration=exaggeration,
    show_waterfalls=show_waterfalls,
    map_style=map_styles[map_style_choice], # Passa a escolha do usuário
    mapbox_key=mapbox_token if mapbox_token else None
)
    )
    
    st.pydeck_chart(terrain_map, use_container_width=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>🎯 Navegação 3D:</strong> Arraste para rotacionar | Ctrl + Arraste para inclinar | Scroll para zoom | Clique nos pontos para informações
    </div>
    """, unsafe_allow_html=True)
    
    # Layout em colunas para análises
    if show_slope or show_profile:
        st.markdown("---")
        st.markdown("### 📈 Análises Geomorfológicas")
        
        analysis_col1, analysis_col2 = st.columns([1, 1])
        
        with analysis_col1:
            if show_slope:
                st.markdown("#### Mapa de Declividade")
                slope_map = create_slope_heatmap(elevation_df)
                st.plotly_chart(slope_map, use_container_width=True)
                
                # Estatísticas de declividade
                avg_slope = elevation_df['slope'].mean()
                max_slope = elevation_df['slope'].max()
                
                st.markdown(f"""
                <div class="info-box">
                <strong>📊 Análise de Inclinação:</strong><br>
                • Declividade média: <strong>{avg_slope:.1f}°</strong><br>
                • Declividade máxima: <strong>{max_slope:.1f}°</strong><br>
                • Áreas críticas (>30°): <strong>{(elevation_df['slope'] > 30).sum() / len(elevation_df) * 100:.1f}%</strong>
                </div>
                """, unsafe_allow_html=True)
        
        with analysis_col2:
            if show_profile:
                st.markdown("#### Perfil Altimétrico Interativo")
                
                st.markdown("""
                <div class="info-box">
                <strong>📍 Selecione dois pontos:</strong><br>
                Defina as coordenadas de início e fim do transecto
                </div>
                """, unsafe_allow_html=True)
                
                p1_col, p2_col = st.columns(2)
                
                with p1_col:
                    st.markdown("**Ponto Inicial**")
                    p1_lat = st.number_input("Latitude 1", value=-25.15, format="%.4f", key="p1_lat")
                    p1_lon = st.number_input("Longitude 1", value=-50.92, format="%.4f", key="p1_lon")
                
                with p2_col:
                    st.markdown("**Ponto Final**")
                    p2_lat = st.number_input("Latitude 2", value=-25.25, format="%.4f", key="p2_lat")
                    p2_lon = st.number_input("Longitude 2", value=-51.03, format="%.4f", key="p2_lon")
                
                if st.button("🔍 Gerar Perfil", key="generate_profile"):
                    profile_fig = create_elevation_profile(
                        elevation_df,
                        (p1_lat, p1_lon),
                        (p2_lat, p2_lon)
                    )
                    st.plotly_chart(profile_fig, use_container_width=True)
    
    # Tabela de cachoeiras
    st.markdown("---")
    st.markdown("### 💧 Ranking das Maiores Cachoeiras")
    
    waterfalls_display = waterfalls_df.sort_values('height', ascending=False).copy()
    waterfalls_display['rank'] = range(1, len(waterfalls_display) + 1)
    waterfalls_display = waterfalls_display[['rank', 'name', 'height', 'elevation', 'description']]
    waterfalls_display.columns = ['#', 'Nome', 'Altura (m)', 'Altitude (m)', 'Descrição']
    
    st.dataframe(
        waterfalls_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "#": st.column_config.NumberColumn(format="%d"),
            "Altura (m)": st.column_config.NumberColumn(format="%.0f m"),
            "Altitude (m)": st.column_config.NumberColumn(format="%.0f m"),
        }
    )
    
    # Processamento de arquivo uploadado
    if uploaded_shapefile is not None:
        st.markdown("---")
        st.markdown("### 📁 Dados Carregados pelo Usuário")
        
        try:
            # Tentar ler o arquivo
            if uploaded_shapefile.name.endswith('.geojson') or uploaded_shapefile.name.endswith('.json'):
                gdf = gpd.read_file(uploaded_shapefile)
                st.success(f"✅ Arquivo carregado: {len(gdf)} feições encontradas")
                st.dataframe(gdf.head(), use_container_width=True)
            else:
                st.info("💡 Para Shapefiles, faça upload de um arquivo .zip contendo todos os componentes (.shp, .shx, .dbf, .prj)")
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
    
    # Rodapé
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #8b7355; padding: 2rem;">
        <p><strong>Geoparque Prudentópolis - Conservação e Desenvolvimento Sustentável</strong></p>
        <p style="font-size: 0.85rem;">Dashboard desenvolvido com Python, Streamlit, PyDeck e Plotly | Dados topográficos SRTM</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
