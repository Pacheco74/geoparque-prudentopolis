# 🚀 Início Rápido - 5 Minutos

Este guia irá colocá-lo operacional em **menos de 5 minutos**.

---

## ⚡ Opção 1: Modo Demonstração (Dados Sintéticos)

Para testar o dashboard **imediatamente** sem downloads:

```bash
# 1. Instalar dependências básicas
pip install streamlit pandas numpy pydeck plotly geopandas

# 2. Executar dashboard
streamlit run geoparque_dashboard.py
```

**Pronto!** O dashboard abrirá com dados sintéticos de Prudentópolis.

---

## 📥 Opção 2: Com Dados Reais (Recomendado)

### Passo 1: Download de Dados SRTM (3 minutos)

**Método A - Open-Elevation API (Mais fácil)**

Execute o script de exemplo:
```bash
python exemplo_download_dados.py
```

Escolha opção `1` e aguarde. Um arquivo CSV será gerado.

**Método B - Download Manual (Mais qualidade)**

1. Acesse: https://earthexplorer.usgs.gov/
2. Busque por: **Latitude -25.1973, Longitude -50.9780**
3. Dataset: **SRTM 1 Arc-Second Global**
4. Baixe o arquivo `.tif`
5. Coloque em `data/prudentopolis_srtm.tif`

### Passo 2: Configurar Dashboard (1 minuto)

Edite `geoparque_dashboard.py`, linha ~100:

```python
# Substituir:
elevation_df = generate_elevation_data(grid_size=grid_resolution)

# Por (se usou o script):
elevation_df = pd.read_csv('elevation_data_XXXXX.csv')

# Ou (se baixou SRTM manualmente):
from srtm_processor import load_srtm_data
elevation_df = load_srtm_data(
    'data/prudentopolis_srtm.tif',
    bbox=(-51.1, -25.3, -50.9, -25.1)
)
```

### Passo 3: Executar (30 segundos)

```bash
streamlit run geoparque_dashboard.py
```

---

## 🗺️ Opção 3: Com Mapa Mapbox (Melhor Visual)

### Passo 1: Obter Token Gratuito (2 minutos)

1. Crie conta em: https://account.mapbox.com/auth/signup/
2. Copie o "Default public token"

### Passo 2: Configurar (30 segundos)

```bash
# Criar arquivo .env
cp .env.example .env

# Editar .env e colar o token:
MAPBOX_ACCESS_TOKEN=pk.eyJ1Ijoi...
```

### Passo 3: Atualizar Código (1 minuto)

Em `geoparque_dashboard.py`, adicione no início:

```python
import os
from dotenv import load_dotenv

load_dotenv()
MAPBOX_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN')
```

E na função `create_3d_terrain_map`, adicione:

```python
r = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_style='mapbox://styles/mapbox/dark-v10',
    mapbox_key=MAPBOX_TOKEN,  # ← Adicione esta linha
    # ...
)
```

### Passo 4: Executar

```bash
pip install python-dotenv
streamlit run geoparque_dashboard.py
```

---

## 🎯 Primeiros Passos no Dashboard

1. **Barra Lateral:**
   - Ajuste o **Exagero Vertical** para 5.0 (melhor visualização)
   - Ative **Mapa de Declividade**

2. **Mapa 3D:**
   - Arraste para rotacionar
   - Ctrl + Arraste para inclinar (~60°)
   - Clique nas cachoeiras para info

3. **Análise:**
   - Ative **Perfil Altimétrico**
   - Teste coordenadas: 
     - Ponto 1: `-25.15, -50.92`
     - Ponto 2: `-25.25, -51.03`

---

## 🆘 Problemas Comuns

### "ModuleNotFoundError: No module named 'rasterio'"

```bash
# Windows
pip install pipwin
pipwin install rasterio

# macOS/Linux
pip install rasterio
```

### Dashboard não abre

```bash
# Verificar se Streamlit está instalado
streamlit --version

# Reinstalar se necessário
pip install streamlit --upgrade
```

### PyDeck não renderiza

Sem token Mapbox, PyDeck pode não funcionar. Use:

```python
# Em geoparque_dashboard.py, altere:
map_style=None  # ao invés de 'mapbox://...'
```

### Dados muito lentos

Reduza resolução na barra lateral:
- Resolução: **50** (ao invés de 100 ou 150)

---

## 📚 Próximos Passos

- **Guia Completo**: Veja `GUIA_INSTALACAO.md`
- **Documentação Técnica**: Veja `README.md`
- **Exemplos Avançados**: Execute `exemplo_download_dados.py`

---

## 💡 Dicas Pro

### Performance
```python
# Em geoparque_dashboard.py, adicione cache:
@st.cache_data
def load_elevation_data():
    # ... seu código
```

### Personalização
```python
# Mudar cores do tema
# Em load_css(), altere:
'color': '#d4af37'  # Dourado
# Para:
'color': '#00ff00'  # Verde (ou sua preferência)
```

### Upload de Trilhas
1. Prepare shapefile no QGIS
2. Exporte como GeoJSON
3. Upload no dashboard
4. Visualize sobreposto no 3D!

---

**Tempo total estimado:** 5-10 minutos ⏱️

**Divirta-se explorando a geodiversidade de Prudentópolis! 🏔️**
