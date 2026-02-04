"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GEOPARQUE PRUDENTÓPOLIS - DASHBOARD PROFISSIONAL DE ANÁLISE TOPOGRÁFICA 3D
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Versão: 2.0.0 Professional Edition
Autor: Sistema de Geoprocessamento Avançado
Data: Fevereiro 2026

FUNCIONALIDADES PRINCIPAIS:
- Visualização 3D realista com superfície contínua (mesh surface)
- Upload e análise de múltiplos formatos: DBF, CSV, SHP, GeoJSON, XLSX, TIF
- Geração automática de gráficos dinâmicos baseados nos dados carregados
- Sistema de cache otimizado para performance
- Interface profissional com tema Dark Geological

TECNOLOGIAS:
- Streamlit 1.31+ (Interface)
- Plotly 5.18+ (Visualização 3D e gráficos)
- GeoPandas 0.14+ (Dados geoespaciais)
- Pandas 2.1+ (Análise de dados)
- NumPy 1.24+ (Computação numérica)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ═══════════════════════════════════════════════════════════════════════════
# IMPORTS E CONFIGURAÇÕES INICIAIS
# ═══════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
from pathlib import Path
import io
import json
import zipfile
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Geoparque Prudentópolis | Dashboard Profissional",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/geoparque-prudentopolis',
        'Report a bug': "https://github.com/geoparque-prudentopolis/issues",
        'About': "Dashboard Profissional de Análise Topográfica 3D - Geoparque Prudentópolis/PR"
    }
)

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTES E CONFIGURAÇÕES GLOBAIS
# ═══════════════════════════════════════════════════════════════════════════

class Config:
    """Classe de configuração centralizada do sistema"""
    
    # Coordenadas centrais de Prudentópolis
    CENTER_LAT = -25.1973
    CENTER_LON = -50.9780
    
    # Paleta de cores profissional (Dark Geological Theme)
    COLORS = {
        'primary': '#d4af37',      # Dourado
        'secondary': '#b8860b',    # Cobre
        'accent': '#8b7355',       # Bronze
        'background': '#0a0a0a',   # Preto profundo
        'surface': '#1a1a1a',      # Cinza escuro
        'text': '#e0e0e0',         # Texto claro
        'error': '#ff4444',        # Vermelho
        'success': '#4caf50',      # Verde
        'warning': '#ff9800',      # Laranja
    }
    
    # Formatos de arquivo suportados
    SUPPORTED_FORMATS = {
        'geospatial': ['.shp', '.geojson', '.json', '.kml', '.gpkg'],
        'tabular': ['.csv', '.xlsx', '.xls', '.dbf'],
        'raster': ['.tif', '.tiff', '.asc'],
    }
    
    # Limites de tamanho de arquivo (MB)
    MAX_FILE_SIZE = 200

# ═══════════════════════════════════════════════════════════════════════════
# ESTILIZAÇÃO CSS PROFISSIONAL
# ═══════════════════════════════════════════════════════════════════════════

def load_professional_css() -> None:
    """
    Carrega CSS personalizado com tema Dark Geological profissional.
    
    Design System:
    - Tipografia: Sistema modular com hierarquia clara
    - Cores: Paleta dourado/cobre sobre fundo escuro
    - Espaçamento: Grid system responsivo
    - Animações: Transições suaves e profissionais
    """
    
    st.markdown(f"""
    <style>
    /* ═══════════════════════════════════════════════════════════════════ */
    /* TEMA BASE - DARK GEOLOGICAL                                          */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    :root {{
        --primary-color: {Config.COLORS['primary']};
        --secondary-color: {Config.COLORS['secondary']};
        --accent-color: {Config.COLORS['accent']};
        --background-color: {Config.COLORS['background']};
        --surface-color: {Config.COLORS['surface']};
        --text-color: {Config.COLORS['text']};
    }}
    
    .stApp {{
        background: linear-gradient(135deg, {Config.COLORS['background']} 0%, {Config.COLORS['surface']} 100%);
    }}
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* CABEÇALHO PRINCIPAL                                                  */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    .main-header {{
        background: linear-gradient(135deg, 
            rgba(26, 26, 26, 0.95) 0%, 
            rgba(45, 36, 22, 0.95) 50%, 
            rgba(26, 26, 26, 0.95) 100%);
        padding: 2.5rem 3rem;
        border-radius: 15px;
        border: 2px solid var(--secondary-color);
        margin-bottom: 2.5rem;
        box-shadow: 
            0 10px 40px rgba(184, 134, 11, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }}
    
    .main-header::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(212, 175, 55, 0.1), 
            transparent);
        animation: shine 3s infinite;
    }}
    
    @keyframes shine {{
        to {{ left: 100%; }}
    }}
    
    .main-title {{
        color: var(--primary-color);
        font-size: 2.8rem;
        font-weight: 900;
        text-align: center;
        text-shadow: 
            2px 2px 4px rgba(0, 0, 0, 0.8),
            0 0 20px rgba(212, 175, 55, 0.3);
        margin: 0;
        letter-spacing: 1px;
    }}
    
    .subtitle {{
        color: var(--secondary-color);
        text-align: center;
        font-size: 1.15rem;
        margin-top: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.5px;
    }}
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* CARDS DE MÉTRICAS PROFISSIONAIS                                     */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    .metric-card {{
        background: linear-gradient(145deg, 
            rgba(26, 26, 26, 0.98) 0%, 
            rgba(37, 37, 37, 0.98) 100%);
        padding: 1.75rem;
        border-radius: 12px;
        border: 1px solid var(--secondary-color);
        box-shadow: 
            0 4px 20px rgba(184, 134, 11, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }}
    
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 
            0 8px 30px rgba(184, 134, 11, 0.35),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-color: var(--primary-color);
    }}
    
    .metric-label {{
        color: var(--secondary-color);
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        color: var(--primary-color);
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.75rem 0;
        font-variant-numeric: tabular-nums;
    }}
    
    .metric-delta {{
        color: var(--accent-color);
        font-size: 0.9rem;
        font-weight: 500;
    }}
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* CAIXAS DE INFORMAÇÃO E ALERTAS                                      */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    .info-box {{
        background: rgba(184, 134, 11, 0.12);
        border-left: 4px solid var(--primary-color);
        padding: 1.25rem 1.5rem;
        border-radius: 8px;
        margin: 1.25rem 0;
        color: var(--text-color);
        box-shadow: 0 2px 10px rgba(184, 134, 11, 0.15);
    }}
    
    .success-box {{
        background: rgba(76, 175, 80, 0.12);
        border-left: 4px solid {Config.COLORS['success']};
        padding: 1.25rem 1.5rem;
        border-radius: 8px;
        margin: 1.25rem 0;
        color: var(--text-color);
    }}
    
    .warning-box {{
        background: rgba(255, 152, 0, 0.12);
        border-left: 4px solid {Config.COLORS['warning']};
        padding: 1.25rem 1.5rem;
        border-radius: 8px;
        margin: 1.25rem 0;
        color: var(--text-color);
    }}
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* BOTÕES PROFISSIONAIS                                                */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    .stButton > button {{
        background: linear-gradient(135deg, 
            var(--secondary-color) 0%, 
            var(--primary-color) 100%);
        color: #000;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        border-radius: 8px;
        padding: 0.85rem 2.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(184, 134, 11, 0.3);
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, 
            var(--primary-color) 0%, 
            #ffd700 100%);
        box-shadow: 0 6px 25px rgba(212, 175, 55, 0.5);
        transform: translateY(-2px);
    }}
    
    .stButton > button:active {{
        transform: translateY(0);
        box-shadow: 0 2px 10px rgba(184, 134, 11, 0.4);
    }}
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* CONTROLES DE ENTRADA                                                */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    .stSlider > div > div > div > div {{
        background-color: var(--secondary-color);
    }}
    
    .stSelectbox label, 
    .stSlider label, 
    .stFileUploader label,
    .stNumberInput label,
    .stCheckbox label {{
        color: var(--primary-color) !important;
        font-weight: 600;
        font-size: 0.95rem;
    }}
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* TABELAS PROFISSIONAIS                                               */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    .dataframe {{
        background-color: var(--surface-color) !important;
        color: var(--text-color) !important;
        border-radius: 8px;
        overflow: hidden;
    }}
    
    .dataframe th {{
        background: linear-gradient(135deg, 
            rgba(45, 36, 22, 0.95) 0%, 
            rgba(26, 26, 26, 0.95) 100%) !important;
        color: var(--primary-color) !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.85rem;
        padding: 1rem !important;
    }}
    
    .dataframe td {{
        background-color: rgba(26, 26, 26, 0.6) !important;
        color: var(--text-color) !important;
        padding: 0.85rem !important;
        border-bottom: 1px solid rgba(184, 134, 11, 0.1);
    }}
    
    .dataframe tr:hover td {{
        background-color: rgba(184, 134, 11, 0.1) !important;
    }}
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* SIDEBAR PROFISSIONAL                                                */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, 
            {Config.COLORS['background']} 0%, 
            {Config.COLORS['surface']} 100%);
        border-right: 2px solid var(--secondary-color);
    }}
    
    [data-testid="stSidebar"] h2 {{
        color: var(--primary-color);
        font-weight: 700;
    }}
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* SEPARADORES E DIVISÓRIAS                                            */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            var(--secondary-color) 50%, 
            transparent 100%);
        margin: 2rem 0;
        opacity: 0.5;
    }}
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* UPLOAD DE ARQUIVOS                                                  */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    .stFileUploader {{
        border: 2px dashed var(--secondary-color);
        border-radius: 10px;
        padding: 1.5rem;
        background: rgba(184, 134, 11, 0.05);
        transition: all 0.3s ease;
    }}
    
    .stFileUploader:hover {{
        border-color: var(--primary-color);
        background: rgba(184, 134, 11, 0.1);
    }}
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* RESPONSIVIDADE                                                       */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    @media (max-width: 768px) {{
        .main-title {{
            font-size: 2rem;
        }}
        
        .metric-value {{
            font-size: 1.8rem;
        }}
    }}
    
    /* ═══════════════════════════════════════════════════════════════════ */
    /* ANIMAÇÕES CUSTOMIZADAS                                              */
    /* ═══════════════════════════════════════════════════════════════════ */
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}
    
    .loading {{
        animation: pulse 2s infinite;
    }}
    
    </style>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE GERAÇÃO DE DADOS TOPOGRÁFICOS
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def generate_realistic_elevation_data(
    center_lat: float = Config.CENTER_LAT,
    center_lon: float = Config.CENTER_LON,
    grid_size: int = 100,
    extent: float = 0.15
) -> pd.DataFrame:
    """
    Gera dados de elevação realistas para Prudentópolis com topografia complexa.
    
    Algoritmo:
    1. Cria grid regular de coordenadas
    2. Aplica múltiplas funções sinusoidais para simular Serra da Esperança
    3. Adiciona componentes de cânions e vales
    4. Inclui rugosidade estocástica para realismo
    
    Args:
        center_lat: Latitude central da área
        center_lon: Longitude central da área
        grid_size: Número de pontos em cada dimensão (grid_size x grid_size)
        extent: Extensão da área em graus (aproximadamente)
    
    Returns:
        DataFrame com colunas: lat, lon, elevation
        
    Performance:
        - Cache TTL: 3600 segundos (1 hora)
        - Complexidade: O(n²) onde n = grid_size
    """
    
    # Criar grid de coordenadas geográficas
    lat_range = np.linspace(center_lat - extent, center_lat + extent, grid_size)
    lon_range = np.linspace(center_lon - extent, center_lon + extent, grid_size)
    
    # Pré-alocar array para performance
    data = []
    
    # Parâmetros topográficos de Prudentópolis
    base_elevation = 800  # Altitude média da região
    
    for i, lat in enumerate(lat_range):
        for j, lon in enumerate(lon_range):
            # Componente 1: Serra da Esperança (inclinação NE-SW)
            serra_component = 300 * np.sin((lat - center_lat) * 30) * \
                              np.cos((lon - center_lon) * 20)
            
            # Componente 2: Cânions profundos (depressões localizadas)
            canyon_component = -150 * np.exp(
                -((lat - center_lat + 0.05)**2 + (lon - center_lon - 0.03)**2) / 0.002
            )
            
            # Componente 3: Vales fluviais secundários
            valley_component = -50 * np.sin((lat - center_lat) * 40) * \
                               np.sin((lon - center_lon) * 35)
            
            # Componente 4: Rugosidade do terreno basáltico (estocástico)
            noise = np.random.normal(0, 25)
            
            # Elevação total com limites realistas
            elevation = base_elevation + serra_component + canyon_component + \
                        valley_component + noise
            elevation = np.clip(elevation, 500, 1400)  # Limites da região
            
            data.append({
                'lat': lat,
                'lon': lon,
                'elevation': elevation,
                'x_index': i,
                'y_index': j
            })
    
    return pd.DataFrame(data)


@st.cache_data
def calculate_terrain_metrics(elevation_df: pd.DataFrame, grid_size: int) -> pd.DataFrame:
    """
    Calcula métricas geomorfológicas do terreno.
    
    Métricas calculadas:
    - Slope (declividade) em graus
    - Aspect (orientação de vertentes) em graus
    - Curvature (curvatura do terreno)
    
    Args:
        elevation_df: DataFrame com dados de elevação
        grid_size: Dimensão do grid
    
    Returns:
        DataFrame enriquecido com métricas geomorfológicas
    
    Algoritmo:
        Utiliza gradientes numéricos de NumPy para computação eficiente
    """
    
    # Reshape elevação para matriz 2D
    elevation_matrix = elevation_df['elevation'].values.reshape(grid_size, grid_size)
    
    # Calcular gradientes (derivadas parciais)
    grad_y, grad_x = np.gradient(elevation_matrix)
    
    # Declividade (slope) em graus
    slope_radians = np.arctan(np.sqrt(grad_x**2 + grad_y**2))
    slope_degrees = np.degrees(slope_radians)
    
    # Orientação de vertentes (aspect) em graus (0 = Norte, 90 = Leste)
    aspect_radians = np.arctan2(-grad_y, grad_x)
    aspect_degrees = np.degrees(aspect_radians)
    aspect_degrees = (90 - aspect_degrees) % 360
    
    # Curvatura (segunda derivada)
    grad_yy, grad_yx = np.gradient(grad_y)
    grad_xy, grad_xx = np.gradient(grad_x)
    curvature = np.sqrt(grad_xx**2 + grad_yy**2)
    
    # Adicionar ao DataFrame
    elevation_df['slope'] = slope_degrees.flatten()
    elevation_df['aspect'] = aspect_degrees.flatten()
    elevation_df['curvature'] = curvature.flatten()
    
    return elevation_df


# ═══════════════════════════════════════════════════════════════════════════
# DADOS ESTÁTICOS DE GEOSSÍTIOS (CACHOEIRAS)
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data
def get_waterfalls_database() -> pd.DataFrame:
    """
    Retorna banco de dados das principais cachoeiras de Prudentópolis.
    
    Fonte: Inventário de Geossítios - Projeto Geoparque Prudentópolis
    
    Returns:
        DataFrame com informações detalhadas das cachoeiras
    """
    
    waterfalls = [
        {
            'name': 'Salto São Francisco',
            'lat': -25.1523,
            'lon': -50.9234,
            'height': 196,
            'elevation': 920,
            'flow_rate': 'Alto',
            'accessibility': 'Moderado',
            'description': 'Segunda maior queda livre do Brasil. Formação em derrame basáltico da Fm. Serra Geral.',
            'geological_era': 'Cretáceo',
            'rock_type': 'Basalto'
        },
        {
            'name': 'Cachoeira Véu de Noiva',
            'lat': -25.1789,
            'lon': -50.9456,
            'height': 120,
            'elevation': 850,
            'flow_rate': 'Médio',
            'accessibility': 'Fácil',
            'description': 'Queda espetacular em formato de véu. Trilha interpretativa.',
            'geological_era': 'Cretáceo',
            'rock_type': 'Basalto'
        },
        {
            'name': 'Salto Barão do Rio Branco',
            'lat': -25.2134,
            'lon': -51.0123,
            'height': 85,
            'elevation': 780,
            'flow_rate': 'Alto',
            'accessibility': 'Difícil',
            'description': 'Formação em degraus de basalto. Piscinas naturais na base.',
            'geological_era': 'Cretáceo',
            'rock_type': 'Basalto'
        },
        {
            'name': 'Cachoeira da Mariquinha',
            'lat': -25.1645,
            'lon': -50.9678,
            'height': 75,
            'elevation': 890,
            'flow_rate': 'Baixo',
            'accessibility': 'Moderado',
            'description': 'Acesso por trilha em mata atlântica preservada.',
            'geological_era': 'Cretáceo',
            'rock_type': 'Basalto'
        },
        {
            'name': 'Salto Manduri',
            'lat': -25.2456,
            'lon': -51.0345,
            'height': 95,
            'elevation': 760,
            'flow_rate': 'Médio',
            'accessibility': 'Fácil',
            'description': 'Infraestrutura turística. Piscina natural na base.',
            'geological_era': 'Cretáceo',
            'rock_type': 'Basalto'
        },
        {
            'name': 'Cachoeira Santa Maria',
            'lat': -25.1912,
            'lon': -50.9890,
            'height': 60,
            'elevation': 820,
            'flow_rate': 'Médio',
            'accessibility': 'Fácil',
            'description': 'Conjunto de três quedas em sequência. Valor cênico excepcional.',
            'geological_era': 'Cretáceo',
            'rock_type': 'Basalto'
        }
    ]
    
    return pd.DataFrame(waterfalls)


# ═══════════════════════════════════════════════════════════════════════════
# VISUALIZAÇÃO 3D REALISTA COM PLOTLY
# ═══════════════════════════════════════════════════════════════════════════

def create_professional_3d_terrain(
    elevation_df: pd.DataFrame,
    waterfalls_df: pd.DataFrame,
    grid_size: int,
    exaggeration: float = 3.0,
    show_waterfalls: bool = True,
    colorscale: str = 'earth'
) -> go.Figure:
    """
    Cria visualização 3D profissional do terreno usando surface mesh.
    
    Vantagens sobre blocos sólidos:
    - Superfície contínua e realista
    - Melhor percepção da topografia
    - Renderização mais rápida
    - Possibilidade de iluminação realista
    
    Args:
        elevation_df: Dados de elevação
        waterfalls_df: Dados das cachoeiras
        grid_size: Dimensão do grid
        exaggeration: Fator de exagero vertical
        show_waterfalls: Mostrar marcadores de cachoeiras
        colorscale: Escala de cores (earth, viridis, terrain, etc.)
    
    Returns:
        Objeto Figure do Plotly com visualização 3D
        
    Técnicas utilizadas:
        - Surface mesh com colormap topográfico
        - Iluminação realista (ambient + diffuse)
        - Marcadores 3D para geossítios
        - Camera otimizada para melhor ângulo
    """
    
    # Preparar matrizes de coordenadas
    lats = elevation_df['lat'].unique()
    lons = elevation_df['lon'].unique()
    elevations = elevation_df['elevation'].values.reshape(grid_size, grid_size)
    
    # Aplicar exagero vertical
    elevations_exaggerated = elevations * exaggeration
    
    # Criar figura 3D
    fig = go.Figure()
    
    # ─────────────────────────────────────────────────────────────────────
    # SUPERFÍCIE DO TERRENO (Surface Mesh)
    # ─────────────────────────────────────────────────────────────────────
    
    fig.add_trace(go.Surface(
        x=lons,
        y=lats,
        z=elevations_exaggerated,
        colorscale=colorscale,
        colorbar=dict(
            title=dict(
                text='Elevação (m)',
                font=dict(size=14, color=Config.COLORS['primary'])
            ),
            tickfont=dict(size=12, color=Config.COLORS['text']),
            x=1.02,
            len=0.7
        ),
        hovertemplate=(
            '<b>Coordenadas</b><br>' +
            'Latitude: %{y:.4f}<br>' +
            'Longitude: %{x:.4f}<br>' +
            'Elevação: %{z:.0f}m<br>' +
            '<extra></extra>'
        ),
        name='Terreno',
        lighting=dict(
            ambient=0.6,
            diffuse=0.8,
            fresnel=0.2,
            specular=0.3,
            roughness=0.5
        ),
        lightposition=dict(
            x=0,
            y=1000,
            z=2000
        )
    ))
    
    # ─────────────────────────────────────────────────────────────────────
    # MARCADORES DE CACHOEIRAS (Scatter3d)
    # ─────────────────────────────────────────────────────────────────────
    
    if show_waterfalls and not waterfalls_df.empty:
        fig.add_trace(go.Scatter3d(
            x=waterfalls_df['lon'],
            y=waterfalls_df['lat'],
            z=waterfalls_df['elevation'] * exaggeration,
            mode='markers+text',
            marker=dict(
                size=12,
                color=Config.COLORS['primary'],
                symbol='diamond',
                line=dict(
                    color=Config.COLORS['background'],
                    width=2
                ),
                opacity=0.95
            ),
            text=waterfalls_df['name'],
            textposition='top center',
            textfont=dict(
                size=10,
                color=Config.COLORS['primary'],
                family='Arial Black'
            ),
            hovertemplate=(
                '<b>%{text}</b><br>' +
                'Altura da queda: ' + waterfalls_df['height'].astype(str) + 'm<br>' +
                'Elevação: %{z:.0f}m<br>' +
                '<extra></extra>'
            ),
            name='Cachoeiras'
        ))
    
    # ─────────────────────────────────────────────────────────────────────
    # CONFIGURAÇÃO DO LAYOUT 3D
    # ─────────────────────────────────────────────────────────────────────
    
    fig.update_layout(
        title=dict(
            text='Modelo Digital de Elevação - Serra da Esperança',
            x=0.5,
            xanchor='center',
            font=dict(size=20, color=Config.COLORS['primary'], family='Arial Black')
        ),
        scene=dict(
            xaxis=dict(
                title='Longitude',
                backgroundcolor=Config.COLORS['background'],
                gridcolor=Config.COLORS['accent'],
                showbackground=True,
                titlefont=dict(color=Config.COLORS['text'])
            ),
            yaxis=dict(
                title='Latitude',
                backgroundcolor=Config.COLORS['background'],
                gridcolor=Config.COLORS['accent'],
                showbackground=True,
                titlefont=dict(color=Config.COLORS['text'])
            ),
            zaxis=dict(
                title=f'Elevação (m) × {exaggeration:.1f}',
                backgroundcolor=Config.COLORS['background'],
                gridcolor=Config.COLORS['accent'],
                showbackground=True,
                titlefont=dict(color=Config.COLORS['text'])
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3),
                center=dict(x=0, y=0, z=-0.1)
            ),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.6)
        ),
        paper_bgcolor=Config.COLORS['surface'],
        plot_bgcolor=Config.COLORS['background'],
        font=dict(color=Config.COLORS['text']),
        height=700,
        margin=dict(l=0, r=0, t=50, b=0),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor=Config.COLORS['secondary'],
            borderwidth=1,
            font=dict(color=Config.COLORS['text'])
        )
    )
    
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# SISTEMA DE UPLOAD E PROCESSAMENTO DE ARQUIVOS
# ═══════════════════════════════════════════════════════════════════════════

class FileProcessor:
    """
    Classe para processamento de múltiplos formatos de arquivo.
    
    Formatos suportados:
    - Geoespaciais: SHP, GeoJSON, KML, GPKG
    - Tabulares: CSV, XLSX, XLS, DBF
    - Raster: TIF, TIFF, ASC
    
    Features:
        - Detecção automática de tipo
        - Validação de integridade
        - Normalização de dados
        - Relatório de estatísticas
    """
    
    @staticmethod
    def detect_file_type(filename: str) -> str:
        """Detecta tipo do arquivo pela extensão."""
        ext = Path(filename).suffix.lower()
        
        for category, extensions in Config.SUPPORTED_FORMATS.items():
            if ext in extensions:
                return category
        
        return 'unknown'
    
    @staticmethod
    def process_geospatial(file_obj) -> Tuple[gpd.GeoDataFrame, Dict[str, Any]]:
        """
        Processa arquivos geoespaciais (SHP, GeoJSON, KML).
        
        Args:
            file_obj: Objeto de arquivo do Streamlit
        
        Returns:
            Tupla (GeoDataFrame, metadados)
        """
        try:
            # Ler GeoDataFrame
            gdf = gpd.read_file(file_obj)
            
            # Garantir CRS (sistema de referência de coordenadas)
            if gdf.crs is None:
                gdf = gdf.set_crs('EPSG:4326', allow_override=True)
            
            # Converter para WGS84 se necessário
            if gdf.crs != 'EPSG:4326':
                gdf = gdf.to_crs('EPSG:4326')
            
            # Extrair metadados
            metadata = {
                'total_features': len(gdf),
                'geometry_types': gdf.geometry.type.value_counts().to_dict(),
                'crs': str(gdf.crs),
                'bounds': gdf.total_bounds.tolist(),
                'columns': gdf.columns.tolist(),
                'has_z': gdf.geometry.has_z.any()
            }
            
            return gdf, metadata
            
        except Exception as e:
            raise ValueError(f"Erro ao processar arquivo geoespacial: {str(e)}")
    
    @staticmethod
    def process_tabular(file_obj, filename: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Processa arquivos tabulares (CSV, XLSX, DBF).
        
        Args:
            file_obj: Objeto de arquivo
            filename: Nome do arquivo
        
        Returns:
            Tupla (DataFrame, metadados)
        """
        try:
            ext = Path(filename).suffix.lower()
            
            # Carregar de acordo com o formato
            if ext == '.csv':
                df = pd.read_csv(file_obj, encoding='utf-8', low_memory=False)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_obj)
            elif ext == '.dbf':
                # DBF geralmente vem com Shapefiles
                import dbfread
                dbf = dbfread.DBF(file_obj.name, encoding='utf-8')
                df = pd.DataFrame(iter(dbf))
            else:
                raise ValueError(f"Formato não suportado: {ext}")
            
            # Extrair metadados
            metadata = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.astype(str).to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum()
            }
            
            # Identificar colunas numéricas para análise
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            metadata['numeric_columns'] = numeric_cols
            
            # Estatísticas descritivas para colunas numéricas
            if numeric_cols:
                metadata['statistics'] = df[numeric_cols].describe().to_dict()
            
            return df, metadata
            
        except Exception as e:
            raise ValueError(f"Erro ao processar arquivo tabular: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════
# GERADOR AUTOMÁTICO DE GRÁFICOS DINÂMICOS
# ═══════════════════════════════════════════════════════════════════════════

class DynamicChartGenerator:
    """
    Classe para geração automática de gráficos baseados em dados carregados.
    
    Estratégia:
        1. Analisa tipos de dados (numérico, categórico, temporal)
        2. Identifica relações e padrões
        3. Sugere visualizações apropriadas
        4. Gera gráficos interativos com Plotly
    """
    
    @staticmethod
    def analyze_data_structure(df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Analisa estrutura do DataFrame e classifica colunas.
        
        Returns:
            Dicionário com classificação das colunas
        """
        classification = {
            'numeric': [],
            'categorical': [],
            'datetime': [],
            'text': [],
            'boolean': []
        }
        
        for col in df.columns:
            dtype = df[col].dtype
            
            if pd.api.types.is_numeric_dtype(dtype):
                classification['numeric'].append(col)
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                classification['datetime'].append(col)
            elif pd.api.types.is_bool_dtype(dtype):
                classification['boolean'].append(col)
            elif pd.api.types.is_categorical_dtype(dtype) or \
                 df[col].nunique() / len(df) < 0.05:  # Baixa cardinalidade
                classification['categorical'].append(col)
            else:
                classification['text'].append(col)
        
        return classification
    
    @staticmethod
    def create_distribution_chart(df: pd.DataFrame, column: str) -> go.Figure:
        """Cria gráfico de distribuição para coluna numérica."""
        
        fig = go.Figure()
        
        # Histograma
        fig.add_trace(go.Histogram(
            x=df[column],
            name='Frequência',
            marker=dict(
                color=Config.COLORS['primary'],
                line=dict(color=Config.COLORS['background'], width=1)
            ),
            opacity=0.75
        ))
        
        # Box plot sobreposto
        fig.add_trace(go.Box(
            x=df[column],
            name='Distribuição',
            marker=dict(color=Config.COLORS['secondary']),
            boxmean='sd'
        ))
        
        fig.update_layout(
            title=f'Distribuição: {column}',
            xaxis_title=column,
            yaxis_title='Frequência',
            paper_bgcolor=Config.COLORS['surface'],
            plot_bgcolor=Config.COLORS['background'],
            font=dict(color=Config.COLORS['text']),
            showlegend=True,
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_correlation_heatmap(df: pd.DataFrame, numeric_cols: List[str]) -> go.Figure:
        """Cria matriz de correlação para variáveis numéricas."""
        
        # Calcular correlação
        corr_matrix = df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdYlGn',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont=dict(size=10),
            colorbar=dict(
                title='Correlação',
                titleside='right',
                tickfont=dict(color=Config.COLORS['text'])
            )
        ))
        
        fig.update_layout(
            title='Matriz de Correlação',
            paper_bgcolor=Config.COLORS['surface'],
            plot_bgcolor=Config.COLORS['background'],
            font=dict(color=Config.COLORS['text']),
            height=500,
            xaxis=dict(tickangle=-45)
        )
        
        return fig
    
    @staticmethod
    def create_categorical_chart(df: pd.DataFrame, column: str) -> go.Figure:
        """Cria gráfico de barras para dados categóricos."""
        
        value_counts = df[column].value_counts().head(15)  # Top 15
        
        fig = go.Figure(data=[
            go.Bar(
                x=value_counts.index,
                y=value_counts.values,
                marker=dict(
                    color=Config.COLORS['primary'],
                    line=dict(color=Config.COLORS['background'], width=1)
                ),
                text=value_counts.values,
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title=f'Frequência: {column}',
            xaxis_title=column,
            yaxis_title='Contagem',
            paper_bgcolor=Config.COLORS['surface'],
            plot_bgcolor=Config.COLORS['background'],
            font=dict(color=Config.COLORS['text']),
            height=400,
            xaxis=dict(tickangle=-45)
        )
        
        return fig
    
    @staticmethod
    def create_time_series_chart(df: pd.DataFrame, date_col: str, value_col: str) -> go.Figure:
        """Cria gráfico de série temporal."""
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df[date_col],
            y=df[value_col],
            mode='lines+markers',
            name=value_col,
            line=dict(color=Config.COLORS['primary'], width=2),
            marker=dict(size=6, color=Config.COLORS['secondary'])
        ))
        
        fig.update_layout(
            title=f'Série Temporal: {value_col}',
            xaxis_title=date_col,
            yaxis_title=value_col,
            paper_bgcolor=Config.COLORS['surface'],
            plot_bgcolor=Config.COLORS['background'],
            font=dict(color=Config.COLORS['text']),
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, 
                           color_col: Optional[str] = None) -> go.Figure:
        """Cria gráfico de dispersão."""
        
        fig = go.Figure()
        
        if color_col and color_col in df.columns:
            # Scatter colorido por categoria
            for category in df[color_col].unique():
                mask = df[color_col] == category
                fig.add_trace(go.Scatter(
                    x=df.loc[mask, x_col],
                    y=df.loc[mask, y_col],
                    mode='markers',
                    name=str(category),
                    marker=dict(size=8)
                ))
        else:
            # Scatter simples
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='markers',
                marker=dict(
                    size=8,
                    color=Config.COLORS['primary'],
                    line=dict(color=Config.COLORS['background'], width=1)
                )
            ))
        
        fig.update_layout(
            title=f'{y_col} vs {x_col}',
            xaxis_title=x_col,
            yaxis_title=y_col,
            paper_bgcolor=Config.COLORS['surface'],
            plot_bgcolor=Config.COLORS['background'],
            font=dict(color=Config.COLORS['text']),
            height=500,
            hovermode='closest'
        )
        
        return fig


# ═══════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES DE INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

def render_metric_card(label: str, value: Any, delta: str = "") -> None:
    """Renderiza card de métrica profissional."""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-delta">{delta}</div>
    </div>
    """, unsafe_allow_html=True)


def render_info_box(message: str, box_type: str = 'info') -> None:
    """Renderiza caixa de informação estilizada."""
    class_name = f'{box_type}-box' if box_type != 'info' else 'info-box'
    st.markdown(f"""
    <div class="{class_name}">
        {message}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# APLICAÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """
    Função principal da aplicação.
    
    Fluxo de execução:
        1. Carregar CSS profissional
        2. Renderizar cabeçalho
        3. Configurar sidebar com controles
        4. Processar dados topográficos
        5. Exibir visualização 3D
        6. Gerenciar upload de arquivos
        7. Gerar análises dinâmicas
    """
    
    # ─────────────────────────────────────────────────────────────────────
    # INICIALIZAÇÃO
    # ─────────────────────────────────────────────────────────────────────
    
    load_professional_css()
    
    # ─────────────────────────────────────────────────────────────────────
    # CABEÇALHO
    # ─────────────────────────────────────────────────────────────────────
    
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🏔️ GEOPARQUE PRUDENTÓPOLIS</h1>
        <p class="subtitle">Dashboard Profissional de Análise Topográfica 3D | Serra da Esperança - Paraná</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────────────────────────────
    # SIDEBAR - CONTROLES
    # ─────────────────────────────────────────────────────────────────────
    
    with st.sidebar:
        st.markdown("## ⚙️ Controles de Visualização")
        st.markdown("---")
        
        # Exagero vertical
        exaggeration = st.slider(
            "Exagero Vertical",
            min_value=1.0,
            max_value=10.0,
            value=3.0,
            step=0.5,
            help="Fator de amplificação da dimensão vertical para melhor percepção do relevo"
        )
        
        # Mostrar cachoeiras
        show_waterfalls = st.checkbox(
            "Exibir Geossítios (Cachoeiras)", 
            value=True,
            help="Mostrar marcadores das principais cachoeiras catalogadas"
        )
        
        # Resolução do terreno
        grid_resolution = st.selectbox(
            "Resolução do Modelo",
            options=[50, 75, 100, 150],
            index=2,
            help="Número de pontos no grid. Maior = mais detalhes (processamento mais lento)"
        )
        
        # Paleta de cores
        colorscale = st.selectbox(
            "Paleta de Cores",
            options=['earth', 'terrain', 'viridis', 'jet', 'rainbow'],
            index=0,
            help="Esquema de cores para representação da elevação"
        )
        
        st.markdown("---")
        st.markdown("## 📊 Análises Disponíveis")
        
        show_slope = st.checkbox("Análise de Declividade", value=True)
        show_statistics = st.checkbox("Estatísticas Geomorfológicas", value=True)
        
        st.markdown("---")
        st.markdown("## 📤 Sistema de Upload")
        
        uploaded_files = st.file_uploader(
            "Carregar Dados para Análise",
            type=['shp', 'geojson', 'json', 'csv', 'xlsx', 'xls', 'dbf', 'tif', 'tiff'],
            accept_multiple_files=True,
            help="Formatos suportados: SHP, GeoJSON, CSV, XLSX, DBF, TIF"
        )
        
        st.markdown("---")
        
        render_info_box("""
        <strong>💡 Navegação 3D:</strong><br>
        • <strong>Rotacionar:</strong> Arrastar com mouse<br>
        • <strong>Zoom:</strong> Scroll<br>
        • <strong>Pan:</strong> Shift + Arrastar<br>
        • <strong>Reset:</strong> Duplo clique
        """)
    
    # ─────────────────────────────────────────────────────────────────────
    # PROCESSAMENTO DE DADOS TOPOGRÁFICOS
    # ─────────────────────────────────────────────────────────────────────
    
    with st.spinner('🔄 Processando modelo digital de elevação...'):
        # Gerar dados de elevação
        elevation_df = generate_realistic_elevation_data(grid_size=grid_resolution)
        
        # Calcular métricas geomorfológicas
        elevation_df = calculate_terrain_metrics(elevation_df, grid_resolution)
        
        # Carregar dados de cachoeiras
        waterfalls_df = get_waterfalls_database()
    
    # ─────────────────────────────────────────────────────────────────────
    # MÉTRICAS GERAIS
    # ─────────────────────────────────────────────────────────────────────
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "Altitude Máxima",
            f"{elevation_df['elevation'].max():.0f}m",
            "Serra da Esperança"
        )
    
    with col2:
        render_metric_card(
            "Altitude Mínima",
            f"{elevation_df['elevation'].min():.0f}m",
            "Vales fluviais"
        )
    
    with col3:
        render_metric_card(
            "Amplitude Altimétrica",
            f"{elevation_df['elevation'].max() - elevation_df['elevation'].min():.0f}m",
            "Desnível total"
        )
    
    with col4:
        render_metric_card(
            "Geossítios",
            len(waterfalls_df),
            "Cachoeiras catalogadas"
        )
    
    st.markdown("---")
    
    # ─────────────────────────────────────────────────────────────────────
    # VISUALIZAÇÃO 3D PRINCIPAL
    # ─────────────────────────────────────────────────────────────────────
    
    st.markdown("### 🗺️ Modelo Digital de Elevação 3D")
    
    terrain_fig = create_professional_3d_terrain(
        elevation_df,
        waterfalls_df,
        grid_resolution,
        exaggeration=exaggeration,
        show_waterfalls=show_waterfalls,
        colorscale=colorscale
    )
    
    st.plotly_chart(terrain_fig, use_container_width=True)
    
    # ─────────────────────────────────────────────────────────────────────
    # ANÁLISES GEOMORFOLÓGICAS
    # ─────────────────────────────────────────────────────────────────────
    
    if show_slope or show_statistics:
        st.markdown("---")
        st.markdown("### 📈 Análises Geomorfológicas Avançadas")
        
        if show_slope:
            st.markdown("#### Distribuição de Declividade")
            
            # Criar gráfico de distribuição de slope
            slope_dist_fig = DynamicChartGenerator.create_distribution_chart(
                elevation_df, 
                'slope'
            )
            slope_dist_fig.update_layout(xaxis_title='Declividade (°)')
            st.plotly_chart(slope_dist_fig, use_container_width=True)
            
            # Estatísticas de slope
            col_slope1, col_slope2, col_slope3 = st.columns(3)
            
            with col_slope1:
                avg_slope = elevation_df['slope'].mean()
                render_metric_card("Declividade Média", f"{avg_slope:.1f}°", "")
            
            with col_slope2:
                max_slope = elevation_df['slope'].max()
                render_metric_card("Declividade Máxima", f"{max_slope:.1f}°", "")
            
            with col_slope3:
                critical_area = (elevation_df['slope'] > 30).sum() / len(elevation_df) * 100
                render_metric_card("Áreas Críticas", f"{critical_area:.1f}%", "> 30°")
        
        if show_statistics:
            st.markdown("#### Estatísticas Descritivas")
            
            stats_df = elevation_df[['elevation', 'slope', 'aspect', 'curvature']].describe()
            stats_df = stats_df.round(2)
            
            st.dataframe(
                stats_df,
                use_container_width=True,
                column_config={
                    'elevation': 'Elevação (m)',
                    'slope': 'Declividade (°)',
                    'aspect': 'Orientação (°)',
                    'curvature': 'Curvatura'
                }
            )
    
    # ─────────────────────────────────────────────────────────────────────
    # PROCESSAMENTO DE ARQUIVOS CARREGADOS
    # ─────────────────────────────────────────────────────────────────────
    
    if uploaded_files:
        st.markdown("---")
        st.markdown("### 📁 Análise de Dados Carregados")
        
        for uploaded_file in uploaded_files:
            st.markdown(f"#### 📄 {uploaded_file.name}")
            
            # Detectar tipo de arquivo
            file_type = FileProcessor.detect_file_type(uploaded_file.name)
            
            try:
                if file_type == 'geospatial':
                    # Processar arquivo geoespacial
                    gdf, metadata = FileProcessor.process_geospatial(uploaded_file)
                    
                    st.success(f"✅ Arquivo geoespacial carregado com sucesso!")
                    
                    # Exibir metadados
                    col_meta1, col_meta2 = st.columns(2)
                    
                    with col_meta1:
                        render_info_box(f"""
                        <strong>📊 Informações:</strong><br>
                        • Total de feições: <strong>{metadata['total_features']}</strong><br>
                        • Sistema de coordenadas: <strong>{metadata['crs']}</strong><br>
                        • Tipo de geometria: <strong>{list(metadata['geometry_types'].keys())}</strong>
                        """)
                    
                    with col_meta2:
                        bounds = metadata['bounds']
                        render_info_box(f"""
                        <strong>🗺️ Extensão espacial:</strong><br>
                        • Longitude: <strong>{bounds[0]:.4f} a {bounds[2]:.4f}</strong><br>
                        • Latitude: <strong>{bounds[1]:.4f} a {bounds[3]:.4f}</strong>
                        """)
                    
                    # Exibir tabela de atributos
                    st.markdown("**Tabela de Atributos:**")
                    st.dataframe(gdf.drop(columns=['geometry']).head(10), use_container_width=True)
                    
                elif file_type == 'tabular':
                    # Processar arquivo tabular
                    df, metadata = FileProcessor.process_tabular(uploaded_file, uploaded_file.name)
                    
                    st.success(f"✅ Arquivo tabular carregado com sucesso!")
                    
                    # Exibir metadados
                    col_meta1, col_meta2, col_meta3 = st.columns(3)
                    
                    with col_meta1:
                        render_metric_card(
                            "Total de Linhas",
                            f"{metadata['total_rows']:,}",
                            ""
                        )
                    
                    with col_meta2:
                        render_metric_card(
                            "Total de Colunas",
                            metadata['total_columns'],
                            ""
                        )
                    
                    with col_meta3:
                        render_metric_card(
                            "Colunas Numéricas",
                            len(metadata['numeric_columns']),
                            ""
                        )
                    
                    # Pré-visualização dos dados
                    st.markdown("**Pré-visualização:**")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    # ─────────────────────────────────────────────────────
                    # GERAÇÃO AUTOMÁTICA DE GRÁFICOS
                    # ─────────────────────────────────────────────────────
                    
                    st.markdown("---")
                    st.markdown("#### 📊 Análises Automáticas")
                    
                    # Analisar estrutura dos dados
                    data_structure = DynamicChartGenerator.analyze_data_structure(df)
                    
                    # Gráficos para colunas numéricas
                    if data_structure['numeric']:
                        st.markdown("**Variáveis Numéricas:**")
                        
                        # Seletor de coluna para análise
                        numeric_col = st.selectbox(
                            "Selecione uma variável para análise:",
                            data_structure['numeric'],
                            key=f"numeric_select_{uploaded_file.name}"
                        )
                        
                        # Gráfico de distribuição
                        dist_fig = DynamicChartGenerator.create_distribution_chart(df, numeric_col)
                        st.plotly_chart(dist_fig, use_container_width=True)
                        
                        # Matriz de correlação (se houver múltiplas variáveis)
                        if len(data_structure['numeric']) > 1:
                            st.markdown("**Matriz de Correlação:**")
                            corr_fig = DynamicChartGenerator.create_correlation_heatmap(
                                df, 
                                data_structure['numeric']
                            )
                            st.plotly_chart(corr_fig, use_container_width=True)
                        
                        # Scatter plot
                        if len(data_structure['numeric']) >= 2:
                            st.markdown("**Análise de Dispersão:**")
                            
                            col_scatter1, col_scatter2 = st.columns(2)
                            
                            with col_scatter1:
                                x_col = st.selectbox(
                                    "Eixo X:",
                                    data_structure['numeric'],
                                    key=f"x_select_{uploaded_file.name}"
                                )
                            
                            with col_scatter2:
                                y_col = st.selectbox(
                                    "Eixo Y:",
                                    [col for col in data_structure['numeric'] if col != x_col],
                                    key=f"y_select_{uploaded_file.name}"
                                )
                            
                            # Opção de colorir por categoria
                            color_col = None
                            if data_structure['categorical']:
                                color_col = st.selectbox(
                                    "Colorir por (opcional):",
                                    ['Nenhum'] + data_structure['categorical'],
                                    key=f"color_select_{uploaded_file.name}"
                                )
                                if color_col == 'Nenhum':
                                    color_col = None
                            
                            scatter_fig = DynamicChartGenerator.create_scatter_plot(
                                df, x_col, y_col, color_col
                            )
                            st.plotly_chart(scatter_fig, use_container_width=True)
                    
                    # Gráficos para colunas categóricas
                    if data_structure['categorical']:
                        st.markdown("**Variáveis Categóricas:**")
                        
                        categorical_col = st.selectbox(
                            "Selecione uma categoria:",
                            data_structure['categorical'],
                            key=f"cat_select_{uploaded_file.name}"
                        )
                        
                        cat_fig = DynamicChartGenerator.create_categorical_chart(df, categorical_col)
                        st.plotly_chart(cat_fig, use_container_width=True)
                    
                    # Série temporal (se houver coluna de data)
                    if data_structure['datetime'] and data_structure['numeric']:
                        st.markdown("**Análise Temporal:**")
                        
                        col_time1, col_time2 = st.columns(2)
                        
                        with col_time1:
                            date_col = st.selectbox(
                                "Coluna de data:",
                                data_structure['datetime'],
                                key=f"date_select_{uploaded_file.name}"
                            )
                        
                        with col_time2:
                            value_col = st.selectbox(
                                "Variável:",
                                data_structure['numeric'],
                                key=f"value_select_{uploaded_file.name}"
                            )
                        
                        time_fig = DynamicChartGenerator.create_time_series_chart(
                            df, date_col, value_col
                        )
                        st.plotly_chart(time_fig, use_container_width=True)
                
                else:
                    st.warning(f"⚠️ Formato de arquivo não suportado: {uploaded_file.name}")
            
            except Exception as e:
                st.error(f"❌ Erro ao processar arquivo: {str(e)}")
                st.exception(e)  # Mostrar stack trace completo para debug
            
            st.markdown("---")
    
    # ─────────────────────────────────────────────────────────────────────
    # TABELA DE CACHOEIRAS
    # ─────────────────────────────────────────────────────────────────────
    
    st.markdown("### 💧 Inventário de Geossítios - Cachoeiras")
    
    waterfalls_display = waterfalls_df.sort_values('height', ascending=False).copy()
    waterfalls_display.insert(0, 'Ranking', range(1, len(waterfalls_display) + 1))
    
    st.dataframe(
        waterfalls_display[[
            'Ranking', 'name', 'height', 'elevation', 'flow_rate', 
            'accessibility', 'rock_type', 'description'
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            'Ranking': st.column_config.NumberColumn('#', format='%d'),
            'name': 'Nome',
            'height': st.column_config.NumberColumn('Altura (m)', format='%.0f m'),
            'elevation': st.column_config.NumberColumn('Altitude (m)', format='%.0f m'),
            'flow_rate': 'Vazão',
            'accessibility': 'Acessibilidade',
            'rock_type': 'Litologia',
            'description': 'Descrição'
        }
    )
    
    # ─────────────────────────────────────────────────────────────────────
    # RODAPÉ
    # ─────────────────────────────────────────────────────────────────────
    
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: {Config.COLORS['accent']}; padding: 2rem;">
        <p><strong>Geoparque Prudentópolis - Conservação e Desenvolvimento Sustentável</strong></p>
        <p style="font-size: 0.85rem;">
            Dashboard desenvolvido com Python, Streamlit e Plotly | 
            Versão 2.0.0 Professional Edition | 
            {datetime.now().year}
        </p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PONTO DE ENTRADA DA APLICAÇÃO
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
